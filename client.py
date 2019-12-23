import socket


class client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.count = 100
        self.id = 0

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
        data = input()
        print(data)
        li = self.cut_data(data)
        order = 0
        for tmp in li:
            if tmp == li[-1]:
                self.udpSend(tmp, order, True)
            else:
                self.udpSend(tmp, order, False)
            order += 1
        self.id += 1

    def udpSend(self, data, order, isLastPacket):
        count = '{}'.format(hex(self.count))
        count = count.replace('0x', '')
        while len(count) < 4:
            count = '0' + count
        if count == 'ffff':
            self.count = 0
        prefix = '{} 01 20 00 0100 00 00 00 00 00 0d'.format(count)
        id = '7{}'.format(hex(order))
        id = id.replace('0x', '')
        identifier = '{} {}'.format(id, '78' if isLastPacket else '77')
        data = identifier + data
        print(data)
        domain = '08 67 72 6f 75 70 2d 31 37 0563 73 33 30 35 03 66 75 6e 00 00 0a 00 01'
        msg = prefix + data + domain
        msg = msg.replace('0x', '')
        msg = msg.replace(' ', '')
        msg = bytes.fromhex(msg)
        print(msg)
        self.sock.sendto(msg, ('120.78.166.34', 53))
        self.count += 1


if __name__ == '__main__':
    client = client()
    s = ''
    client.packetSend(s)
