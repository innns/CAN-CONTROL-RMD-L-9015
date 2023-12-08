import CanControlRMD
import math
import time
import MyUDPServer
from tqdm import trange
from tqdm import tqdm

MOTOR = [i for i in range(10)]


def D2R(x):
    return x * math.pi / 180.0


def R2D(x):
    return x * 180.0 / math.pi


PI1 = [0x7F, 0x4F, 0x80, 0x01, 0x60, 0x00]
PI2 = [0x7F, 0x4F, 0x80, 0x01, 0x60, 0x00]
PI3 = [150, 50, 90, 1, 220, 0]

if __name__ == "__main__":
    CAN = CanControlRMD.CanControlRMD()
    # UDP socket
    UDP = MyUDPServer.MyUDPServer("127.0.0.1", 5000)
    # UDP.listen_threading()

    print("\nSTARTING CAN UDP")
    for tt in trange(50):
        time.sleep(0.1)

    CAN.recv_can_threading()
    print("\nSTARTING CAN LISTEN THREADING")
    for tt in trange(10):
        time.sleep(0.1)

    print("\nSETTING INIT PID PARAS")

    CAN.set_PID(1, PI1[0], PI1[1], PI1[2], PI1[3], PI1[4], PI1[5], False)
    time.sleep(0.33)

    CAN.set_PID(2, PI2[0], PI2[1], PI2[2], PI2[3], PI2[4], PI2[5], False)
    time.sleep(0.33)

    CAN.set_PID(3, PI3[0], PI3[1], PI3[2], PI3[3], PI3[4], PI3[5], False)
    time.sleep(0.33)

    print("\nRESETTING ZERO POINT")

    offset = [0, 0, 0, 0]
    for i in range(1, 4):
        # 3个电机
        for j in range(3):
            # 重试三次
            CAN.read_multi_angel(i)
            time.sleep(0.01)
            msg = CAN.get_msg()
            print("{} WANT{} MSG MOTOR{} ANGLE{}".format("#" * i + "_" * (3 - i), i, msg.motor_id, msg.single_angle))
            time.sleep(0.01)
            if msg.motor_id == i:
                offset[i] = round(msg.single_angle / 360.0) * 360
                CAN.multi_angle_control(i, 0x05, int(100 * offset[i]))
                break

    print("MOTOR OFFSET{}\n".format(offset[1:]))

    print("#" * 5 + " INIT DONE " + "#" * 5)
    while 1:
        json_data = UDP.listen_once()
        # UDP.clear_json_data()
        if "cmd" in json_data.keys():
            cmd = json_data["cmd"]
            if cmd == "close_ALL":
                print("ABOUT TO CLOSE")
                time.sleep(5)
                UDP.close()
                CAN.close()
                break
            elif cmd == "angle":
                if json_data["id"] == 1:
                    CAN.multi_angle_control(json_data["id"], 0x05,
                                            int(100 * (float(json_data["angle"]) + offset[json_data["id"]])))
                else:
                    CAN.multi_angle_control(json_data["id"], 0x05,
                                            int(100 * (-1 * float(json_data["angle"]) + offset[json_data["id"]])))
                print("id{} angle{} off{}".format(json_data["id"], json_data["angle"], offset[json_data["id"]]))
            elif cmd == "motion":
                # CAN.motion_control(json_data["id"], json_data["p_des"], json_data["v_des"], 3, 0.2, 0)
                print("id{} p_des{} v_des{}".format(json_data["id"], json_data["p_des"], json_data["v_des"]))
            elif cmd == "set_PID":
                print("id{0} {1} {2} {3} {4} {5} {6} {7}}".format(json_data["id"],
                                                                  json_data["cp"], json_data["ci"],
                                                                  json_data["sp"], json_data["si"],
                                                                  json_data["pp"], json_data["pi"],
                                                                  json_data["save"]))
            elif cmd == "close_motor":
                print("CLOSE")
                # CAN.close_motor(json_data["id"])
            elif cmd == "read":
                print("READ")
            elif cmd == "clear":
                print("CLEAR")
                UDP.clear_json_data()
                UDP.clear_json_data()
                time.sleep(3)
                UDP.clear_json_data()
                # CAN.read_multi_angel(json_data["id"])
                # CAN.process_recv_can()
                # msg = CAN.get_msg()
                # if msg is not None:
                #     send_data = {"id": msg.motor_id, "angel": msg.angel}
                #     UDP.send_json_data(send_data)
                #     print("SEND: ", send_data)
            print(json_data)
        else:
            pass
