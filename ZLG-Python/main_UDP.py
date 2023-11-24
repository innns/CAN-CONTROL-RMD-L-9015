import tqdm.notebook

import CanControlRMD
import math
import time
import MyUDPServer

MOTOR = [i for i in range(10)]


def D2R(x):
    return x * math.pi / 180.0


def R2D(x):
    return x * 180.0 / math.pi


if __name__ == '__main__':
    CAN = CanControlRMD.CanControlRMD()
    # UDP socket
    UDP = MyUDPServer.MyUDPServer('127.0.0.1', 5000)
    UDP.listen_threading()
    # 创建一个can 监听线程并启动
    # CAN.recv_can_threading()

    while 1:
        json_data = UDP.get_json_data()
        if json_data.has_key('cmd'):
            cmd = json_data['cmd']
            if cmd == 'close_ALL':
                UDP.close()
                CAN.close()
                break
            elif cmd == 'angle':
                CAN.multi_angle_control(json_data['id'], 0x05, json_data['angel'])
            elif cmd == 'motion':
                CAN.motion_control(json_data['id'], json_data['p_des'], json_data['v_des'], 5, 0.3, 0.2)
            elif cmd == 'set_PID':
                CAN.set_PID(json_data['id'],
                            json_data['cp'], json_data['ci'],
                            json_data['sp'], json_data['si'],
                            json_data['pp'], json_data['pi'],
                            json_data['save'])
            elif cmd == 'close_motor':
                CAN.close_motor(json_data['id'])
            elif cmd == 'read':
                CAN.read_multi_angel(json_data['id'])
                CAN.process_recv_can()
                msg = CAN.get_msg()
                if msg is not None:
                    send_data = {'id': msg.motor_id, 'angel': msg.angel}
                    UDP.send_json_data(send_data)
                    print("SEND: ", send_data)

    # time.sleep(1)
    # CAN.close_motor(MOTOR[3])
    # time.sleep(2)
    # CAN.set_PID(MOTOR[3], 0x30, 0x0A, 0x30, 0x0, 0x4A, 0x00, False)
    # CAN.multi_angle_control(MOTOR[3], 0x05, 0)
    # while True:
    #     start_time = time.time()
    #     # for i in range((HZ * ALL_TIME)):
    #     HZ = 50
    #     ALL_TIME = 20
    #     i = 0
    #     for i in range(HZ * ALL_TIME):
    #         i += 1
    #         CAN.read_multi_angel(MOTOR[3])
    #         msg = CAN.get_msg()
    #
    #     print("\nALL COST TIME = {:.2f} s".format(time.time() - start_time))
