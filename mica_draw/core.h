#pragma once

template < class T > inline Print &operator <<( Print &obj, T arg ) { obj.print( arg ); return obj; }

#define UPDATE( NAME )       read( NAME )
#define CREATE( TYPE, NAME ) TYPE NAME; UPDATE( NAME )

namespace core {
  
class base
{
  protected:
    // NB: Read and write assume little endian
    int read( uint8_t &value )
    {
      return Serial.readBytes( &value, sizeof( uint8_t ) );
    }
    
    int read( uint16_t &value )
    {
      return Serial.readBytes( ( uint8_t * )&value, sizeof( uint16_t ) );
    }

    int read( char *text, int len )
    {
      return Serial.readBytes( ( uint8_t * )text, len );
    }

    int write( const uint8_t &value )
    {
      return Serial.write( &value, sizeof( uint8_t ) );
    }

    int write( const uint16_t &value )
    {
      return Serial.write( ( uint8_t * )&value, sizeof( uint16_t ) );
    }
};

}

