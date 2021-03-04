import socket
import sys
from os import path

TCP_IP = '0.0.0.0'
TCP_PORT = int(sys.argv[1])
BUFFER_SIZE = 1024
# created a socket to be a server.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the server to a port number.
s.bind((TCP_IP, TCP_PORT))
# can receive 5 client parallel
s.listen(5)
# http msg of the protocol
http = "HTTP/1.1 "
http_ok = "200 OK\n"
http_not_found = " 404 Not Found\n"
http_move = "301 Moved Permanently\n"
conn = "Connection:"
http_len_msg = "Content-Length:"
folder = "files"
msg_to_client = None
http_conn_mas = None
location = "Location: /result.html\n"

while True:
    # receive a client
    client, addr = s.accept()
    # give him 1 sec before timeout.
    client.settimeout(1)
    not_close = True
    while not_close:
        try:
            # get data from the client
            buffer = client.recv(BUFFER_SIZE).decode()
            if not buffer:
                break
            buffering = True
            # receive all the data and put him in the buffer
            while buffering:
                if '\r\n\r\n' in buffer:
                    buffering = False
                else:
                    more = client.recv(BUFFER_SIZE).decode()
                    buffer += more
                    # split the buffer line by line
            print(buffer)
            data_seg = buffer.split("\r\n")
            for line in data_seg:
                if "Connection" in line:
                    http_conn_mas = conn + line.split("Connection:")[1] + "\n"
                    if "close" in http_conn_mas:
                        not_close = False
            # take the path of the file from the first line
            first_line = data_seg[0].split(' ')
            path_file = ''.join(first_line[1:-1])
            # redirect moved ant the http need to find him in the folder
            if path_file == "/redirect":
                mas_client = http + http_move + conn + "close\n" + location + "\n"
                client.send(bytes(mas_client.encode()))
                not_close = False
                break
            # checking if file is exists
            if not path.exists(folder + path_file):
                mas_client = http + http_not_found + conn + "close\n" + "\n"
                client.send(bytes(mas_client.encode()))
                not_close = False
                break
            if path_file == "/":
                path_file = "/index.html"
            # read the file by bytes,and sent it back.
            with open(folder + path_file, 'rb') as file:
                lines = file.read()
            len_lines = http_len_msg + str(len(lines)) + "\n"
            mas_client = http + http_ok + http_conn_mas + len_lines + "\n"
            client.send(bytes(mas_client.encode() + lines))
        except socket.timeout as e:
            not_close = False
    client.close()
