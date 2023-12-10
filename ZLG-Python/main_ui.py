# !/user/bin/env Python3
# -*- coding:utf-8 -*-

"""
file：window.py.py
create time:2019/6/27 14:54
author:Loong Xu
desc: 窗口
"""
import tkinter as tk
from tkinter import filedialog, dialog
import os
import collections
import math
import CanControlRMD
import time
import json

NOTE = (
    "pi does not work; kp,kd is the default PD controller para, index means motor id, DONT EDIT; DIRECTION means motor spin direction")
pi = [0x6F, 0x4F, 0x80, 0x20, 0x30, 0x00]
kp = [2.0, 6, 6, 6]
kd = [0.10, 0.10, 0.10, 0.10]
DIRECTION = [0, 1, -1, -1]  # 电机转动方向 由安装位置、操作要求决定
software_zero = [180, 168.5, 191.7, 110]
AMP_LOW = [0, -30, -30, -60]
AMP_UP = [0, 30, 30, 30]
IP = "127.0.0.1"
PORT = 5000

names = ['NOTE', 'pi', 'kp', 'kd', 'DIRECTION', 'software_zero', 'AMP_LOW', 'AMP_UP', 'IP', 'PORT']

with open("control_para.json", "r") as f:
    data_raw = f.read()
    print(data_raw)
    data = json.loads(data_raw)
    if all(key in data for key in names):
        print("USING JSON PARA")
        pi = data['pi']
        kp = data['kp']
        kd = data['kd']
        DIRECTION = data['DIRECTION']
        software_zero = data['software_zero']
        AMP_LOW = data['AMP_LOW']
        AMP_UP = data['AMP_UP']
        IP = data['IP']
        PORT = data['PORT']
    else:
        print("USING DEFAULT PARA")


def D2R(x):
    return x * math.pi / 180.0


def R2D(x):
    return x * 180.0 / math.pi


window = tk.Tk()
window.title('MOTOR CONTROLL')  # 标题
window.geometry('800x600')  # 窗口尺寸

file_path = ''

file_text = ''

all_data = collections.deque()

text_show = tk.Text(window, width=100, height=10, bg='orange', font=('Arial', 12))
text_show.grid(row=0, column=0, columnspan=4, sticky='we')

text_cur_show = tk.Text(window, width=100, height=10, bg='green', font=('Arial', 12))
text_cur_show.grid(row=1, column=0, columnspan=4, sticky='we')
#
# text_recv_show = tk.Text(window, width=80, height=4, bg='green', font=('Arial', 12))
# text_recv_show.pack()
CAN = CanControlRMD.CanControlRMD()
CAN.recv_can_threading(True)


def open_file():
    '''
    打开文件
    :return:
    '''
    global file_path
    global file_text
    global all_data
    file_path = filedialog.askopenfilename(title=u'选择文件', initialdir=(os.getcwd()))
    print('打开文件：', file_path)
    if file_path is not None:
        # 创建一个空列表用于存储文件内容
        all_data.clear()
        file_text = ""
        # 使用with语句打开文件
        with open(file=file_path, mode='r+', encoding='utf-8') as file:
            # 逐行读取文件
            lines = file.readlines()
            for line in lines:
                if len(line) < 3:
                    continue
                file_text += line
                # 去除每行末尾的换行符
                line = line.strip()
                print(line)
                # 拆分每一行的数据
                parts = line.split(',')
                # 转换数据类型并添加到列表
                if parts[0].isdigit() and parts[1].isdigit():
                    index = int(parts[0])
                    motor_id = int(parts[1])
                    angle = float(parts[2])
                    all_data.append((index, motor_id, angle))
        text_show.insert('insert', file_text)


def activate_control_once():
    global all_data
    global CAN
    cur_index = 0
    print(all_data)
    if len(all_data) != 0:
        cur_index = all_data[0][0]
        while all_data is not None:
            if all_data[0][0] == cur_index:
                text_cur_show.insert('insert',
                                     "index {:4d}\tmotor {:d}\tangel={:6.3f}\n".format(all_data[0][0], all_data[0][1],
                                                                                       all_data[0][2]))
                CAN.multi_angle_control(all_data[0][1], 0x05, int(all_data[0][2] * 100))
                print(all_data.popleft())
            else:
                break


def activate_control():
    start_time = time.time()
    HZ = 50
    ALL_TIME = 5
    cnt = 0
    while len(all_data) > 0:
        activate_control_once()
        cnt += 1
        diff = 1 / HZ * cnt - (time.time() - start_time)
        if diff > 0:
            time.sleep(diff)


def set_pid():
    global pi
    CAN.set_PID(1, pi[0], pi[1], pi[2], pi[3], pi[4], pi[5], False)
    CAN.set_PID(2, pi[0], pi[1], pi[2], pi[3], pi[4], pi[5], False)
    CAN.set_PID(3, pi[0], pi[1], pi[2], pi[3], pi[4], pi[5], False)


def read_angles():
    s_a = [0, 0, 0, 0]
    m_a = [0, 0, 0, 0]
    for i in range(1, 4):
        # 3个电机
        for j in range(3):
            # 重试三次
            CAN.read_multi_angel(i)
            time.sleep(0.01)
            msg = CAN.get_msg()
            print("{} WANT_{} MOTOR_{} SINGLE_ANGLE_{}".format("#" * i + "_" * (3 - i), i, msg.motor_id,
                                                               msg.single_angle))
            if msg.motor_id == i:
                s_a[i] = msg.single_angle
                break
    for i in range(1, 4):
        # 3个电机
        for j in range(3):
            # 重试三次
            CAN.read_single_angel(i)
            time.sleep(0.01)
            msg = CAN.get_msg()
            print("{} WANT_{} MOTOR_{} SINGLE_ANGLE_{}".format("#" * i + "_" * (3 - i), i, msg.motor_id,
                                                               msg.single_angle))
            if msg.motor_id == i:
                m_a[i] = msg.single_angle
    for i in range(1, 4):
        text_cur_show.insert('insert',
                             "MOTOR {} \tZERO {:.2f} \tSINGLE {:.2f} \tMULTI {:.2f} \tOFFSET {:.2f}\n". \
                             format(i,
                                    software_zero[i],
                                    s_a[i],
                                    m_a[i],
                                    m_a[i] -
                                    software_zero[i]))


def read_encoder():
    for i in range(1, 4):
        # 3个电机
        for j in range(3):
            # 重试三次
            CAN.read_encoder(i)
            time.sleep(0.3)


def read_raw_encoder():
    for i in range(1, 4):
        # 3个电机
        for j in range(3):
            # 重试三次
            CAN.read_raw_encoder(i)
            time.sleep(0.03)


def read_zero_shift_encoder():
    for i in range(1, 4):
        # 3个电机
        for j in range(3):
            # 重试三次
            CAN.read_zero_shift_encoder(i)
            time.sleep(0.3)


def close_multi():
    CAN.close_multi(2, False)


def open_mul():
    CAN.open_multi(2)


def close_motors():
    CAN.close_motor(1)
    time.sleep(0.01)
    CAN.close_motor(2)
    time.sleep(0.01)
    CAN.close_motor(3)


def move_to_zero():
    global pi, kp, kd, DIRECTION, software_zero, AMP_LOW, AMP_UP, IP, PORT
    for i in range(1, 4):
        # TODO: >>>>>>>>>>>>>>>>>>>>>>> 注意调参 >>>>>>>>>>>>>>>>>>>>>>>>>
        CAN.motion_control(i,
                           D2R(software_zero[i]),
                           0.2,
                           1.5,
                           0.05,
                           0)


def move_to_zero_hard():
    global pi, kp, kd, DIRECTION, software_zero, AMP_LOW, AMP_UP, IP, PORT
    for i in range(1, 4):
        # TODO: >>>>>>>>>>>>>>>>>>>>>>> 注意调参 >>>>>>>>>>>>>>>>>>>>>>>>>
        CAN.motion_control(i,
                           D2R(software_zero[i]),
                           0.2,
                           4,
                           0.10,
                           0)
        # CAN.motion_control(i,
        #                    D2R(software_zero[i]),
        #                    0.2,
        #                    1.5,
        #                    0.05,
        #                    0)


def record_angles():
    global pi, kp, kd, DIRECTION, software_zero, AMP_LOW, AMP_UP, IP, PORT
    angles = [0, 0, 0, 0]
    HZ = 4
    ALL_TIME = 60
    start_time = time.time()
    with open("record_data.csv", "w+") as file:
        file.write("油门,横向,纵向\n")
        for cnt in range(HZ * ALL_TIME):
            for i in range(1, 4):
                # 3个电机
                for j in range(3):
                    # 重试三次
                    CAN.read_single_angel(i)
                    time.sleep(0.01)
                    msg = CAN.get_msg()
                    print("{} WANT_{} MOTOR_{} SINGLE_ANGLE_{}".format("#" * i + "_" * (3 - i), i, msg.motor_id,
                                                                       msg.single_angle))
                    if msg.motor_id == i:
                        angles[i] = DIRECTION[i] * (msg.single_angle - software_zero[i])
            file.write("{},{},{}\n".format((8.0 + angles[3]), angles[1], angles[2]))  # 8.0 油门自带重力 需要补偿一些
            angles = [0, 0, 0, 0]
            diff = 1 / HZ * (cnt + 1) - (time.time() - start_time)
            if (diff > 0):
                time.sleep(diff)


def set_software_zero():
    global pi, kp, kd, DIRECTION, software_zero, AMP_LOW, AMP_UP, IP, PORT
    with open("control_para.json", "r") as f:
        data_raw = f.read()
        print(data_raw)
        data = json.loads(data_raw)
        if all(key in data for key in names):
            print("USING JSON PARA")
            pi = data['pi']
            kp = data['kp']
            kd = data['kd']
            DIRECTION = data['DIRECTION']
            software_zero = data['software_zero']
            AMP_LOW = data['AMP_LOW']
            AMP_UP = data['AMP_UP']
            IP = data['IP']
            PORT = data['PORT']
        else:
            print("USING DEFAULT PARA")
    for i in range(1, 4):
        # 3个电机
        for j in range(10):
            # 重试三次
            CAN.read_multi_angel(i)
            time.sleep(0.01)
            msg = CAN.get_msg()
            print("{} MOTOR_{} RECV{} ANGLE_{}".format("#" * i + "_" * (3 - i), i, msg.motor_id, msg.single_angle))
            time.sleep(0.01)
            if msg.motor_id == i:
                # CAN.multi_angle_control(i, 0x05, offset[i])
                software_zero[msg.motor_id] = msg.single_angle
                break
    with open('control_para.json', 'w', newline='\n') as file:
        para_dict = dict(zip(names, [NOTE, pi, kp, kd, DIRECTION, software_zero, AMP_LOW, AMP_UP, IP, PORT]))
        para_dict_json = json.dumps(para_dict, indent=1)
        file.write(para_dict_json)
    for i in range(1, 4):
        text_cur_show.insert('insert', "MOTOR {}\tZERO {:.2f}\n".format(i, software_zero[i]))


bt_open = tk.Button(window, text='打开文件', width=15, height=2, command=open_file)
bt_open.grid(row=2, column=0)

bt_activate = tk.Button(window, text='单次控制', width=15, height=2, command=activate_control_once)
bt_activate.grid(row=2, column=1)

bt_activate = tk.Button(window, text='启动控制', width=15, height=2, command=activate_control)
bt_activate.grid(row=2, column=2)

bt_read_angles = tk.Button(window, text='读取当前角度', width=15, height=2, command=read_angles)
bt_read_angles.grid(row=3, column=0)

bt_set_zero = tk.Button(window, text='设置当前角度为零位', width=15, height=2, command=set_software_zero)
bt_set_zero.grid(row=3, column=1)

bt_close_motors = tk.Button(window, text='关闭电机', width=15, height=2, command=close_motors)
bt_close_motors.grid(row=3, column=2)

bt_move_to_zero = tk.Button(window, text='复位到零位', width=15, height=2, command=move_to_zero)
bt_move_to_zero.grid(row=4, column=0)

bt_record = tk.Button(window, text='开始录制_1min', width=15, height=2, command=record_angles)
bt_record.grid(row=4, column=1)

bt_move_to_zero_hard = tk.Button(window, text='复位到零位 大力', width=15, height=2, command=move_to_zero_hard)
bt_move_to_zero_hard.grid(row=4, column=2)


# bt_pid = tk.Button(window, text='set pid', width=15, height=1, command=set_pid)
# bt_pid.pack()


bt_encoder = tk.Button(window, text='read_encoder', width=15, height=1, command=read_encoder)
bt_encoder.grid(row=5, column=0)

bt_raw_encoder = tk.Button(window, text='read_raw_encoder', width=15, height=1, command=read_raw_encoder)
bt_raw_encoder.grid(row=5, column=1)

bt_zs_encoder = tk.Button(window, text='read_zs_encoder', width=15, height=1, command=read_zero_shift_encoder)
bt_zs_encoder.grid(row=5, column=2)

bt_open_mul = tk.Button(window, text='bt_open_mul', width=15, height=1, command=open_mul)
bt_open_mul.grid(row=6, column=0)

bt_close_mul = tk.Button(window, text='bt_close_mul', width=15, height=1, command=close_multi)
bt_close_mul.grid(row=6, column=1)

window.mainloop()  # 显示
