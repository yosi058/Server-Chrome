import socket
import sys
import os.path
from os import path

TCP_IP = '127.0.0.1'
TCP_PORT = 12345
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(4)

while True:
    client, addr = s.accept()
    client.settimeout(5)
    not_close = True
    while not_close:
        try:
            buffer = client.recv(BUFFER_SIZE).decode()
            if not buffer:
                break
            buffering = True
            while buffering:
                if '\r\n\r\n' in buffer:
                    buffering = False
                else:
                    more = s.recv(BUFFER_SIZE)
                    buffer += more
            http = "HTTP/1.1"
            http_ok = "200 OK\n"
            http_not_found = "404 Not Found\n"
            http_move = "301 Moved Permanently\n"
            conn = "Connection:"
            len_msg = "Contend-Lenght:"
            folder = "files"
            mas_to_client = None
            conn_mas = None
            location = "Location: /result.html\n"
            data_seg = buffer.split("\r\n")
            for info in data_seg:
                if "Connection" in info:
                    conn_mas = conn + info.split("Connection:")[1] + "\n"
                    if "close" in conn_mas:
                        not_close = False
            line = data_seg[0].split(' ')
            path_file = ''.join(line[1:-1])
            if not path.exists(folder + path_file):
                mas_client = http + http_not_found + conn + "close\n" + "\n"
                print(mas_client)
                client.send(bytes(mas_client.encode('utf-8')))
                not_close = False
                break
            if path_file == "/":
                path_file = "/index.html"
            elif path_file == "/redirect":
                mas_client = http + http_move + conn + "close\n" + location + "\n"
                client.send(bytes(mas_client.encode('utf-8')))
                not_close = False
                break
            with open(folder + path_file, 'rb') as file:
                lines = file.read()
            len_lines = len_msg + str(len(lines)) + "\n"
            mas_client = http + http_ok + conn_mas + len_lines + "\n"
            client.send(bytes(mas_client.encode('utf-8')))
            client.send(bytes(lines))
        except TimeoutError as e:
            not_close = False
            client.close()
            break
        finally:
            client.close()
            break
