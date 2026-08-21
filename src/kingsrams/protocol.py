"""RCSSServerMJ length-prefixed TCP protocol helpers."""

import socket


LENGTH_PREFIX_SIZE = 4


def send_message(connection: socket.socket, message: str) -> None:
    payload = message.encode()
    connection.sendall(len(payload).to_bytes(LENGTH_PREFIX_SIZE, byteorder="big") + payload)


def receive_message(connection: socket.socket) -> str:
    size = int.from_bytes(_receive_exactly(connection, LENGTH_PREFIX_SIZE), byteorder="big")
    return _receive_exactly(connection, size).decode()


def _receive_exactly(connection: socket.socket, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        chunk = connection.recv(size - len(chunks))
        if not chunk:
            raise ConnectionResetError("simulation server closed the connection")
        chunks.extend(chunk)
    return bytes(chunks)