"""
The Hive  -
An IoT middleware for easy resource sharing across heterogeneous devices.

Contains API for apps running on the Hive.

Author: Fadhil Abubaker
"""

import os
import zmq
import packet

# Supported Hive types
VIDEO = 1
AUDIO = 2

class Hive(object):
    """
    A class container for Hive apps.
    Stores metadata such as app id and status.
    Contains methods to interact with the Hive.
    One instance per app.
    """

    # 32-bit unique id within a device.
    app_id = None
    hive_id = None
    zmqctx = None

    boot_port = None
    boot_sock = None
    comm_port = None
    comm_sock = None

    def __init__(self, port):
        """
        Connects & registers with a Hive Seeker
        at given ipc port.

        All apps register on boot_sock
        then communicate on comm_sock.
        """
        self.app_id = os.getpid()
        self.hive_id = 0
        self.zmqctx = zmq.Context()

        self.boot_port = port
        self.boot_sock = self.zmqctx.socket(zmq.PAIR)
        self.boot_sock.connect(self.boot_port)

        self.comm_port = self.boot_port + str(self.app_id)
        self.comm_sock = self.zmqctx.socket(zmq.PAIR)
        self.comm_sock.connect(self.comm_port)

#        Send a registration packet to Seeker daemon.     
        handle = packet.Packet()
        handle.pack([200, self.hive_id, self.app_id])
        self.boot_sock.send(handle.msg)

        app_id = None
        pack_type = None
        # All apps boot on the same boot_port, hence the while loop.
        while pack_type != 201 and app_id != self.app_id:
            # Expecting a 201 packet confirming registration.
            handle.unpack(self.boot_sock.recv())
            pack_type = handle.contents[0]
            hive_id = handle.contents[1]
            app_id = handle.contents[2]

        self.hive_id = hive_id
        print ">> Sucessfully registered."


# Testing grounds
if __name__ == "__main__":
    h = Hive("ipc:///tmp/seeker")
