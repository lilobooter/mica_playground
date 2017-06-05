import socket
import threading
import sys
import select

BIND_IP = '0.0.0.0'
BIND_PORT = 9090

def handle_client(client_socket):
    fd = client_socket.makefile( )
    while 1:
        request = fd.readline( )
        if len( request ) == 0: break
	print >> sys.stderr, "RECV:", request,
        print request, 
        fd.write( "OK\n" )
	fd.flush( )
	sys.stdout.flush( )
    print >> sys.stderr, "SHUT"
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
    tcp_server()
