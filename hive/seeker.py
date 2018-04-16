"""
The Hive - An IoT middleware for easy resource sharing across heterogeneous devices.

Contains core implementation of a Seeker daemon.

Author: Fadhil Abubaker
"""

import os
import sys
import zmq

import packet

HIVE_ID = 1996

class Seeker(object):
    """
    A Seeker daemon is run on a device that hosts Hive apps.
    Handles comms between apps and the Hive middleware.

    App bootup is handled on $boot_port and
    all remaining app comms are handled on
    $boot_port${app_id}.

    Eg: boot_port : 'ipc:///tmp/seeker'
        comms for app 234 : 'ipc:///tmp/seeker234'
    """

    seeker_id = None

    zmqctx = None
    poller = None
    packeter = None
    boot_port = None

    sockets = []
    app_db = {}

    def __init__(self, seeker_id, port):
        self.seeker_id = seeker_id
        self.boot_port = port

    @staticmethod
    def _detach():
        pid = os.fork()

        if pid > 0:
            sys.exit(0)

        os.setsid()
        os.umask(0)

    def _ipc_boot(self):
        self.zmqctx = zmq.Context()
        boot_sock = self.zmqctx.socket(zmq.PAIR)
        boot_sock.bind(self.boot_port)
        self.sockets.append(boot_sock)

        self.poller = zmq.Poller()
        self.poller.register(boot_sock, zmq.POLLIN)

    def _create_sock(self, port):
        '''
        Creates a socket that binds to given
        port and adds it to poller.
        '''
        sock = self.zmqctx.socket(zmq.PAIR)
        sock.bind(port)
        self.poller.register(sock, zmq.POLLIN)
        self.sockets.append(sock)

    def run(self):
        #self._detach()
        self._ipc_boot()
        packeter = packet.Packet()

        while True:
            active = dict(self.poller.poll())
            for sock in self.sockets:
                if sock in active:
                    packeter.unpack(sock.recv())
                    self._packet_handler(packeter, sock)

    def _packet_handler(self, packeter, sock):
        if packeter.pack_type == 200:
            # Create state for requesting app.
            app_id = packeter.contents[2]
            self.app_db[app_id] = {}

            app_port = self.boot_port + str(app_id)
            self._create_sock(app_port)
            print ">> Registered %s @ %s" % (app_id, app_port)

            # TODO: Implement actual hive_ids.
            # Send 201 registration confirmation.
            packeter.pack([201, HIVE_ID, app_id])
            sock.send(packeter.msg)

# Testing grounds
if __name__ == "__main__":
    s = Seeker(1, "ipc:///tmp/seeker")
    s.run()
