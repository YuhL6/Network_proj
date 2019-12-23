import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
msg = '0064 01 20 00 0100 00 00 00 00 00'
x = '0d6400787776767672757575747474'
rest = '08 67 72 6f 75 70 2d 31 37 0563 73 33 30 35 03 66 75 6e 00 00 0a 00 01'
msg = msg + x + rest
# msg += x
msg = msg.replace(' ', '')
msg = bytes.fromhex(msg)
print(msg)
sock.sendto(msg, ('120.78.166.34', 53))
msg = sock.recv(1024)
print(msg)
print(msg.hex())