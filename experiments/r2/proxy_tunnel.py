"""Per-command SSH CONNECT tunnel through the already running local proxy."""
import os,select,socket,sys
sock=socket.create_connection(('127.0.0.1',7890),timeout=15)
target=sys.argv[1]+':'+sys.argv[2]
sock.sendall(('CONNECT '+target+' HTTP/1.1\r\nHost: '+target+'\r\n\r\n').encode())
header=b''
while b'\r\n\r\n' not in header:
    header+=sock.recv(1)
    if len(header)>16000:raise RuntimeError('proxy response too long')
if b' 200 ' not in header.split(b'\r\n')[0]:raise RuntimeError('proxy CONNECT failed')
sock.settimeout(None)
while True:
    ready,_,_=select.select([sock,sys.stdin.buffer],[],[])
    if sock in ready:
        data=sock.recv(65536)
        if not data:break
        sys.stdout.buffer.write(data);sys.stdout.buffer.flush()
    if sys.stdin.buffer in ready:
        data=os.read(sys.stdin.fileno(),65536)
        if not data:break
        sock.sendall(data)
