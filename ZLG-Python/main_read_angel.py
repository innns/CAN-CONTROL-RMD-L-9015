import tqdm.notebook

import CanControlRMD
import math
import time
from tqdm import trange
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np

MOTOR = [i for i in range(10)]


def D2R(x):
    return x * math.pi / 180.0


def R2D(x):
    return x * 180.0 / math.pi


def calc_sin(amp, phase, sample_hz, sample_id):
    return amp * math.sin(2 * math.pi / sample_hz * sample_id + phase)


def calc_cos(amp, phase, sample_hz, sample_id):
    return amp * math.cos(2 * math.pi / sample_hz * sample_id + phase)


if __name__ == '__main__':
    CAN = CanControlRMD.CanControlRMD()
    CAN.recv_can_threading()
    time.sleep(3)
    CAN.close_motor(MOTOR[3])
    # CAN.set_PID(MOTOR[3], 0xff, 0x00, 0xff, 0x00, 0x05, 0x0, False)
    time.sleep(3)
    # CAN.init_motor_motion_single(MOTOR[3], 52.7)
    # time.sleep(2)
    # CAN.init_motor_motion_single(MOTOR[3], 0)
    # time.sleep(2)


    # x = [0]
    # y = [0]
    # plt.ion()


    while True:
        CAN.set_PID(MOTOR[3], 0x30, 0x0A, 0x30, 0x0, 0x4A, 0x00, False)
        CAN.multi_angle_control(MOTOR[3], 0x0A, 0)
        start_time = time.time()
        # for i in range((HZ * ALL_TIME)):
        HZ = 50
        ALL_TIME = 20
        i = 0
        for i in trange(HZ * ALL_TIME):
            i += 1
            CAN.read_multi_angel(MOTOR[3])
            msg = CAN.get_msg()
            # for data in msg.can_data:
            #     print("0x{:02X} ".format(data), end="")
            # print()
            print("MAINLOOP: {}".format(msg.single_angle), end='\n')
            # tqdm.write("\nMAINLOOP: {}".format(msg.single_angle), end='')


            # t = (time.time() - start_time)
            # if (len(x) > 100):
            #     x = x[1:]
            #     y = y[1:]
            # x.append(t)
            # y.append(msg.single_angle)
            # plt.clf()  # 清除之前画的图
            # plt.plot(x, y)
            # plt.pause(0.001)

            diff = 1 / HZ * i - (time.time() - start_time)
            if (diff > 0):
                time.sleep(diff)
        print("\nALL COST TIME = {:.2f} s".format(time.time() - start_time))
        # print("Can control start")
        # time.sleep(5)
        # print("Can control end")
