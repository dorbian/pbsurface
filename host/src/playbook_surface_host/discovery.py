"""Bounded UDP discovery responder for local PlayBook clients."""

from __future__ import annotations

import json
import socket
import threading

from .model import DISCOVERY_REQUEST, DEFAULT_DISCOVERY_PORT, Endpoint


MAX_DATAGRAM = 4096


def response_for(message: bytes, endpoint: Endpoint) -> bytes | None:
    if message.strip() != DISCOVERY_REQUEST:
        return None
    encoded = json.dumps(endpoint.discovery_payload(), separators=(",", ":"), sort_keys=True).encode("utf-8")
    if len(encoded) > MAX_DATAGRAM:
        raise ValueError("discovery response exceeds maximum datagram size")
    return encoded


class DiscoveryResponder:
    def __init__(self, endpoint: Endpoint, bind_address: str = "0.0.0.0", port: int = DEFAULT_DISCOVERY_PORT) -> None:
        self.endpoint = endpoint
        self.bind_address = bind_address
        self.port = port
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._socket: socket.socket | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.bind_address, self.port))
        sock.settimeout(0.5)
        self._socket = sock
        self._thread = threading.Thread(target=self._run, name="playbook-discovery", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
        if self._socket:
            self._socket.close()
        self._thread = None
        self._socket = None

    def _run(self) -> None:
        assert self._socket is not None
        while not self._stop.is_set():
            try:
                message, sender = self._socket.recvfrom(MAX_DATAGRAM)
            except socket.timeout:
                continue
            except OSError:
                return
            response = response_for(message, self.endpoint)
            if response is not None:
                self._socket.sendto(response, sender)

