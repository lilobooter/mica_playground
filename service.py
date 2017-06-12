import sys
import struct
import select
import random
import math
import time
import shlex

class stack:
	def __init__( self, fd ):
		self.content = [ ]
		self.recipient = None
		self.grammar = { }
		self.fd = fd
		self.inputs = { }
		self.inputs[ self.fd ] = self.incoming
		self.acceptable = [ ]

	def register( self, obj ):
		contents = dir( obj )
		if "words" in contents:
			self.grammar.update( obj.words )
		if "accepted" in contents:
			self.acceptable.append( obj.accepted )
		if "fd" in contents and "incoming" in contents:
			self.inputs[ obj.fd ] = obj.incoming

	def pop( self ):
		return self.content.pop( )

	def push( self, value ):
		def execute( word ):
			if isinstance( word, list ):
				for t in word: self.push( t )
			else:
				word( self )

		if self.recipient is not None:
			self.recipient( self, value )
		elif value in self.grammar:
			execute( self.grammar[ value ] )
		elif self.accepted( value ):
			pass
		else:
			print >> sys.stderr, "Unrecognised token", value
		return self

	def accepted( self, value ):
		for a in self.acceptable:
			try:
				r = a( value )
				if r is not None:
					self.append( r )
					return True
			except:
				pass
		return False

	def append( self, value ):
		self.content.append( value )
		return self

	def parse( self, data ):
		for token in shlex.split( data.rstrip( ) ):
			self.push( token )

	def incoming( self, stack ):
		d = sys.stdin.readline( )
		if d == "": raise EOFError( "EOF" )
		stack.parse( d )

	def run( self ):
		active = select.select( s.inputs, [ ], s.inputs, 0.1 )
		if len( active[ 2 ] ) > 0:
			return False
		for fd in active[ 0 ]:
			if fd in self.inputs:
				self.inputs[ fd ]( self )
		return True

class ints:
	def accepted( self, value ):
		if isinstance( value, int ): return value
		if isinstance( value, float ): return value
		if not isinstance( value, str ): return None
		if value[ 0 : 2 ] == '0x': return int( value, 16 )
		if value[ 0 : 2 ] == '0o': return int( value, 8 )
		if value[ 0 : 2 ] == '0b': return int( value, 2 )
		return int( value )

class floats:
	def accepted( self, value ):
		return float( value )

class arithmetic:
	def __init__( self ):
		def add( stack ):
			a = float( stack.pop( ) )
			b = float( stack.pop( ) )
			stack.append( b + a )

		def subtract( stack ):
			a = float( stack.pop( ) )
			b = float( stack.pop( ) )
			stack.append( b - a )

		def multiply( stack ):
			a = float( stack.pop( ) )
			b = float( stack.pop( ) )
			stack.append( b * a )

		def divide( stack ):
			a = float( stack.pop( ) )
			b = float( stack.pop( ) )
			stack.append( b / a )

		def modulo( stack ):
			a = float( stack.pop( ) )
			b = float( stack.pop( ) )
			stack.append( b % a )

		def raised( stack ):
			a = float( stack.pop( ) )
			b = float( stack.pop( ) )
			stack.append( b ** a )

		self.words = { }
		self.words[ "+" ] = add
		self.words[ "-" ] = subtract
		self.words[ "*" ] = multiply
		self.words[ "/" ] = divide
		self.words[ "%" ] = modulo
		self.words[ "**" ] = raised

		def floor( stack ):
			a = float( stack.pop( ) )
			stack.append( math.floor( a ) )

		def ceil( stack ):
			a = float( stack.pop( ) )
			stack.append( math.ceil( a ) )

		def to_int( stack ):
			a = stack.pop( )
			if isinstance( a, float ):
				a = int( math.floor( a ) )
			elif isinstance( a, str ):
				a = int( math.floor( float( a ) ) )
			else:
				a = int( a )
			stack.append( a )

		def to_float( stack ):
			a = float( stack.pop( ) )
			stack.append( a )

		self.words[ "floor" ] = floor
		self.words[ "ceil" ] = ceil
		self.words[ "int" ] = to_int
		self.words[ "float" ] = to_float

		def left( stack ):
			a = int( stack.pop( ) )
			b = int( stack.pop( ) )
			stack.append( b << a )

		def right( stack ):
			a = int( stack.pop( ) )
			b = int( stack.pop( ) )
			stack.append( b >> a )

		self.words[ "<<" ] = left
		self.words[ ">>" ] = right

class bits:
	def __init__( self ):
		def op_and( stack ):
			a = int( stack.pop( ) )
			b = int( stack.pop( ) )
			stack.append( b & a )

		def op_or( stack ):
			a = int( stack.pop( ) )
			b = int( stack.pop( ) )
			stack.append( b | a )

		def op_xor( stack ):
			a = int( stack.pop( ) )
			b = int( stack.pop( ) )
			stack.append( b ^ a )

		self.words = { }
		self.words[ "&" ] = op_and
		self.words[ "|" ] = op_or
		self.words[ "^" ] = op_xor

class maths:
	def __init__( self ):
		def e( stack ):
			stack.append( math.e )

		def log( stack ):
			a = float( stack.pop( ) )
			stack.append( math.log( a ) )

		def pi( stack ):
			stack.append( math.pi )

		def sin( stack ):
			a = float( stack.pop( ) )
			stack.append( math.sin( a ) )

		def cos( stack ):
			a = float( stack.pop( ) )
			stack.append( math.cos( a ) )

		def tan( stack ):
			a = float( stack.pop( ) )
			stack.append( math.tan( a ) )

		self.words = { }
		self.words[ "e" ] = e
		self.words[ "log" ] = log
		self.words[ "pi" ] = pi
		self.words[ "sin" ] = sin
		self.words[ "cos" ] = cos
		self.words[ "tan" ] = tan

class manipulations:
	def __init__( self ):
		def depth( stack ):
			a = len( stack.content )
			stack.append( a )

		def pick( stack ):
			a = int( stack.pop( ) )
			i = len( stack.content ) - a - 1
			stack.append( stack.content[ i ] )

		def roll( stack ):
			a = int( stack.pop( ) )
			i = len( stack.content ) - a - 1
			stack.content = stack.content[ : i ] + stack.content[ i + 1 : ] + stack.content[ i : i + 1 ]

		def drop( stack ):
			stack.pop( )

		def clear( stack ):
			stack.content = [ ]

		self.words = { }
		self.words[ "depth?" ] = depth
		self.words[ "pick" ] = pick
		self.words[ "roll" ] = roll
		self.words[ "drop" ] = drop
		self.words[ "clear" ] = clear

class string:
	def __init__( self ):
		self.words = { }
		self.words[ "$" ] = self.string

	def string( self, stack ):
		self.state = ""
		stack.recipient = self.cb_string

	def cb_string( self, stack, value ):
		def adjust( value ):
			if self.state != "":
				return self.state + " " + value
			return value

		def quoted( value ):
			return len( value ) != 0 and value[ 0 ] in [ '"', '\'' ]

		def complete( value ):
			if not quoted( value ): return True
			if len( value ) == 1: return False
			return value[ 0 ] == value[ -1 ]

		def clean( value ):
			if quoted( value ):
				return value[ 1 : -1 ]
			return value

		value = adjust( value )
		if complete( value ):
			value = clean( value )
			stack.append( value )
			stack.recipient = None
		else:
 			self.state = value

class word:
	def __init__( self ):
		def word( stack ):
			self.name = None
			self.body = [ ]
			stack.recipient = cb_word

		def cb_word( stack, value ):
			if self.name is None:
				self.name = value
			elif value != ';':
				self.body.append( value )
			else:
				stack.grammar[ self.name ] = self.body
				stack.recipient = None

		self.words = { }
		self.words[ ":" ] = word

class loop:
	def __init__( self ):
		self.loops = [ ]
		self.words = { }
		self.words[ "do" ] = self.do
		self.words[ "i" ] = self.i

	def do( self, stack ):
		lower = float( stack.pop( ) )
		upper = float( stack.pop( ) )
		self.loops.append( [ lower, upper, lower, [ ] ] )
		stack.recipient = self.loop

	def loop( self, stack, value ):
		if value != "loop" and value != "+loop":
			self.loops[ -1 ][ 3 ].append( value )
		else:
			stack.recipient = None
			loop = self.loops[ -1 ]
			while loop[ 2 ] < loop[ 1 ]:
				for token in loop[ 3 ]:
					stack.push( token )
				if value == "loop":
					loop[ 2 ] += 1
				else:
					loop[ 2 ] += float( stack.pop( ) )
			self.loops.pop( )

	def i( self, stack ):
		stack.append( self.loops[ -1 ][ 2 ] )

class clock:
	def __init__( self ):
		def sleep( stack ):
			t = float( stack.pop( ) )
			time.sleep( t )

		def now( stack ):
			stack.append( time.time( ) )

		def tform( stack ):
			form = str( stack.pop( ) )
			now = float( stack.pop( ) )
			stack.append( time.strftime( form, time.localtime( now ) ) )

		self.words = { }
		self.words[ "sleep" ] = sleep
		self.words[ "now" ] = now
		self.words[ "tform" ] = tform

class io:
	def __init__( self, fd = sys.stdout ):
		def output( stack ):
			a = stack.pop( )
			print >> self.fd, a

		def dump( stack ):
			print >> self.fd, "[",
			for item in stack.content:
				print >> self.fd, '"' + str( item ) + '"',
			print >> self.fd, "]"

		self.fd = fd
		self.words = { }
		self.words[ "." ] = output
		self.words[ ".s" ] = dump

class noise:
	def __init__( self ):
		def irnd( stack ):
			a = float( stack.pop( ) ) + 1
			stack.append( int( a * random.random( ) ) )

		self.words = { }
		self.words[ "irnd" ] = irnd

class utils:
	def __init__( self ):
		def help( stack ):
			for word in sorted( stack.grammar ):
				print word,
			print

		self.words = { }
		self.words[ "help" ] = help

class primitives:
	def __init__( self, fd ):
		self.fd = fd
		self.pending = 0
		self.touched = None

		self.words = { }
		self.words[ "noop" ] = self.noop
		self.words[ "reset" ] = self.reset
		self.words[ "bg" ] = self.bg
		self.words[ "fg" ] = self.fg
		self.words[ "plot" ] = self.plot
		self.words[ "line" ] = self.line
		self.words[ "cls" ] = self.cls
		self.words[ "rect" ] = self.rect
		self.words[ "fill" ] = self.fill
		self.words[ "circle" ] = self.circle
		self.words[ "invert" ] = self.invert
		self.words[ "rotate" ] = self.rotate
		self.words[ "triangle" ] = self.triangle
		self.words[ "print" ] = self.text
		self.words[ "at" ] = self.at
		self.words[ "textsize" ] = self.textsize
		self.words[ "sync" ] = self.sync_all

		self.responses = { }
		self.responses[ 0 ] = self.resp_error
		self.responses[ 1 ] = self.resp_ack
		self.responses[ 2 ] = self.resp_touch
		self.responses[ 3 ] = self.resp_release

	def sync( self, stack ):
		while self.pending > 0:
			self.incoming( stack )
		self.pending += 1

	def sync_all( self, stack ):
		while self.pending > 0:
			self.incoming( stack )
		
	def noop( self, stack ):
		self.sync( stack )
		self.write( struct.pack( "<B", 0 ) )

	def reset( self, stack ):
		self.sync( stack )
		self.write( struct.pack( "<B", 1 ) )

	def bg( self, stack ):
		self.sync( stack )
		colour = int( stack.pop( ) )
		self.write( struct.pack( "<BH", 2, colour ) )

	def fg( self, stack ):
		self.sync( stack )
		colour = int( stack.pop( ) )
		self.write( struct.pack( "<BH", 3, colour ) )

	def plot( self, stack ):
		self.sync( stack )
		y = int( stack.pop( ) )
		x = int( stack.pop( ) )
		self.write( struct.pack( "<BHH", 4, x, y ) )

	def line( self, stack ):
		self.sync( stack )
		y2 = int( stack.pop( ) )
		x2 = int( stack.pop( ) )
		y1 = int( stack.pop( ) )
		x1 = int( stack.pop( ) )
		self.write( struct.pack( "<BHHHH", 5, x1, y1, x2, y2 ) )

	def cls( self, stack ):
		self.sync( stack )
		self.write( struct.pack( "<B", 6 ) )

	def rect( self, stack ):
		self.sync( stack )
		y2 = int( stack.pop( ) )
		x2 = int( stack.pop( ) )
		y1 = int( stack.pop( ) )
		x1 = int( stack.pop( ) )
		self.write( struct.pack( "<BHHHH", 7, x1, y1, x2, y2 ) )

	def fill( self, stack ):
		self.sync( stack )
		a = int( stack.pop( ) )
		self.write( struct.pack( "<BB", 8, a ) )

	def circle( self, stack ):
		self.sync( stack )
		r = int( stack.pop( ) )
		y = int( stack.pop( ) )
		x = int( stack.pop( ) )
		self.write( struct.pack( "<BHHH", 16, x, y, r ) )

	def invert( self, stack ):
		self.sync( stack )
		a = int( stack.pop( ) )
		self.write( struct.pack( "<BB", 10, a ) )

	def rotate( self, stack ):
		self.sync( stack )
		a = int( stack.pop( ) )
		self.write( struct.pack( "<BB", 11, a ) )

	def triangle( self, stack ):
		self.sync( stack )
		y3 = int( stack.pop( ) )
		x3 = int( stack.pop( ) )
		y2 = int( stack.pop( ) )
		x2 = int( stack.pop( ) )
		y1 = int( stack.pop( ) )
		x1 = int( stack.pop( ) )
		self.write( struct.pack( "<BHHHHHH", 12, x1, y1, x2, y2, x3, y3 ) )

	def text( self, stack ):
		self.sync( stack )
		a = str( stack.pop( ) )
		self.write( struct.pack( "<BB", 13, len( a ) ) + a )

	def at( self, stack ):
		self.sync( stack )
		y = int( stack.pop( ) )
		x = int( stack.pop( ) )
		self.write( struct.pack( "<BHH", 14, x, y ) )

	def textsize( self, stack ):
		self.sync( stack )
		s = int( stack.pop( ) )
		self.write( struct.pack( "<BH", 15, s ) )

	def incoming( self, stack ):
		pattern = "<B"
		( op, ) = struct.unpack( pattern, self.read( struct.calcsize( pattern ) ) )
		if op in self.responses:
			self.responses[ op ]( stack )
		else:
			print >> sys.stderr, "unrecognised response:", op

	def resp_error( self, stack ):
		print >> sys.stderr, "unknown error"

	def resp_ack( self, stack ):
		pattern = "<B"
		( op, ) = struct.unpack( pattern, self.read( struct.calcsize( pattern ) ) )
		self.pending -= 1
		print >> sys.stderr, "operation complete:", int( op ), "pending:", self.pending

	def resp_touch( self, stack ):
		pattern = "<HHH"
		( x, y, z ) = struct.unpack( pattern, self.read( struct.calcsize( pattern ) ) )
		print "touch at", x, y, z
		#if self.touched is None:
		#	stack.push( x ).push( y ).push( "plot" )
		#else:
		#	x1, y1, z1 = self.touched
		#	if x1 != x or y1 != y:
		#		stack.push( x ).push( y ).push( x1 ).push( y1 ).push( "line" )
		self.touched = ( x, y, z )

	def resp_release( self, stack ):
		self.touched = None
		print "release"

	def write( self, data ):
		self.fd.write( data )
		self.fd.flush( )

	def read( self, size ):
		return self.fd.read( size )

class servos:
	def __init__( self, fd ):
		self.fd = fd
		self.pending = 0
		self.touched = None

		self.words = { }
		self.words[ "noop" ] = self.noop
		self.words[ "reset" ] = self.reset
		self.words[ "connect" ] = self.connect
		self.words[ "range" ] = self.range
		self.words[ "turn" ] = self.turn
		self.words[ "absolute" ] = self.absolute

		self.responses = { }
		self.responses[ 0 ] = self.resp_error
		self.responses[ 1 ] = self.resp_ack
		self.responses[ 2 ] = self.resp_debug

	def sync( self, stack ):
		while self.pending > 8:
			self.incoming( stack )
		self.pending += 1

	def noop( self, stack ):
		self.sync( stack )
		self.write( struct.pack( "<B", 0 ) )

	def reset( self, stack ):
		self.sync( stack )
		self.write( struct.pack( "<B", 1 ) )

	def connect( self, stack ):
		self.sync( stack )
		unit = int( stack.pop( ) )
		pin = int( stack.pop( ) )
		self.write( struct.pack( "<BHH", 2, unit, pin ) )

	def range( self, stack ):
		self.sync( stack )
		unit = int( stack.pop( ) )
		upper = int( stack.pop( ) )
		lower = int( stack.pop( ) )
		self.write( struct.pack( "<BHHH", 3, unit, lower, upper ) )

	def turn( self, stack ):
		self.sync( stack )
		unit = int( stack.pop( ) )
		position = int( float( stack.pop( ) ) * 0xffff )
		self.write( struct.pack( "<BHH", 4, unit, position ) )

	def absolute( self, stack ):
		self.sync( stack )
		unit = int( stack.pop( ) )
		position = int( stack.pop( ) )
		self.write( struct.pack( "<BHH", 5, unit, position ) )

	def incoming( self, stack ):
		pattern = "<B"
		( op, ) = struct.unpack( pattern, self.read( struct.calcsize( pattern ) ) )
		if op in self.responses:
			self.responses[ op ]( stack )
		else:
			print >> sys.stderr, "unrecognised response:", op

	def resp_error( self, stack ):
		print >> sys.stderr, "unknown error"

	def resp_ack( self, stack ):
		pattern = "<B"
		( op, ) = struct.unpack( pattern, self.read( struct.calcsize( pattern ) ) )
		self.pending -= 1
		print >> sys.stderr, "operation complete:", int( op )

	def resp_debug( self, stack ):
		print "debug:", self.fd.readline( ),

	def write( self, data ):
		self.fd.write( data )
		self.fd.flush( )

	def read( self, size ):
		return self.fd.read( size )

s = stack( sys.stdin )
s.register( ints( ) )
s.register( floats( ) )
s.register( arithmetic( ) )
s.register( bits( ) )
s.register( maths( ) )
s.register( manipulations( ) )
s.register( string( ) )
s.register( word( ) )
s.register( loop( ) )
s.register( clock( ) )
s.register( io( ) )
s.register( noise( ) )
s.register( utils( ) )

if len( sys.argv ) > 2 and sys.argv[ 1 ] == "lcd":
	fd = open( sys.argv[ 2 ], "r+" )
	s.register( primitives( fd ) )
elif len( sys.argv ) > 2 and sys.argv[ 1 ] == "servos":
	fd = open( sys.argv[ 2 ], "r+" )
	s.register( servos( fd ) )

while True:
	try:
		s.run( )
		sys.stdout.flush( )
	except EOFError, e:
		break
	except Exception, e:
		print "ERR: ", e
