import can
import time
import random

def generate_random_data_vcell():
    return ["0x" + format(random.randint(174, 176), '02X') for _ in range(8)]
   
def generate_random_data_tcell():
    return ["0x" + format(random.randint(138, 139), '02X') for _ in range(8)]

def generate_random_data_diagnostic():
    return ["0x" + format(random.randint(0, 255), '02X') for _ in range(8)]

with can.Bus(interface='socketcan', channel='vcan0', receive_own_messages=True) as bus:
    try:
        while True:
            #bms diagnostic
            data = generate_random_data_diagnostic()
            data_bytes = [int(x, 16) for x in data]  # Converter para bytes
            msg = can.Message(arbitration_id=0x19B50007, is_extended_id=True, data=data_bytes)
            bus.send(msg)            

            #vcell
            data = generate_random_data_tcell()
            data_bytes = [int(x, 16) for x in data]  # Converter para bytes
            msg = can.Message(arbitration_id=0x19B50100, is_extended_id=True, data=data_bytes)
            bus.send(msg)
            data = generate_random_data_tcell()
            data_bytes = [int(x, 16) for x in data]  # Converter para bytes
            msg = can.Message(arbitration_id=0x19B50101, is_extended_id=True, data=data_bytes)
            bus.send(msg)
            data = generate_random_data_tcell()
            data_bytes = [int(x, 16) for x in data]  # Converter para bytes
            msg = can.Message(arbitration_id=0x19B50102, is_extended_id=True, data=data_bytes)
            bus.send(msg)
            data = generate_random_data_tcell()
            data_bytes = [int(x, 16) for x in data]  # Converter para bytes
            msg = can.Message(arbitration_id=0x19B50103, is_extended_id=True, data=data_bytes)
            bus.send(msg)
            data = generate_random_data_tcell()
            data_bytes = [int(x, 16) for x in data]  # Converter para bytes
            msg = can.Message(arbitration_id=0x19B50104, is_extended_id=True, data=data_bytes)
            bus.send(msg)
            data = generate_random_data_tcell()
            data_bytes = [int(x, 16) for x in data]  # Converter para bytes
            msg = can.Message(arbitration_id=0x19B50105, is_extended_id=True, data=data_bytes)
            bus.send(msg)
            data = generate_random_data_tcell()
            data_bytes = [int(x, 16) for x in data]  # Converter para bytes
            msg = can.Message(arbitration_id=0x19B50106, is_extended_id=True, data=data_bytes)
            bus.send(msg)
            data = generate_random_data_tcell()
            data_bytes = [int(x, 16) for x in data]  # Converter para bytes
            msg = can.Message(arbitration_id=0x19B50107, is_extended_id=True, data=data_bytes)
            bus.send(msg)
            data = generate_random_data_tcell()
            data_bytes = [int(x, 16) for x in data]  # Converter para bytes
            msg = can.Message(arbitration_id=0x19B50108, is_extended_id=True, data=data_bytes)
            bus.send(msg)
            
            #tcell
            data = generate_random_data_tcell()
            data_bytes = [int(x, 16) for x in data]  # Converter para bytes
            msg = can.Message(arbitration_id=0x19B50800, is_extended_id=True, data=data_bytes)
            bus.send(msg)
            data = generate_random_data_tcell()
            data_bytes = [int(x, 16) for x in data]  # Converter para bytes
            msg = can.Message(arbitration_id=0x19B50801, is_extended_id=True, data=data_bytes)
            bus.send(msg)
            data = generate_random_data_tcell()
            data_bytes = [int(x, 16) for x in data]  # Converter para bytes
            msg = can.Message(arbitration_id=0x19B50802, is_extended_id=True, data=data_bytes)
            bus.send(msg)
            data = generate_random_data_tcell()
            data_bytes = [int(x, 16) for x in data]  # Converter para bytes
            msg = can.Message(arbitration_id=0x19B50803, is_extended_id=True, data=data_bytes)
            bus.send(msg)
            data = generate_random_data_tcell()
            data_bytes = [int(x, 16) for x in data]  # Converter para bytes
            msg = can.Message(arbitration_id=0x19B50804, is_extended_id=True, data=data_bytes)
            bus.send(msg)
            data = generate_random_data_tcell()
            data_bytes = [int(x, 16) for x in data]  # Converter para bytes
            msg = can.Message(arbitration_id=0x00000103, is_extended_id=True, data=data_bytes)
            bus.send(msg)
            print(f"Message sent on {bus.channel_info}")
            # Ajuste o intervalo de envio aqui (por exemplo, aguardar 1 segundo)

            time.sleep(0.5)
            
    except can.CanError:
        print("Message NOT sent")
    except KeyboardInterrupt:
    	bus.shutdown()



