import CanControlRMD
import math
import time
import tqdm
from tqdm import trange
import keyboard

MOTOR = [i for i in range(10)]

pi = [0x7F, 0x4F, 0x80, 0x20, 0x40, 0x00]
id = 0


def AMP_LIMIT(x, max, min):
    if x > max:
        return max
    elif x < min:
        return min
    else:
        return x


def key_fun():
    global pi, id
    # print("key_fun")
    id += 1
    if keyboard.is_pressed('1'):
        pi[0] += 1
        return 0
    elif keyboard.is_pressed('q'):
        pi[0] -= 1
        return 0
    elif keyboard.is_pressed('2'):
        pi[1] += 1
        return 0
    elif keyboard.is_pressed('w'):
        pi[1] -= 1
        return 0
    elif keyboard.is_pressed('3'):
        pi[2] += 1
        return 0
    elif keyboard.is_pressed('e'):
        pi[2] -= 1
        return 0
    elif keyboard.is_pressed('4'):
        pi[3] += 1
        return 0
    elif keyboard.is_pressed('r'):
        pi[3] -= 1
        return 0
    elif keyboard.is_pressed('5'):
        pi[4] += 1
        return 0
    elif keyboard.is_pressed('t'):
        pi[4] -= 1
        return 0
    elif keyboard.is_pressed('6'):
        pi[5] += 1
        return 0
    elif keyboard.is_pressed('y'):
        pi[5] -= 1
        return 0
    id -= 1


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
    HZ = 50
    ALL_TIME = 5
    # CAN.close_motor(MOTOR[1])
    # time.sleep(0.2)
    # # CAN.multi_angle_control(MOTOR[3], 0x30, 5270)
    # # time.sleep(2)
    # CAN.multi_angle_control(MOTOR[1], 0x30, 0)
    # CAN.multi_angle_control(MOTOR[2], 0x30, 0)
    #
    # time.sleep(1)
    #
    CAN.close_motor(MOTOR[1])
    CAN.close_motor(MOTOR[2])

    time.sleep(2)

    while True:
        start_time = time.time()
        CAN.set_PID(MOTOR[3], pi[0], pi[1], pi[2], pi[3], pi[4], pi[5], False)
        for i in range((HZ * ALL_TIME)):
            #     t_ff = 0.2
            #     if (calc_sin(1, 0, HZ, i) - calc_sin(1, 0, HZ, i - 1)) > 0:
            #         t_ff = 0.4
            # CAN.motion_control(MOTOR[3],
            #                    D2R(calc_sin(15, 0, HZ * ALL_TIME, i)+5),
            #                    0.01,
            #                    1.0,
            #                    0.06,
            #                    0)
            # CAN.motion_control(MOTOR[3],
            #                    D2R(calc_sin(15, 0, HZ * ALL_TIME, i)),
            #                    0.05,
            #                    0.8,
            #                    0.01,
            #                    0)
            CAN.recv_can_threading()
            # CAN.multi_angle_control(MOTOR[1], 0x05, int(100 * calc_sin(10, 0, HZ * ALL_TIME, i)))
            #

            # CAN.multi_angle_control(MOTOR[2], 0x05, 0)
            CAN.multi_angle_control(MOTOR[3], 0x05, int(100 * (-20 + calc_sin(20, 0, HZ * ALL_TIME, i))))
            # CAN.multi_angle_control(MOTOR[1], 0x30, int(100 * calc_sin(10, 0, HZ * ALL_TIME, i)))
            # print(
            #     "id {} : {}".format(i, calc_sin(10, 0, HZ * ALL_TIME, i)))
            # id_ = id
            # key_fun()
            # for jj in range(6):
            #     pi[jj] = AMP_LIMIT(pi[jj], 0xff, 0)
            # CAN.set_PID(MOTOR[1], pi[0], pi[1], pi[2], pi[3], pi[4], pi[5], False)
            # CAN.set_PID(MOTOR[2], pi[0], pi[1], pi[2], pi[3], pi[4], pi[5], False)
            #
            # if id_ != id:
            #     print("")
            #     print("Cur  KP {:2X} KI {:2X}".format(pi[0], pi[1]))
            #     print("Spd  KP {:2X} KI {:2X}".format(pi[2], pi[3]))
            #     print("Pos  KP {:2X} KI {:2X}".format(pi[4], pi[5]))

            diff = 1 / HZ * (i + 1) - (time.time() - start_time)
            if (diff > 0):
                time.sleep(diff)
        print("ALL COST TIME = {} s".format(time.time() - start_time))
        print("Can control start")
        # CAN.motion_control(MOTOR[3], 0, 0.008, 3, 0.3, 0.06)
        # time.sleep(20)
        print("Can control end")
