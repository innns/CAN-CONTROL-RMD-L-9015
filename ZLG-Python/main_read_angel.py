import tqdm.notebook

import CanControlRMD
import math
import time
from tqdm import trange
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import collections

MOTOR = [i for i in range(10)]


def D2R(x):
    return x * math.pi / 180.0


def R2D(x):
    return x * 180.0 / math.pi


def calc_sin(amp, phase, sample_hz, sample_id):
    return amp * math.sin(2 * math.pi / sample_hz * sample_id + phase)


def calc_cos(amp, phase, sample_hz, sample_id):
    return amp * math.cos(2 * math.pi / sample_hz * sample_id + phase)


pi = [0x60, 0x10, 0x30, 0x00, 0x60, 0x00]

if __name__ == '__main__':
    CAN = CanControlRMD.CanControlRMD()

    print("\nSTARTING CAN")
    for i in trange(30):
        time.sleep(0.1)

    CAN.recv_can_threading()
    print("\nSTARTING CAN LISTEN THREADING")
    for i in trange(10):
        time.sleep(0.1)

    print("\nSETTING INIT PID PARAS")

    for i in trange(1, 4):
        CAN.set_PID(i, pi[0], pi[1], pi[2], pi[3], pi[4], pi[5], False)
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

    show_queue = collections.deque(maxlen=50)
    time_queue = collections.deque(maxlen=50)

    plt.ion()
    while True:
        # CAN.set_PID(MOTOR[3], 0x60, 0x10, 0x30, 0x0, 0x60, 0x00, False)
        CAN.multi_angle_control(MOTOR[3], 0x05, 0)
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
            show_queue.append(-1 * msg.single_angle)
            time_queue.append(time.time() - start_time)
            plt.clf()  # 清除之前画的图
            plt.plot(time_queue, show_queue)
            plt.ylim((-90, 90))
            plt.pause(0.001)

            diff = 1 / HZ * i - (time.time() - start_time)
            if (diff > 0):
                time.sleep(diff)
        print("\nALL COST TIME = {:.2f} s".format(time.time() - start_time))
        # print("Can control start")
        # time.sleep(5)
        # print("Can control end")
