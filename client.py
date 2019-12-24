

import socket
import select





import pytun
import dns.message
import dns.name
import dns.query



import base64 as coder
import time
import queue


local_addr = '10.20.0.1'
dst_addr = '10.20.0.2'
local_mask = '255.255.255.0'
remote_dns_addr = '120.78.166.34'
# remote_dns_addr = '52.82.37.174'





remote_dns_port = 53
mtu = 130
query_root_name = 'group-30.cs305.fun'
label_len = 63


class client_tun:
    def __init__(self):
        self._tun = pytun.TunTapDevice(
            name='mytun', flags=pytun.IFF_TUN | pytun.IFF_NO_PI)
        self._tun.addr = local_addr
        self._tun.dstaddr = dst_addr
        self._tun.netmask = local_mask
        self._tun.mtu = mtu
        self._tun.persist(True)
        self._tun.up()
        self.speed = 0.8
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.status=0
        self.sta=0

    def run(self):
        mtu = self._tun.mtu
        r = [self._tun, self._socket]
        w = []
        x = []
        data_out = b''
        data_to_socket = b''
        last_blank = time.time()
        while True:
            # print(1)
            r, w, x = select.select(r, w, x)
            if self._tun in r:
                data_to_socket = self._tun.read(mtu)
            if self._socket in r:
                self.sta=time.time()
                self.status=1
                data_out, target_addr = self._socket.recvfrom(65532)
                dns_response = dns.message.from_wire(data_out)
                if dns_response.answer:
                    txt_record = dns_response.answer[0]
                    data_out = coder.b64decode(str(txt_record.items[0]))
                else:
                    data_out = b''

            if self._tun in w :

                self._tun.write(data_out)
                data_out = b''
            if self._socket in w or (time.time()-self.sta)>0.1:
                encoded_data_to_socket = coder.b64encode(data_to_socket)
                split_labels = [str(encoded_data_to_socket[i:i + label_len], encoding='ascii')
                                for i in range(0, len(encoded_data_to_socket), label_len)]
                split_labels.append(query_root_name)
                target_domain = '.'.join(split_labels)
                name = dns.name.from_text(target_domain)
                query = dns.message.make_query(name, 'TXT')
                self._socket.sendto(
                    query.to_wire(), (remote_dns_addr, remote_dns_port))
                data_to_socket = b''

            r = []
            w = []
            self.status=0
            if data_out:
                w.append(self._tun)
            else:
                r.append(self._socket)
            if not data_to_socket:
                r.append(self._tun)
            now = time.time()
            print(now - last_blank)
            if now - last_blank > self.speed or data_to_socket:
                print(data_to_socket)
                w.append(self._socket)
                last_blank = now


if __name__ == '__main__':
    server = client_tun()

    server.run()
