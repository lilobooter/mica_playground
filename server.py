#!/usr/bin/env python

import socket
import threading
import sys
import select
import subprocess

p = subprocess.Popen( sys.argv[ 1 : ], stdin = subprocess.PIPE, stdout = subprocess.PIPE )

BIND_IP = '0.0.0.0'
BIND_PORT = 9090

def handle_client(client_socket):
	fd = client_socket.makefile( )
	running = True
	while running:
		( ins, outs, errs ) = select.select( [ fd, p.stdout ], [ ], [ ], 0.5 )
		for io in ins:
			data = io.readline( )
			if data == '':
				running = False
				break
			if io == fd:
				print >> sys.stderr, "RECV:", data,
				print >> p.stdin, data,
				p.stdin.flush( )
			else:
				print >> sys.stderr, "XMIT:", data,
				print >> fd, ">>>", data,
				fd.flush( )
	client_socket.close()

def tcp_server():
	server = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
	server.bind(( BIND_IP, BIND_PORT))
	server.listen(5)
	print >> sys.stderr, "[*] Listening on %s:%d" % (BIND_IP, BIND_PORT)

	while 1:
		result = select.select( [ server ], [ ], [ ], 0.0 )
		if server in result[ 0 ]:
			client, addr = server.accept()
			print >> sys.stderr, "[*] Accepted connection from: %s:%d" %(addr[0], addr[1])
			client_handler = threading.Thread(target=handle_client, args=(client,))
			client_handler.start()

if __name__ == '__main__':
	tcp_server( )
