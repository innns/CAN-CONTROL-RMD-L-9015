import tqdm.notebook

import CanControlRMD
import math
import time
from tqdm import trange
from tqdm import tqdm

MOTOR = [i for i in range(10)]


def D2R(x):
    return x * math.pi / 180.0


def R2D(x):
    return x * 180.0 / math.pi


def calc_sin(amp, phase, sample_hz, sample_id):
    return amp * math.sin(2 * math.pi / sample_hz * sample_id + phase)


def calc_cos(amp, phase, sample_hz, sample_id):
    return amp * math.cos(2 * math.pi / sample_hz * sample_id + phase)


# if __name__ == '__main__':
#     CAN = CanControlRMD.CanControlRMD()
#     CAN.recv_can_threading()
#     HZ = 500
#     ALL_TIME = 10
#     time.sleep(1)
#     CAN.close_motor(MOTOR[2])
#     time.sleep(2)
#     CAN.motion_control(MOTOR[2],
#                        0,
#                        0,
#                        2,
#                        0.1,
#                        0)
#     time.sleep(1)
#     # CAN.init_motor_motion_single(MOTOR[3], 52.7)
#     # time.sleep(2)
#     # CAN.init_motor_motion_single(MOTOR[3], 0)
#     # time.sleep(2)
#     while True:
#         for i in range(HZ):
#             CAN.motion_control(MOTOR[2],
#                                0,
#                                0,
#                                2,
#                                0.1,
#                                0)
#             time.sleep(0.1)
#
#         print("Can control start")
#         CAN.motion_control(MOTOR[2],
#                            0,
#                            0.002,
#                            2,
#                            0.1,
#                            0)
#         time.sleep(5)
#         print("Can control end")
if __name__ == '__main__':
    CAN = CanControlRMD.CanControlRMD()
    CAN.recv_can_threading()
    HZ = 100
    ALL_TIME = 10
    time.sleep(3)
    CAN.close_motor(MOTOR[3])
    # CAN.set_PID(MOTOR[3], 0xff, 0x00, 0xff, 0x00, 0x05, 0x0, False)
    time.sleep(3)
    # CAN.init_motor_motion_single(MOTOR[3], 52.7)
    # time.sleep(2)
    # CAN.init_motor_motion_single(MOTOR[3], 0)
    # time.sleep(2)
    while True:
        CAN.set_PID(MOTOR[3], 0x30, 0x0A, 0x30, 0x0, 0x4A, 0x00, False)
        CAN.multi_angle_control(MOTOR[3], 0x05, 0)
        start_time = time.time()
        for i in range((HZ * ALL_TIME)):
            CAN.read_multi_angel(MOTOR[3])
            msg = CAN.get_msg()
            # for data in msg.can_data:
            #     print("0x{:02X} ".format(data), end="")
            # print()
            print("\rMAINLOOP: {}".format(msg.single_angle), end='')
            # tqdm.write("\nMAINLOOP: {}".format(msg.single_angle), end='')
            diff = 1 / HZ * (i + 1) - (time.time() - start_time)
            if (diff > 0):
                time.sleep(diff)
        print("\nALL COST TIME = {:.2f} s".format(time.time() - start_time))
        # print("Can control start")
        # time.sleep(5)
        # print("Can control end")
