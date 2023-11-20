import CanControlRMD
import math
import time

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
    while True:
        start_time = time.time()
        for i in range(HZ):
            CAN.motion_control(3,
                               D2R(calc_sin(30, 0, HZ, i)),
                               D2R(calc_cos(30, 0, HZ, i)) * 2 * math.pi / 10.0,
                               5,
                               0.3,
                               0)
            print("id {} : {}".format(i, calc_sin(30, 0, HZ, i)))
            diff = ALLTIME/HZ*(i+1) - (time.time() - start_time)
            if diff > 0:
                time.sleep(diff)
        print("ALL COST TIME = {} s".format(time.time() - start_time))
        print("Can control start")
        CAN.motion_control(3, D2R(calc_sin(30, 0, HZ, HZ)), 0.008, 5, 0.3, 0)
        time.sleep(5)
        print("Can control end")