import CanControlRMD
import math
import time
import MyUDPServer
from tqdm import trange
from tqdm import tqdm
import json

# TODO: motion 模式下的位置最大只能-12.5 到 12.5 rad, 跳变+-720时候就会出大问题！


MOTOR = [i for i in range(10)]


def D2R(x):
    return x * math.pi / 180.0


def R2D(x):
    return x * 180.0 / math.pi


def AMP_LIMIT(x, low, up):
    return low if (x < low) else (up if (x > up) else x)


NOTE = (
    "pi does not work; kp,kd is the default PD controller para, index means motor id, DONT EDIT; DIRECTION means motor spin direction")
pi = [0x6F, 0x4F, 0x80, 0x20, 0x30, 0x00]
kp = [2.0, 6, 6, 6]
kd = [0.10, 0.18, 0.18, 0.18]
DIRECTION = [0, 1, -1, -1]  # 电机转动方向 由安装位置、操作要求决定
software_zero = [180, 168.5, 191.7, 110]
AMP_LOW = [0, -30, -30, -60]
AMP_UP = [0, 30, 30, 30]
IP = "127.0.0.1"
PORT = 5000

names = ['NOTE', 'pi', 'kp', 'kd', 'DIRECTION', 'software_zero', 'AMP_LOW', 'AMP_UP', 'IP', 'PORT']
para_dict = dict(zip(names, [NOTE, pi, kp, kd, DIRECTION, software_zero, AMP_LOW, AMP_UP, IP, PORT]))

if __name__ == "__main__":
    UDP = MyUDPServer.MyUDPServer(IP, PORT)

    CAN = CanControlRMD.CanControlRMD()

    # READ PARAMETERS
    with open("control_para.json", "r") as f:
        data_raw = f.read()
        print(data_raw)
        data = json.loads(data_raw)
        if all(key in data for key in names):
            print("USING JSON PARA")
            pi = data['pi']
            kp = data['kp']
            kd = data['kd']
            DIRECTION = data['DIRECTION']
            software_zero = data['software_zero']
            AMP_LOW = data['AMP_LOW']
            AMP_UP = data['AMP_UP']
            IP = data['IP']
            PORT = data['PORT']
        else:
            print("NO PARA FILE DEFAULT PARA")
            print(para_dict)
            time.sleep(20)
            raise Exception("NO JSON FILE")

    # UDP.listen_threading()
    # 创建一个can 监听线程并启动
    print("\nSTARTING CAN")
    for i in trange(40):
        time.sleep(0.1)

    CAN.recv_can_threading()
    print("\nSTARTING CAN LISTEN THREADING")
    for i in trange(20):
        time.sleep(0.1)

    for i in range(1, 4):
        if (software_zero[i] + AMP_LOW[i] < 0 or software_zero[i] + AMP_LOW[i] > 360):
            raise AssertionError("软件零位在360 / 0 度附近 非常危险！")
    # print("\nSETTING INIT PID PARAS")

    # for i in trange(1, 4):
    #     CAN.set_PID(i, pi[0], pi[1], pi[2], pi[3], pi[4], pi[5], False)
    #     time.sleep(0.4)

    # print("\nRESETTING ZERO POINT")
    #
    # offset = [0, 0, 0, 0]
    # for i in range(1, 4):
    #     # 3个电机
    #     for j in range(3):
    #         # 重试三次
    #         CAN.read_multi_angel(i)
    #         time.sleep(0.01)
    #         msg = CAN.get_msg()
    #         print("{} WANT_{} MOTOR_{} ANGLE_{}".format("#" * i + "_" * (3 - i), i, msg.motor_id, msg.single_angle))
    #         time.sleep(0.01)
    #         if msg.motor_id == i:
    #             offset[i] = round(msg.single_angle / 360.0) * 360
    #             # CAN.multi_angle_control(i, 0x05, offset[i])
    #             if abs(offset[i]) > 360:
    #                 print("ERROR! PLZ RESET ZERO")
    #                 time.sleep(5)
    #                 raise AssertionError("电机角度超过正负360度范围")
    #             print("Motion {} = {} rad".format(MOTOR[i], D2R(offset[i])))
    #             CAN.motion_control(MOTOR[i],
    #                                D2R(offset[i]),
    #                                0.2,
    #                                kp[i],
    #                                kd[i],
    #                                0)
    #             break

    for i in range(1, 4):
        # 3个电机
        for j in range(3):
            # 重试三次
            CAN.read_multi_angel(i)
            time.sleep(0.01)
            msg = CAN.get_msg()
            print("{} WANT_{} MOTOR_{} ANGLE_{}".format("#" * i + "_" * (3 - i), i, msg.motor_id, msg.single_angle))
            time.sleep(0.01)
            if msg.motor_id == i:
                # CAN.multi_angle_control(i, 0x05, offset[i])
                angle_ = msg.single_angle
                id_ = msg.motor_id
                print("Motion {} ZERO {}".format(MOTOR[i], software_zero[i]))
                # if (angle_ != AMP_LIMIT(angle_, software_zero[i] + AMP_LOW[id_], software_zero[i] + AMP_UP[id_])
                #         and angle_ != AMP_LIMIT(angle_, 0, software_zero[i] + AMP_UP[id_] - 360)
                #         and angle_ != AMP_LIMIT(angle_, software_zero[i] + AMP_LOW[id_] + 360, 360)):
                if angle_ != AMP_LIMIT(angle_, software_zero[i] + AMP_LOW[id_] - 10,
                                       software_zero[i] + AMP_UP[id_] + 10):
                    print("ERROR! PLZ RESET ZERO")
                    time.sleep(5)
                    raise AssertionError("电机角度超过正负范围 请调试零点！")
                CAN.motion_control(MOTOR[i],
                                   D2R(software_zero[i]),
                                   0.2,
                                   1.5,
                                   0.05,
                                   0)
                break
    print("等待电机回到零位")
    for i in trange(20):
        time.sleep(0.1)
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
                id_ = json_data["id"]
                tar_angle = AMP_LIMIT(software_zero[id_] + DIRECTION[id_] * json_data["angle"],
                                      software_zero[id_] + AMP_LOW[id_],
                                      software_zero[id_] + AMP_UP[id_])
                print("M{} ORIGIN {} WANT {}".format(json_data["id"],
                                                     (software_zero[id_] + DIRECTION[id_] * json_data["angle"]),
                                                     tar_angle))
                CAN.motion_control(json_data["id"],
                                   D2R(tar_angle),
                                   0.2,
                                   kp[json_data["id"]],
                                   kd[json_data["id"]],
                                   0)
                # if json_data["id"] == 1:
                #     CAN.multi_angle_control(json_data["id"], 0x05,
                #                             int(100 * (json_data["angle"] + offset[json_data["id"]])))
                # else:
                #     CAN.multi_angle_control(json_data["id"], 0x05,
                #                             int(-100 * (json_data["angle"] + offset[json_data["id"]])))
                # print("id{} max_spd{} angle{}".format(json_data["id"], 0x05, json_data["angle"]))

            elif cmd == "motion":
                # CAN.motion_control(json_data["id"], json_data["p_des"], json_data["v_des"], 3, 0.2, 0)
                print("id{} p_des{} v_des{}".format(json_data["id"], json_data["p_des"], json_data["v_des"]))

            elif cmd == "set_PID":
                print("id{0} {1} {2} {3} {4} {5} {6} {7}}".format(json_data["id"],
                                                                  json_data["cp"], json_data["ci"],
                                                                  json_data["sp"], json_data["si"],
                                                                  json_data["pp"], json_data["pi"],
                                                                  json_data["save"]))
            elif cmd == "set_zero":
                UDP.clear_json_data()
                for i in range(1, 4):
                    # 3个电机
                    CAN.motion_control(MOTOR[i],
                                       D2R(software_zero[i]),
                                       0.2,
                                       1.5,
                                       0.05,
                                       0)
                UDP.clear_json_data()
                UDP.send_json_data({"cmd": "set_zero_done"})
            elif cmd == "close_motors":
                print("CLOSE ALL_MOTORS")
                UDP.clear_json_data()
                CAN.close_motor(1)
                CAN.close_motor(2)
                CAN.close_motor(3)
                time.sleep(0.1)
                UDP.clear_json_data()
                # CAN.close_motor(json_data["id"])
                UDP.send_json_data({"cmd": "close_motors"})
            elif cmd == "read":
                z_s = software_zero.copy()
                for i in range(1, 4):
                    CAN.motion_control(MOTOR[i],
                                       D2R(software_zero[i]),
                                       0.2,
                                       1.5,
                                       0.05,
                                       0)
                for i in range(1, 4):
                    # 3个电机
                    for j in range(3):
                        # 重试三次
                        CAN.read_multi_angel(i)
                        time.sleep(0.01)
                        msg = CAN.get_msg()
                        if msg.motor_id == i:
                            z_s[i] = DIRECTION[i] * (msg.single_angle[i] - software_zero[i])
                            UDP.send_angle_json(i, z_s[i])
                            print("MOTOR {} \t ANGLE {:.2f}".format(i, z_s[i]))
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
