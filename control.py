#!/usr/bin/env python

import socket
import time
from Tkinter import *

host = '192.168.76.1'
port = 7688
try:  
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(5.0)
	s.connect((host, port))
except socket.error, err:
	print "Caught exception socket.error : " + str(err)
	sys.exit( 0 )
	
# Movement TCP commands definitions

def send( msg ):
	s.sendall( msg + b'\n' )

def leftkey(event = None):
	send( b'left' )

def rightkey(event = None):
	send( b'right' )
	
def backkey(event = None):
	send( b'backward' )

def frontkey(event = None):
	send( b'forward' )
	
def stopkey(event = None):
	send( b'stop' )

def start():	
	main = Tk()
	
	# buttons
	main.wm_title("Robocontroller")
	button_front = Button(main, text="Foward", command=frontkey)
	button_back = Button(main, text="Backwards", command=backkey)
	button_stop = Button(main, text="Stop", command=stopkey)
	button_right = Button(main, text="Turn Right", command=rightkey)
	button_left = Button(main, text="Turn Left", command=leftkey)
	button_front.grid(row =0, column =2)
	button_back.grid(row =2, column =2)
	button_stop.grid(row =1, column =2)
	button_right.grid(row =1, column =3)
	button_left.grid(row =1, column =1)
	
	# key bindings
	main.bind('<Left>', leftkey)
	main.bind('<Right>', rightkey)
	main.bind('<Up>', frontkey)
	main.bind('<Down>', backkey)
	main.bind('<Return>', stopkey)
	main.bind('<Escape>', quit)

	main.wm_attributes("-topmost", 1) # not working on osx
	main.focus_force() # not working on osx
	main.mainloop()

if __name__ == '__main__':
	start( )
