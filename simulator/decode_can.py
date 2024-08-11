import json
import time
import logging
import can
import socket

UDP_IP = "localhost"
UDP_PORT = 9512

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def gen_decode_func(min_val: float, mul_val: float):
    def func(value: int) -> float:
        return value / mul_val + min_val

    return func


def gen_decode_funcs() -> dict:
    with open("decode.json", "r") as file:
        decode_json = json.loads(file.read())

    funcs = {}

    for identifier, blocks in decode_json.items():
        temp = {}

        for name, block in blocks.items():
            func = gen_decode_func(block["min"], block["mul"])
            temp[name] = {
                "func": func,
                "ini": block["ini"],
                "fin": block["fin"],
            }

        funcs[identifier] = temp

    return funcs


def decode(message_id: str, payload: str, funcs: dict) -> list:
    decoded = []
    

    now = int(time.time_ns() // 1000000)
        
    if message_id in funcs:
        for name, params in funcs[message_id].items():
            value = int((payload[params["ini"]:params["fin"]][::-1]), 2)

            decoded.append(
                {
                    "namespace": name,
                    "time": now,
                    "fields": {"value": params["func"](value)},
                }
            )

    return decoded


def send_UDP(funcs: dict):
    print("Waiting")
    bus = can.Bus(interface='socketcan')
    
    while True:
        msg = bus.recv()
        message_id = "0x" + str(hex(msg.arbitration_id))[2:].upper().zfill(8)
        payload = bin(int(msg.data.hex(), 16))[2:].zfill(64)[::-1]

        decoded = decode(message_id, payload, funcs)

        for j in range(0, len(decoded)):
            server.sendto(json.dumps(decoded[j]).encode("utf-8"), (UDP_IP, UDP_PORT))

        print(decoded)
        #logging.basicConfig(filename="Log_CAN.log", level=logging.INFO, format="%(asctime)s %(message)s")
        #logging.info(decoded)


def main():
    funcs = gen_decode_funcs()
    send_UDP(funcs)


if __name__ == "__main__":
    main()

