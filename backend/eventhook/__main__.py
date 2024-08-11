import logging
import socket

import zmq

import shared.config as config
from shared.process.killer import ProcessKiller

logging.basicConfig(level=config.event.LOGLEVEL)


def main():
    killer = ProcessKiller()

    zmq_ctx = zmq.Context()
    zmq_queue = zmq_ctx.socket(zmq.DEALER)  # pylint: disable=no-member
    zmq_queue.connect(f"tcp://eventpersister:{config.event.PERSISTER_PORT}")

    udp_listener = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    udp_listener.bind((config.event.APPLICATION_HOST, config.event.APPLICATION_PORT))
    udp_listener.settimeout(config.event.SOCKET_TIMEOUT)

    logging.info(
        "Event server running at %s:%s",
        config.event.APPLICATION_HOST,
        config.event.APPLICATION_PORT,
    )

    while not killer.die:
        try:
            msg = udp_listener.recv(config.event.BUFFER_SIZE)
            zmq_queue.send(msg)
        except socket.timeout:
            pass


if __name__ == "__main__":
    main()
