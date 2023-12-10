import json
import socket
import threading


class MyUDPServer:
    _ip = '127.0.0.1'
    _port = 5000

    def __init__(self, ip: str, port: int):
        # 创建一个UDP套接字
        self._ip = ip
        self._port = port
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # set up socket broadcasting
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_sock.bind((ip, port))
        self.current_cmd = ''
        self.recv_json_data = {}

    def listen_once(self):
        # 接收对方发送的数据
        recv_data, addr = self.udp_sock.recvfrom(1024)
        self.recv_json_data = json.loads(recv_data.decode('utf-8'))
        self.current_cmd = 'NONE'
        if 'cmd' in self.recv_json_data.keys():
            self.current_cmd = self.recv_json_data['cmd']
        return self.recv_json_data

    def __listen_thread(self):
        while True:
            # 接收对方发送的数据
            recv_data, addr = self.udp_sock.recvfrom(1024)
            self.recv_json_data = json.loads(recv_data.decode('utf-8'))
            if 'cmd' in self.recv_json_data.keys():
                self.current_cmd = self.recv_json_data['cmd']
                continue
            self.current_cmd = 'NONE'

    def listen_threading(self):
        t = threading.Thread(target=self.__listen_thread)
        t.start()

    def get_json_data(self):
        return self.recv_json_data

    def clear_json_data(self):
        self.recv_json_data = {}
        return 1

    def get_cmd(self):
        return self.current_cmd

    def send_json_data(self, json_data: dict, port=_port):
        """
        发送json数据
        :param json_data: 按字典保存
        :param port: 端口号
        :return:
        UDP.send_json_data({"cmd": "clear"})
        """
        self.udp_sock.sendto(json.dumps(json_data).encode('utf-8'), ('127.0.0.1', port))

    def send_angle_json(self, motor_id: int, angle: float, port=_port):
        self.send_json_data({"cmd": "read_angle", "id": motor_id, "angle": "{}".format(angle)}, port)

    def close(self):
        self.udp_sock.close()

    def __del__(self):
        self.close()
