#pragma once

#include <Servo.h>
#include "core.h"

namespace mica_servo {

struct servo_type
{
  servo_type( )
  : pin( -1 )
  , lower( 0 )
  , upper( 180 )
  {
  }
  
  Servo servo;
  int pin;
  int lower;
  int upper;
};

#define SERVOS  12

servo_type servos[ SERVOS ];

#define OPERATIONS 6

class parser : protected core::base
{
  public:
    parser( )
    {
      dictionary[ 0 ] = &parser::noop;
      dictionary[ 1 ] = &parser::reset;
      dictionary[ 2 ] = &parser::connect;
      dictionary[ 3 ] = &parser::range;
      dictionary[ 4 ] = &parser::turn;
      dictionary[ 5 ] = &parser::absolute;
    }

    void setup( ) 
    {
      Serial.begin( BAUD_RATE );
    }

    void loop( )
    {
      while ( Serial.available( ) )
      {
        CREATE( uint8_t, op );
        lookup( op );
      }
    }

  protected:
    void debug( const String &s )
    {
      Serial.write( uint8_t( 2 ) );
      Serial.println( s );
    }
    
    void noop( )
    {
    }
    
    void reset( )
    {
      for( int i = 0; i < SERVOS; i ++ )
      {
        if ( servos[ i ].servo.attached( ) )
          servos[ i ].servo.detach( );
        servos[ i ].pin = -1;
        servos[ i ].lower = 0;
        servos[ i ].upper = 180;
      }
    }
    
    void connect( )
    {
      CREATE( uint16_t, unit );
      CREATE( uint16_t, pin );
      
      if ( unit < SERVOS )
      {
        servos[ unit ].pin = pin;
        if ( servos[ unit ].servo.attached( ) )
          servos[ unit ].servo.detach( );
        servos[ unit ].servo.attach( pin );
      }
    }
    
    void absolute( )
    {
      CREATE( uint16_t, unit );
      CREATE( uint16_t, position );
      if ( unit < SERVOS )
      {
        servos[ unit ].servo.write( position );
      }
    }
    
    void range( )
    {
      CREATE( uint16_t, unit );
      CREATE( uint16_t, lower );
      CREATE( uint16_t, upper );
      if ( unit < SERVOS )
      {
        servos[ unit ].lower = lower;
        servos[ unit ].upper = upper;
      }
    }
    
    void turn( )
    {
      CREATE( uint16_t, unit );
      CREATE( uint16_t, position );
      if ( unit < SERVOS )
      {
        int value = map( position, 0, 0xffff, servos[ unit ].lower, servos[ unit ].upper );
        servos[ unit ].servo.write( value );
      }
    }

  private:
    void lookup( uint8_t op )
    {
      if ( op < OPERATIONS )
      {
        ( this ->* dictionary[ op ] )( );
        write( uint8_t( 0x01 ) );
        write( op );
      }
    }

    typedef void ( parser::*entry )( );
    entry dictionary[ OPERATIONS ];
};

}

