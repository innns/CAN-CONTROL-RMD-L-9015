import json

NOTE = (
    "pi does not work; kp,kd is the default PD controller para, index means motor id, DONT EDIT; DIRECTION means motor spin direction")
pi = [0x6F, 0x4F, 0x80, 0x20, 0x30, 0x00]
kp = [2.0, 6, 6, 6]
kd = [0.10, 0.10, 0.10, 0.10]
DIRECTION = [0, 1, -1, -1]  # 电机转动方向 由安装位置、操作要求决定
software_zero = [180, 168.5, 191.7, 0.3]
AMP_LOW = [0, -30, -30, -60]
AMP_UP = [0, 30, 30, 30]
IP = "127.0.0.1"
PORT = 5000

names = ['NOTE', 'pi', 'kp', 'kd', 'DIRECTION', 'software_zero', 'AMP_LOW', 'AMP_UP', 'IP', 'PORT']
para_dict = dict(zip(names, [NOTE, pi, kp, kd, DIRECTION, software_zero, AMP_LOW, AMP_UP, IP, PORT]))
para_dict_json = json.dumps(para_dict, indent=1)
with open('control_para.json', 'w', newline='\n') as file:
    file.write(para_dict_json)

with open('test.json', 'r') as file:
    data_raw = file.read()
data = json.loads(data_raw)
# print(data_raw)
print(data)
