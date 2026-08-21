import socket
import unittest

from kingsrams.protocol import receive_message, send_message


class ProtocolTests(unittest.TestCase):
    def test_round_trips_length_prefixed_message(self) -> None:
        sender, receiver = socket.socketpair()
        self.addCleanup(sender.close)
        self.addCleanup(receiver.close)

        send_message(sender, "(init T1 KingsRams 1)")

        self.assertEqual(receive_message(receiver), "(init T1 KingsRams 1)")