import CanControlRMD
import math
import time

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
    HZ = 500
    ALLTIME = 10
    CAN.close_motor(MOTOR[3])
    time.sleep(0.2)
    CAN.multi_angle_control(MOTOR[3], 0x80, 5270)
    time.sleep(3)
    CAN.multi_angle_control(MOTOR[3], 0x80, 0)
    time.sleep(2)
    CAN.close_motor(MOTOR[3])
    # CAN.init_motor_motion_single(MOTOR[3], 52.7)
    # time.sleep(2)
    # CAN.init_motor_motion_single(MOTOR[3], 0)
    # time.sleep(2)
    while True:
        start_time = time.time()
        for i in range(HZ):
            t_ff = 0.2
            if (calc_sin(1, 0, HZ, i) - calc_sin(1, 0, HZ, i - 1)) > 0:
                t_ff = 0.4
            CAN.motion_control(MOTOR[3],
                               D2R(calc_sin(30, 0, HZ, i)),
                               D2R(calc_cos(30, 0, HZ, i)) * 2 * math.pi / 10.0,
                               5,
                               0.3,
                               t_ff)
            print("id {} : {}".format(i, calc_sin(30, 0, HZ, i)))
            diff = ALLTIME / HZ * (i + 1) - (time.time() - start_time)
            if diff > 0:
                time.sleep(diff)
        print("ALL COST TIME = {} s".format(time.time() - start_time))
        print("Can control start")
        CAN.motion_control(MOTOR[3], D2R(calc_sin(30, 0, HZ, HZ)), 0.008, 5, 0.3, 0.4)
        time.sleep(5)
        print("Can control end")
