import zlgcan

zcanlib = zlgcan.ZCAN()


def open_usbcan2(device_type=zlgcan.ZCAN_USBCAN1):
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


def receive_can(chn_handle):
    global zcanlib
    rcv_num = zcanlib.GetReceiveNum(chn_handle, zlgcan.ZCAN_TYPE_CAN)
    if rcv_num:
        print("Receive CAN message number:%d" % rcv_num)
        rcv_msg, rcv_num = zcanlib.Receive(chn_handle, rcv_num)
        for i in range(rcv_num):
            print("[%d]:ts:%d, id:0x%x, dlc:%d, eff:%d, rtr:%d, data:%s" % (
                i,
                rcv_msg[i].timestamp,
                rcv_msg[i].frame.can_id,
                rcv_msg[i].frame.can_dlc,
                rcv_msg[i].frame.eff, rcv_msg[i].frame.rtr,
                ''.join(hex(rcv_msg[i].frame.data[j])[2:] +
                        ' ' for j in range(rcv_msg[i].frame.can_dlc))))


class CanControlRMD():
    global zcanlib

    STDID = 0x140
    MOTION_STDID = 0x400
    chn_handle = 0
    dev_handle = 0

    def __init__(self, device_type_=zlgcan.ZCAN_USBCAN1, channel=0):
        # open device and channel 0
        self.dev_handle = open_usbcan2(device_type_)
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
        angleControl = maxSpeed & 0xffffffff
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

    def motion_control(self, Motor_ID: int, p_des_: float, v_des_: float, kp_: float, kd_: float, t_ff_: float):
        """
        :param Motor_ID: uint8_t
        :param p_des_: uint16_t 期望位置 -12.5到12.5，单位rad
        :param v_des_: uint16_t 期望速度 -45到45，单位rad/s
        :param kp_: uint16_t 位置偏差系数 0到500
        :param kd_: uint16_t 前馈力矩 0到5
        :param t_ff_: uint16_t 位置偏差系数 -24到24，单位N-m
        :return: IqRef = [kp*(p_des - p_fd_实际位置) + kd*(v_des - v_fb_实际速度) + t_ff]*KT_扭矩系数
        """
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

    def CAN_RECV(self):
        # receive can message
        zcanlib.ClearBuffer(self.chn_handle)
        receive_can(self.chn_handle)

    def __del__(self):
        # Close Channel
        zcanlib.ResetCAN(self.chn_handle)
        # Close Device
        zcanlib.CloseDevice(self.dev_handle)
        print("Finished")
