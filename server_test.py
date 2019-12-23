import socket
from dnslib import *
import threading
from pytun import *


class server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 53))
        self.packets = []
        self.tun = TunTapDevice(name='mytun', flags=IFF_TUN)
        self.tun.addr = '10.10.10.2'
        self.tun.dstaddr = '10.10.10.1'
        self.tun.netmask = '255.255.255.0'
        self.tun.mtu = 300

    def packetsRead(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            packet = DNSRecord.parse(data)
            packet.reply()
            self.packets.append((packet, data))
            packet = packet.questions[0]
            print(packet)
            self.tun.write(packet)

    def tunReader(self):
        while True:
            data = self.tun.read(self.tun.mtu)
            query, addr = self.packets[0]
            del self.packets[0]
            packet = query.reply()
            packet.add_answer(RR(query.questions[0], QTYPE.TXT, rdata=data))
            self.sock.sendto(packet.pack(), addr)
