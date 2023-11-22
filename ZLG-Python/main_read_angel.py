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
    HZ = 5000
    ALL_TIME = 10
    time.sleep(1)
    CAN.close_motor(MOTOR[2])
    time.sleep(2)
    CAN.multi_angle_control(MOTOR[2],0x10,0)
    time.sleep(1)
    # CAN.init_motor_motion_single(MOTOR[3], 52.7)
    # time.sleep(2)
    # CAN.init_motor_motion_single(MOTOR[3], 0)
    # time.sleep(2)
    while True:
        start_time = time.time()
        for i in range(HZ):
            CAN.multi_angle_control(MOTOR[2], 0x10, 0)
        print("ALL COST TIME = {} s".format(time.time() - start_time))
        print("Can control start")
        time.sleep(5)
        print("Can control end")