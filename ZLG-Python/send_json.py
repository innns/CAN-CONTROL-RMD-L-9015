# import CanControlRMD
import math
import time
import MyUDPServer

MOTOR = [i for i in range(10)]


def D2R(x):
    return x * math.pi / 180.0


def R2D(x):
    return x * 180.0 / math.pi


if __name__ == "__main__":
    # CAN = CanControlRMD.CanControlRMD()

    # UDP socket
    UDP = MyUDPServer.MyUDPServer("127.0.0.1", 6000)
    for i in range(10):
        UDP.send_json_data({"cmd": "angle", "id": 1, "angle": "{}".format(i * 10)}, 5000)
        time.sleep(0.01)
    UDP.send_json_data({"cmd": "clear"})
