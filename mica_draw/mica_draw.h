#pragma once

#include <SPFD5408_Adafruit_GFX.h>    // Core graphics library
#include <SPFD5408_Adafruit_TFTLCD.h> // Hardware-specific library
#include <SPFD5408_TouchScreen.h>

#include "mica_arduino.h"

namespace mica_draw {
  
template < class T > inline Print &operator <<( Print &obj, T arg ) { obj.print(arg); return obj; }

#define OPERATIONS 6

class parser
{
  public:
    parser( )
    : ts( XP, YP, XM, YM, 300 )
    , tft( LCD_CS, LCD_CD, LCD_WR, LCD_RD, LCD_RESET )
    {
      reset( );
      
      dictionary[ 0 ] = &parser::reset;
      dictionary[ 1 ] = &parser::set_bg;
      dictionary[ 2 ] = &parser::set_fg;
      dictionary[ 3 ] = &parser::plot;
      dictionary[ 4 ] = &parser::line;
      dictionary[ 5 ] = &parser::cls;
    }

    void setup( ) 
    {
      Serial.begin( BAUD_RATE );
      tft.reset( );
      uint16_t id = tft.readID( );
      tft.begin( id );
      tft.setRotation( 0 );
      tft.fillScreen( 0x0000 );
    }

    void loop( )
    {
      monitor_touch( );
      
      while ( Serial.available( ) )
      {
        uint8_t op;
        read( op );
        Serial << "received: " << int( op ) << "\r\n";
        lookup( op );
      }
    }

  protected:
    void reset( )
    {
      // Callibration settings
      TS_MINX = DEFAULT_TS_MINX;
      TS_MINY = DEFAULT_TS_MINY;
      TS_MAXX = DEFAULT_TS_MAXX;
      TS_MAXY = DEFAULT_TS_MAXY;

      // Pressure settings
      MINPRESSURE = 10;
      MAXPRESSURE = 1000;

      // Foreground/background state  
      BG = 0x0000;
      FG = 0xffff;

      tft.fillScreen( BG );
    }
    
    void set_bg( )
    {
      read( BG );
    }
    
    void set_fg( )
    {
      read( FG );
    }
    
    void plot( )
    {
      uint16_t x, y;
      read( x );
      read( y );
      tft.drawPixel( x, y, FG );
    }
    
    void line( )
    {
      uint16_t x1, y1, x2, y2;
      read( x1 );
      read( y1 );
      read( x2 );
      read( y2 );
      tft.drawLine( x1, y1, x2, y2, FG );
    }

    void cls( )
    {
      tft.fillScreen( BG );
    }
    
  private:
    // NB: Read and write assume little endian
    int read( uint8_t &value )
    {
      return Serial.readBytes( &value, sizeof( uint8_t ) );
    }
    
    int read( uint16_t &value )
    {
      return Serial.readBytes( ( uint8_t * )&value, sizeof( uint16_t ) );
    }

    int write( const uint8_t &value )
    {
      return Serial.write( &value, sizeof( uint8_t ) );
    }

    int write( const uint16_t &value )
    {
      return Serial.write( ( uint8_t * )&value, sizeof( uint16_t ) );
    }
    
    void lookup( uint8_t op )
    {
      if ( op < OPERATIONS )
        ( this ->* dictionary[ op ] )( );
    }

    void monitor_touch( )
    {  
      TSPoint p = ts.getPoint( );
    
      // if sharing pins, you'll need to fix the directions of the touchscreen pins
      pinMode( XP, OUTPUT );
      pinMode( XM, OUTPUT );
      pinMode( YP, OUTPUT );
      pinMode( YM, OUTPUT );
    
      if ( Serial.availableForWrite( ) > 8 && p.z > MINPRESSURE && p.z < MAXPRESSURE ) 
      {
        write( uint16_t( 0 ) );
        write( uint16_t( p.x ) );
        write( uint16_t( p.y ) );
        write( uint16_t( p.z ) );
      }
    }

    typedef void ( parser::*entry )( );
    entry dictionary[ OPERATIONS ];

    TouchScreen ts;
    Adafruit_TFTLCD tft;
    
    // Callibration settings
    uint16_t TS_MINX;
    uint16_t TS_MINY;
    uint16_t TS_MAXX;
    uint16_t TS_MAXY;

    // Pressure settings
    uint16_t MINPRESSURE;
    uint16_t MAXPRESSURE;

    // Foreground/background state
    uint16_t BG;
    uint16_t FG;
};

}

