#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust, and Warren Lim
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        headers = self.get_headers(data)
        code = headers[0].split(" ")
        return int(code[1])

    def get_headers(self, data):
        data = data.splitlines()
        return data[:data.index("")]

    def get_body(self, data):
        data = data.splitlines()
        data = data[data.index(""):]
        return ''.join(x for x in data)

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')
    
    def parse_url(self, url):
        parsedUrl = urllib.parse.urlsplit(url)
        path = parsedUrl.path
        host = parsedUrl.hostname
        port = parsedUrl.port
        
        if not port: port = 80
        if not path: path = "/"
        return path, host, port
    
    def GET(self, url, args=None):
        path, host, port = self.parse_url(url)
        
        self.connect(host, port)

        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n\r\n"
        print(request)

        self.sendall(request)

        self.socket.shutdown(socket.SHUT_WR)

        response = self.recvall(self.socket)
        self.close()

        print(response)
        
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        path, host, port = self.parse_url(url)
        self.connect(host, port)

        if type(args) is dict:
            encoded_args = ""
            for key in args:
                value = args[key]
                if encoded_args == "":
                    encoded_args += f"{key}={value}"
                else:
                    encoded_args += f"&{key}={value}"
            args = encoded_args
        request = f"POST {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {len(str(args))}\r\n\r\n{args}\r\n\r\n"
        print("THE REQUEST IS:\r\n" + request)

        self.sendall(request)

        self.socket.shutdown(socket.SHUT_WR)

        response = self.recvall(self.socket)
        self.close()

        print("THE RESPONSE IS:\r\n" + response)
        
        code = self.get_code(response)
        body = self.get_body(response)
        print(code, body)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
