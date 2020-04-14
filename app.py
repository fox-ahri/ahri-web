import socket
import re
import multiprocessing
import sys


class WSGIServer(object):

    def __init__(self, setting):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((setting['host'], setting['port']))
        self.server_socket.listen(128)
        self.app = setting['application']

    def set_response_header(self, status, headers):
        self.status = status
        self.headers = headers

    def service_client(self, new_socket):
        request = new_socket.recv(1024).decode('utf-8')
        request_lines = request.splitlines()
        print('=' * 100)
        print(request_lines)

        request_path = ''
        if ret := re.match(r'[^/]+(/[^ ]*)', request_lines[0]):
            request_path = ret.group(1)

        env = dict()
        env['PATH_INFO'] = request_path
        env['REQUEST'] = request_lines

        body = self.app(env, self.set_response_header)

        header = f'HTTP/1.1 {self.status}\r\n'
        for h in self.headers:
            header += f'{h[0]}:{h[1]}\r\n'
        header += '\r\n'

        response = header + body

        new_socket.send(response.encode('utf-8'))

        new_socket.close()

    def run(self):
        try:
            while True:
                new_socket, client_addr = self.server_socket.accept()
                p = multiprocessing.Process(target=self.service_client, args=(new_socket,))
                p.start()
                new_socket.close()
        except KeyboardInterrupt:
            self.server_socket.close()


def main():
    setting = {
        'host': '',
        'port': 3333,
        'package': 'aweb',
        'app': 'application',
        'application': None
    }
    try:
        for i in range(len(sys.argv)):
            if sys.argv[i] == '-c' or sys.argv[i] == '--config':
                with open(sys.argv[i + 1]) as f:
                    for c in (conf := eval(f.read())):
                        setting.update({c: conf[c]})
            elif sys.argv[i] == '-h' or sys.argv[i] == '--host':
                setting.update({'host': sys.argv[i + 1]})
            elif sys.argv[i] == '-p' or sys.argv[i] == '--port':
                setting.update({'port': int(sys.argv[i + 1])})
            elif sys.argv[i] == '-a' or sys.argv[i] == '--app':
                ret = re.match(r'([^:]+):(.*)', sys.argv[i + 1])
                setting.update({'package': ret.group(1)})
                setting.update({'app': ret.group(2)})
    except Exception as e:
        print(e)

    # sys.path.append(setting['package'])
    package = __import__(setting['package'])
    app = getattr(package, setting['app'])
    setting.update({'application': app})

    wsgi_server = WSGIServer(setting)
    wsgi_server.run()


if __name__ == '__main__':
    main()
