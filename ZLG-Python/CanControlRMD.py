import zlgcan
import time
import math
import threading

zcanlib = zlgcan.ZCAN()


class CAN_MSG:
    def __init__(self, motor_id_=0, can_timestamp_=0, can_data_=[], single_angle_=0):
        self.motor_id = motor_id_
        self.can_timestamp = can_timestamp_
        self.can_data = can_data_
        self.single_angle = single_angle_

    def clear(self):
        self.motor_id = 0
        self.can_timestamp = 0
        self.can_data = []
        self.single_angle = 0


def D2R(x):
    return x * math.pi / 180.0


def R2D(x):
    return x * 180.0 / math.pi


def open_can(device_type=zlgcan.ZCAN_USBCAN1):
    global zcanlib
    device_handle = zcanlib.OpenDevice(device_type, 0, 0)
    if device_handle == zlgcan.INVALID_DEVICE_HANDLE:
        print("Open Device failed!")
        exit(0)
    print("device handle:%d." % device_handle)
    # info = zcanlib.GetDeviceInf(device_handle)
    # print("Device Information:\n%s" %(info))
    return device_handle


def open_channel(device_handle, channel):
    global zcanlib
    chn_init_cfg = zlgcan.ZCAN_CHANNEL_INIT_CONFIG()
    chn_init_cfg.can_type = zlgcan.ZCAN_TYPE_CAN
    chn_init_cfg.config.can.acc_mode = 0
    chn_init_cfg.config.can.acc_mask = 0xFFFFFFFF
    # From dev_info.json
    # 250K: (1,28)
    # 500K: (0,28)
    # 1M  : (0,20)
    chn_init_cfg.config.can.timing0 = 0
    chn_init_cfg.config.can.timing1 = 20
    chn_handle = zcanlib.InitCAN(device_handle, channel, chn_init_cfg)
    if chn_handle is None:
        return None
    zcanlib.StartCAN(chn_handle)
    return chn_handle


def transmit_can(chn_handle, stdorext, _id, _data, _len):
    global zcanlib
    transmit_num = 1
    msgs = (zlgcan.ZCAN_Transmit_Data * transmit_num)()
    for i in range(transmit_num):
        msgs[i].transmit_type = 0  # 0-正常发送，2-自发自收
        msgs[i].frame.eff = 0  # 0-标准帧，1-扩展帧
        msgs[i].frame.rtr = 0  # 0-数据帧，1-远程帧
        msgs[i].frame.can_id = _id
        msgs[i].frame.can_dlc = _len
        for j in range(msgs[i].frame.can_dlc):
            msgs[i].frame.data[j] = _data[j]
    zcanlib.Transmit(chn_handle, msgs, transmit_num)
    # ret = zcanlib.Transmit(chn_handle, msgs, transmit_num)
    # print("Tranmit Num: %d." % ret)


def receive_can(chn_handle, print_msg=False):
    global zcanlib
    rcv_num = zcanlib.GetReceiveNum(chn_handle, zlgcan.ZCAN_TYPE_CAN)
    if rcv_num:
        rcv_msg, rcv_num = zcanlib.Receive(chn_handle, rcv_num)
        if print_msg:
            print("Receive CAN message number:%d" % rcv_num)
            for i in range(rcv_num):
                print("[%d]:ts:%d, id:0x%x, dlc:%d, eff:%d, rtr:%d, data:%s" % (
                    i,
                    rcv_msg[i].timestamp,
                    rcv_msg[i].frame.can_id,
                    rcv_msg[i].frame.can_dlc,
                    rcv_msg[i].frame.eff, rcv_msg[i].frame.rtr,
                    ''.join(hex(rcv_msg[i].frame.data[j])[2:] +
                            ' ' for j in range(rcv_msg[i].frame.can_dlc))))
        return rcv_msg, rcv_num
    return None, 0


class CanControlRMD:
    global zcanlib

    STDID = 0x140
    MOTION_STDID = 0x400
    chn_handle = 0
    dev_handle = 0
    msg = CAN_MSG()

    def __init__(self, device_type_=zlgcan.ZCAN_USBCAN1, channel=0):
        # open device and channel 0
        self.dev_handle = open_can(device_type_)
        self.chn_handle = open_channel(self.dev_handle, channel)
        print("channel {} handle:{}.".format(channel, self.chn_handle))

    def torque_control(self, Motor_ID: int, iqControl: int):
        """
        Torque control A1 command 力矩控制
        :param Motor_ID: uint8_t
        :param iqControl: int16_t
        :return:
        """
        Motor_ID = Motor_ID & 0xff
        iqControl = iqControl & 0xffff
        data = [0xA1,
                0,
                0,
                0,
                iqControl & 0xff,
                (iqControl >> 8) & 0xff,
                0,
                0]
        transmit_can(self.chn_handle, 0, self.STDID + Motor_ID, data, 8)

    def speed_control(self, Motor_ID, speedControl):
        """
        speeed control A2 command 速度控制
        :param Motor_ID:
        :param speedControl:
        :return:
        """
        Motor_ID = Motor_ID & 0xff
        speedControl = speedControl & 0xffff
        data = [0xA2,
                0,
                0,
                0,
                speedControl & 0xff,
                (speedControl >> 8) & 0xff,
                (speedControl >> 16) & 0xff,
                (speedControl >> 24) & 0xff]
        transmit_can(self.chn_handle, 0, self.STDID + Motor_ID, data, 8)

    def set_PID(self, Motor_ID: int, C_KP: int, C_KI: int, S_KP: int, S_KI: int, P_KP: int, P_KI: int, save2ROM: bool):
        """
        设置电机的PID参数，所有参数都量化到 0 - 0xff
        :param Motor_ID:
        :param C_KP: uint8_t 代表电流环KP参数，C_KP / 0xff * 系统设置的电流环最大值 为实际参数
        :param C_KI: uint8_t 代表电流环KI参数，C_KI / 0xff * 系统设置的电流环最大值 为实际参数
        :param S_KP: uint8_t 代表速度环KP参数，S_KP / 0xff * 系统设置的速度环最大值 为实际参数
        :param S_KI: uint8_t 代表速度环KI参数，S_KI / 0xff * 系统设置的速度环最大值 为实际参数
        :param P_KP: uint8_t 代表位置环KP参数，P_KP / 0xff * 系统设置的位置环最大值 为实际参数
        :param P_KI: uint8_t 代表位置环KI参数，P_KI / 0xff * 系统设置的位置环最大值 为实际参数
        :param save2ROM: true 保存到 ROM，false 保存到 RAM
        :return:
        """
        CMD = 0x31
        if save2ROM:
            CMD = 0x32
        C_KP = C_KP & 0xff
        C_KI = C_KI & 0xff
        S_KP = S_KP & 0xff
        S_KI = S_KI & 0xff
        P_KP = P_KP & 0xff
        P_KI = P_KI & 0xff
        data = [CMD, 0, C_KP, C_KI, S_KP, S_KI, P_KP, P_KI]
        transmit_can(self.chn_handle, 0, self.STDID + Motor_ID, data, 8)

    def multi_angle_control(self, Motor_ID: int, maxSpeed: int, angleControl: int):
        """
        该指令为控制指令，在电机没有故障的情况下可以运行该指令。主机发送该命令以控制电机的位置（多圈角度）
        :param Motor_ID: uint8_t
        :param maxSpeed: uint16_t 如果位置环加速度为0，那么位置环将进入直接跟踪模式，
            通过 PI 控制器直接跟踪目标位置。其中 maxSpeed 限制了位置运行过程中的最大速度，如果 maxSpeed 值为 0，
            那么就完全由 PI 控制器计算结果输出。
        :param angleControl: int32_t 对应实际位置为0.01degree/LSB，即36000代表360°，
            电机转动方向由目标位置和当前位置的差值决定。
        :return:
        """
        Motor_ID = Motor_ID & 0xff
        maxSpeed = maxSpeed & 0xffff
        angleControl = angleControl & 0xffffffff
        data = [0xA4,
                0,
                maxSpeed & 0xff,
                (maxSpeed >> 8) & 0xff,
                angleControl & 0xff,
                (angleControl >> 8) & 0xff,
                (angleControl >> 16) & 0xff,
                (angleControl >> 24) & 0xff]
        transmit_can(self.chn_handle, 0, self.STDID + Motor_ID, data, 8)

    def single_loop_angle_control(self, Motor_ID: int, spinDirection: int, maxSpeed: int, angleControl: int):
        """
        主机发送该命令以控制电机的位置（单圈角度）。在多圈保存功能关闭时，默认为单圈模式。该指令可在单圈模式下使用。主要应用在直驱电机上。
        :param Motor_ID:
        :param maxSpeed: uint16_t 限制了电机转动的最大速度
        :param spinDirection: uint8_t 电机转动的方向，0x00代表顺时针，0x01代表逆时针
        :param angleControl: uint16_t 数值范围0~35999，对应实际位置为0.01degree/LSB 即实际角度范围0°~359.99°
        :return:
        """
        Motor_ID = Motor_ID & 0xff
        spinDirection = spinDirection & 0x01
        angleControl = angleControl & 0xffff
        data = [0xA6,
                spinDirection,
                maxSpeed & 0xff,
                (maxSpeed >> 8) & 0xff,
                angleControl & 0xff,
                (angleControl >> 8) & 0xff,
                0,
                0]
        transmit_can(self.chn_handle, 0, self.STDID + Motor_ID, data, 8)

    def motion_control(self, Motor_ID: int, p_des_: float, v_des_: float, kp_: float, kd_: float, t_ff_: float,
                       mod_pi=False):
        """
        :param Motor_ID: uint8_t
        :param p_des_: float 期望位置 -12.5到12.5，单位rad
        :param v_des_: float 期望速度 -45到45，单位rad/s
        :param kp_: float 位置偏差系数 0到500
        :param kd_: float 前馈力矩 0到5
        :param t_ff_: float 位置偏差系数 -24到24，单位N-m
        :return: IqRef = [kp*(p_des - p_fd_实际位置) + kd*(v_des - v_fb_实际速度) + t_ff]*KT_扭矩系数
        :param mod_pi: 是否归一化到0-2* pi
        """
        if mod_pi:
            p_des_ = p_des_ % (2 * math.pi)
        Motor_ID = Motor_ID & 0xff
        p_des = int((p_des_ + 12.5) / 25.0 * 65535) & 0xffff
        v_des = int((v_des_ + 45.0) / 90.0 * 4095) & 0xffff
        kp = int(kp_ / 500.0 * 4095) & 0xffff
        kd = int(kd_ / 5.0 * 4095) & 0xffff
        t_ff = int((t_ff_ + 24.0) / 48 * 4095) & 0xffff
        data = [(p_des >> 8) & 0xff,
                p_des & 0xff,
                (v_des >> 4) & 0xff,
                (((v_des & 0x0f) << 4) + ((kp >> 8) & 0x0f)) & 0xff,
                kp & 0xff,
                (kd >> 4) & 0xff,
                (((kd & 0x0f) << 4) + ((t_ff >> 8) & 0x0f)),
                t_ff]
        transmit_can(self.chn_handle, 0, self.MOTION_STDID + Motor_ID, data, 8)

    def close_motor(self, Motor_ID: int):
        Motor_ID = Motor_ID & 0xff
        data = [0x80, 0, 0, 0, 0, 0, 0, 0]
        transmit_can(self.chn_handle, 0, self.STDID + Motor_ID, data, 8)
        time.sleep(0.02)
        data = [0x76, 0, 0, 0, 0, 0, 0, 0]
        transmit_can(self.chn_handle, 0, self.STDID + Motor_ID, data, 8)

    def read_multi_angel(self, Motor_ID: int):
        Motor_ID = Motor_ID & 0xff
        data = [0x92, 0, 0, 0, 0, 0, 0, 0]
        transmit_can(self.chn_handle, 0, self.STDID + Motor_ID, data, 8)

    def read_single_angel(self, Motor_ID: int):
        Motor_ID = Motor_ID & 0xff
        data = [0x94, 0, 0, 0, 0, 0, 0, 0]
        transmit_can(self.chn_handle, 0, self.STDID + Motor_ID, data, 8)

    def read_encoder(self, Motor_ID: int):
        Motor_ID = Motor_ID & 0xff
        data = [0x60, 0, 0, 0, 0, 0, 0, 0]
        transmit_can(self.chn_handle, 0, self.STDID + Motor_ID, data, 8)

    def read_raw_encoder(self, Motor_ID: int):
        Motor_ID = Motor_ID & 0xff
        data = [0x61, 0, 0, 0, 0, 0, 0, 0]
        transmit_can(self.chn_handle, 0, self.STDID + Motor_ID, data, 8)

    def read_zero_shift_encoder(self, Motor_ID: int):
        Motor_ID = Motor_ID & 0xff
        data = [0x62, 0, 0, 0, 0, 0, 0, 0]
        transmit_can(self.chn_handle, 0, self.STDID + Motor_ID, data, 8)

    def close_multi(self, Motor_ID: int, is_resetting_zero: bool):
        Motor_ID = Motor_ID & 0xff
        data = [0x20, 0x04, 0, 0, 0, 0, 0, 0]
        if is_resetting_zero:
            data = [0x20, 0x01, 0, 0, 0, 0, 0, 0]
        transmit_can(self.chn_handle, 0, self.STDID + Motor_ID, data, 8)

    def open_multi(self, Motor_ID: int):
        Motor_ID = Motor_ID & 0xff
        data = [0x20, 0x04, 0, 0, 1, 0, 0, 0]
        transmit_can(self.chn_handle, 0, self.STDID + Motor_ID, data, 8)

    def set_zero(self, Motor_ID: int, zero_data: int):
        Motor_ID = Motor_ID & 0xff
        zero_data = zero_data & 0xffffffff
        data = [0x63,
                0,
                0,
                0,
                zero_data & 0xff,
                (zero_data >> 8) & 0xff,
                (zero_data >> 16) & 0xff,
                (zero_data >> 24) & 0xff]
        transmit_can(self.chn_handle, 0, self.STDID + Motor_ID, data, 8)

    # def init_motor_motion_single(self, Motor_ID: int, pos_des : float):
    #     Motor_ID = Motor_ID & 0xff
    #     data = [0x94,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0,
    #             0]
    #     transmit_can(self.chn_handle, 0, self.MOTION_STDID + Motor_ID, data, 8)
    #     time.sleep(0.01)
    #     msg, num = receive_can(self.chn_handle)
    #     if num > 0:
    #         pos_cur = (msg[0].frame.data[6] + ((msg[0].frame.data[7]) << 8)) / 100.0
    #         print("init_motor_single Motor_ID:{} pos_cur:{} pos_des:{}".format(Motor_ID, pos_cur, pos_des))
    #         pos_diff = pos_des - pos_cur
    #         idx = pos_diff/100.0
    #         for i in range(100):
    #             self.motion_control(Motor_ID, D2R(pos_cur + (i+1) * idx), 0, 0, 0, 0.2)
    #             time.sleep(0.02)

    def recv_can(self):
        # receive can message
        zcanlib.ClearBuffer(self.chn_handle)
        return receive_can(self.chn_handle)

    def process_recv_can(self, print_msg=False):
        # receive can message
        msg, num = receive_can(self.chn_handle, print_msg)
        if num > 0:
            for i in range(num):
                if 0x240 < msg[i].frame.can_id < 0x400:  # 返回的是电机数据
                    motor_id = msg[i].frame.can_id - 0x240
                    if msg[i].frame.can_dlc == 8 and msg[i].frame.data[0] == 0x92:
                        angel = ((msg[i].frame.data[4]) |
                                 (msg[i].frame.data[5] << 8) |
                                 (msg[i].frame.data[6] << 16) |
                                 (msg[i].frame.data[7] << 24))
                        if angel > 0x80000000:
                            angel = angel - 0x100000000
                        angel = angel / 100.0
                        if print_msg:
                            print("motor_id:{} angel:{}".format(motor_id, angel))
                        self.msg = CAN_MSG(motor_id, msg[i].timestamp, msg[i].frame.data[:], angel)
                    elif msg[i].frame.can_dlc == 8 and msg[i].frame.data[0] == 0x94:
                        angel = ((msg[i].frame.data[6]) |
                                 (msg[i].frame.data[7] << 8))
                        angel = angel / 100.0
                        if print_msg:
                            print("motor_id:{} SINGLE angel:{}".format(motor_id, angel))
                        self.msg = CAN_MSG(motor_id, msg[i].timestamp, msg[i].frame.data[:], angel)
                    elif msg[i].frame.can_dlc == 8 and msg[i].frame.data[0] == 0x60:
                        encoder_data = ((msg[i].frame.data[4]) |
                                        (msg[i].frame.data[5] << 8) |
                                        (msg[i].frame.data[6] << 16) |
                                        (msg[i].frame.data[7] << 24))
                        if encoder_data > 0x80000000:
                            encoder_data = encoder_data - 0x100000000
                        if print_msg:
                            print("#### motor_id:{} encoder_data:{}".format(motor_id, encoder_data))
                    elif msg[i].frame.can_dlc == 8 and msg[i].frame.data[0] == 0x61:
                        encoder_data = ((msg[i].frame.data[4]) |
                                        (msg[i].frame.data[5] << 8) |
                                        (msg[i].frame.data[6] << 16) |
                                        (msg[i].frame.data[7] << 24))
                        if encoder_data > 0x80000000:
                            encoder_data = encoder_data - 0x100000000
                        if print_msg:
                            print("#### motor_id:{} raw_encoder_data:{}".format(motor_id, encoder_data))
                    elif msg[i].frame.can_dlc == 8 and msg[i].frame.data[0] == 0x62:
                        encoder_data = ((msg[i].frame.data[4]) |
                                        (msg[i].frame.data[5] << 8) |
                                        (msg[i].frame.data[6] << 16) |
                                        (msg[i].frame.data[7] << 24))
                        if encoder_data > 0x80000000:
                            encoder_data = encoder_data - 0x100000000
                        if print_msg:
                            print("#### motor_id:{} zero_shift_encoder_data:{}".format(motor_id, encoder_data))
        # time.sleep(0.001)

    def __process_recv_can_thread(self, print_msg=False):
        while 1:
            self.process_recv_can(print_msg)

    def get_msg(self):
        return self.msg

    def recv_can_threading(self, print_msg=False):
        # receive can message
        threading.Thread(target=self.__process_recv_can_thread, args=(print_msg,)).start()

    def close(self):
        # Close Channel
        zcanlib.ResetCAN(self.chn_handle)
        # Close Device
        zcanlib.CloseDevice(self.dev_handle)
        print("Finished")

    def __del__(self):
        self.close()


if __name__ == '__main__':
    can = CanControlRMD()
    while 1:
        can.read_single_angel(3)
        can.process_recv_can(True)
        time.sleep(0.1)
