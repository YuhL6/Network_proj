import socket
import select
import pytun
import base64
import dns.message
import dns.name
import dns.query
import dns.resolver

from queue import LifoQueue

tun = pytun.TunTapDevice(
            name='server_tun', flags=pytun.IFF_TUN | pytun.IFF_NO_PI)
tun.addr = '10.10.10.2'
tun.netmask = '255.255.255.0'
tun.mtu = 160
tun.up()

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind(('', 53))
query_queue = LifoQueue(65532)


def decode_query(data: bytes):
    query_dns_pkt = dns.message.from_wire(data)
    name = str(query_dns_pkt.question[0].name)
    name = name[:-20]
    ip_data = ''.join(name.split('.'))
    write_to_tun_data = base64.b64decode(ip_data)

    return write_to_tun_data, query_dns_pkt


def encode_response(send_to_socket_data: bytes, query_dns_pkt):
    response = dns.message.make_response(
        query_dns_pkt, recursion_available=True)
    response.answer.append(dns.rrset.from_text(
        query_dns_pkt.question[0].name, 30000, 1, 'TXT', str(base64.b64encode(send_to_socket_data), encoding='ascii')))
    return response.to_wire()


def run():
    r = [tun, socket]
    w = []
    e = []
    write_to_tun_data = b''
    send_to_socket_data = b''
    while True:
        readable, writable, exceptional = select.select(r, w, e)
        if tun in readable:
            send_to_socket_data = tun.read(tun.mtu)
        if socket in readable:
            data, addr = socket.recvfrom(65523)
            pair = decode_query(data)
            query_queue.put((pair[1], addr))
            write_to_tun_data = pair[0]
        if tun in writable:
            tun.write(write_to_tun_data)
            write_to_tun_data = ''
        if socket in writable and not query_queue.empty():
            query_dns_pkt, target_addr = query_queue.get()
            socket.sendto(encode_response(send_to_socket_data, query_dns_pkt), target_addr)
            send_to_socket_data = b''
        r = []
        w = []

        if send_to_socket_data:
            w.append(socket)
        else:
            r.append(tun)

        if write_to_tun_data:
            w.append(tun)
        else:
            r.append(socket)
