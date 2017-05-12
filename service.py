import sys
import struct

class primitives:
	def __init__( self, fd ):
		self.fd = fd
		self.words = { }
		self.words[ "reset" ] = self.reset
		self.words[ "set_bg" ] = self.set_bg
		self.words[ "set_fg" ] = self.set_fg
		self.words[ "plot" ] = self.plot
		self.words[ "line" ] = self.line
		self.words[ "cls" ] = self.cls

	def write( self, data ):
		self.fd.write( data )
		self.fd.flush( )

	def reset( self, stack ):
		self.write( struct.pack( "<B", 0 ) )

	def set_bg( self, stack ):
		colour = int( stack.pop( ) )
		self.write( struct.pack( "<BH", 1, colour ) )

	def set_fg( self, stack ):
		colour = int( stack.pop( ) )
		self.write( struct.pack( "<BH", 2, colour ) )

	def plot( self, stack ):
		y = int( stack.pop( ) )
		x = int( stack.pop( ) )
		self.write( struct.pack( "<BHH", 3, x, y ) )

	def line( self, stack ):
		y2 = int( stack.pop( ) )
		x2 = int( stack.pop( ) )
		y1 = int( stack.pop( ) )
		x1 = int( stack.pop( ) )
		self.write( struct.pack( "<BHHHH", 4, x1, y1, x2, y2 ) )

	def cls( self, stack ):
		self.write( struct.pack( "<B", 5 ) )
		
class stack:
	def __init__( self ):
		self.stack = [ ]
		self.grammar = { }

	def register( self, words ):
		self.grammar.update( words )

	def push( self, value ):
		if value in self.grammar:
			self.grammar[ value ]( self.stack )
		elif self.isnumber( value ):
			self.stack.append( value )
		else:
			print >> sys.stderr, "Unrecognised token", value
		return self

	def pop( self ):
		return self.stack.pop( )

	def parse( self, data ):
		for token in data.rstrip( ).split( ):
			self.push( token )

	def isnumber( self, string ):
		try:
			int( string )
			return True
		except:
			return False

fd = open( sys.argv[ 1 ], "w" )

s = stack( )
s.register( primitives( fd ).words )

while True:
	d = sys.stdin.readline( )
	if d == '': break
	s.parse( d )

