import socket


class server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 53))
        self.packet_id = {}

    def writePacket(self, data):
        pass

    def packetsRead(self):
        packet = ''
        while True:
            data = self.sock.recv(1024).decode()
            packet += data[1:]
            if data[0] == 'x':
                self.writePacket(data)
            elif data[0] == 'y':
                pass

    def cut_data(self, data):
        if len(data) <= 300:
            return [data]
        else:
            li = [data[0:300]]
            data = data[300:]
            while len(data) > 300:
                li.append(data[0:300])
                data = data[300:]
            li.append(data)
            return data

    def packetSend(self, data):
        data = data.decode()
        li = self.cut_data(data)
        for tmp in li:
            self.udpSend(tmp)
        self.count += 1

    def udpSend(self, data):
        prefix = '{} 01 20 00 0100 00 00 00 00 00 0d'.format(hex(self.count))
        domain = '08 67 72 6f 75 70 2d 31 37 0563 73 33 30 35 03 66 75 6e 00 00 0a 00 01'
        msg = prefix + data + domain
        msg = msg.replace(' ', '')
        msg = bytes.fromhex(msg)
        self.sock.sendto(msg, ('120.78.166.34', 53))