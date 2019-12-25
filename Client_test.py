import socket
import selectors
import pytun
import dns.message
import dns.name
import dns.query
import dns.resolver
import base64

server_domain = 'group-17.cs305.fun'


class client:
    def __init__(self):
        self.tun = pytun.TunTapDevice(name='mytun', flags=pytun.IFF_TUN | pytun.IFF_NO_PI)
        self.tun.addr = '10.10.10.1'
        self.tun.dstaddr = '10.10.10.2'
        self.tun.netmask = '255.255.255.0'
        self.tun.mtu = 70
        self.tun.persist(True)
        self.tun.up()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sel = selectors.DefaultSelector()
        self.sel.register(self.tun, selectors.EVENT_READ, self.tunReader, )
        self.sel.register(self.socket, selectors.EVENT_READ, self.socketReader)

    def dnsAssemble(self, domain):
        packet = dns.message.make_query(domain, 'TXT')
        packet = packet.pack()
        return packet

    def tunReader(self, tun, mask):
        data = tun.read(tun.mtu)
        data = base64.b64encode(data)
        data = str(data, encoding='ascii')
        data = data + '.' + server_domain
        packet = self.dnsAssemble(data)
        self.socket.sendto(packet, ('120.78.166.34', 53))

    def socketReader(self, sock, mask):
        data = sock.recv(1024)
        packet = dns.message.from_wire(data)
        response = packet.answer[0]
        response = base64.b64decode(str(response))
        self.tun.write(response)
        packet = self.dnsAssemble(server_domain)
        self.socket.sendto(packet, ('120.78.166.34', 53))

    def run(self):
        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)


if __name__ == '__main__':
    client = client()
    client.run()
