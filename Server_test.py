import socket
import selectors
import pytun
import dns.message
import dns.name
import dns.query
import dns.resolver
import dns.rrset
import base64


class client:
    def __init__(self):
        self.tun = pytun.TunTapDevice(name='mytun', flags=pytun.IFF_TUN | pytun.IFF_NO_PI)
        self.tun.addr = '10.10.10.2'
        self.tun.dstaddr = '10.10.10.1'
        self.tun.netmask = '255.255.255.0'
        self.tun.mtu = 70
        self.tun.persist(True)
        self.tun.up()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sel = selectors.DefaultSelector()
        self.sel.register(self.tun, selectors.EVENT_READ, self.tunReader, )
        self.sel.register(self.socket, selectors.EVENT_READ, self.socketReader)
        self.pool = []

    def dnsAssemble(self, data):
        question = self.pool[0]
        packet = dns.message.make_response(question, recursion_available=True)
        del self.pool[0]
        packet.answer.append(dns.rrset.from_text(
            question.question[0].name, 30000, 1, 'TXT', str(base64.b64encode(data), encoding='ascii')))
        return packet

    def tunReader(self, tun, mask):
        data = tun.read(tun.mtu)
        data = base64.b64encode(data)
        data = str(data, encoding='ascii')
        packet = self.dnsAssemble(data)
        self.socket.sendto(packet, ('120.78.166.34', 53))

    def socketReader(self, sock, mask):
        data = sock.recv(1024)
        packet = dns.message.from_wire(data)
        domain = str(packet.question[0].name)
        print(domain)
        domain = domain[:-20]
        print(domain)
        self.pool.append(packet)
        data = base64.b64decode(domain)
        self.tun.write(data)

    def run(self):
        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)


if __name__ == '__main__':
    client = client()
    client.run()
