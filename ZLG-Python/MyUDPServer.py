import json
import socket
import threading


class MyUDPServer:
    def __init__(self, ip: str, port: int):
        # 创建一个UDP套接字
        self.ip = ip
        self.port = port
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # set up socket broadcasting
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_sock.bind((ip, port))
        self.current_cmd = ''
        self.recv_json_data = {}

    def listen(self):
        while True:
            # 接收对方发送的数据
            recv_data, addr = self.udp_sock.recvfrom(1024)
            self.recv_json_data = json.loads(recv_data.decode('utf-8'))
            if self.recv_json_data.has_key('cmd'):
                self.current_cmd = self.recv_json_data['cmd']
                continue
            self.current_cmd = 'NONE'

    def listen_threading(self):
        t = threading.Thread(target=self.listen)
        t.start()

    def get_json_data(self):
        return self.recv_json_data

    def get_cmd(self):
        return self.current_cmd

    def send_json_data(self, json_data):
        self.udp_sock.sendto(json.dumps(json_data).encode('utf-8'), ('<broadcast>', self.port))

    def close(self):
        self.udp_sock.close()

    def __del__(self):
        self.close()
