#pragma once

#include "core.h"

#include <SPFD5408_Adafruit_GFX.h>    // Core graphics library
#include <SPFD5408_Adafruit_TFTLCD.h> // Hardware-specific library
#include <SPFD5408_TouchScreen.h>

#include "mica_arduino.h"

namespace mica_draw {

#define OPERATIONS 17

class parser : protected core::base
{
  public:
    parser( )
    : ts( XP, YP, XM, YM, 300 )
    , tft( LCD_CS, LCD_CD, LCD_WR, LCD_RD, LCD_RESET )
    {
      reset( );

      dictionary[ 0 ] = &parser::ping;
      dictionary[ 1 ] = &parser::reset;
      dictionary[ 2 ] = &parser::bg;
      dictionary[ 3 ] = &parser::fg;
      dictionary[ 4 ] = &parser::plot;
      dictionary[ 5 ] = &parser::line;
      dictionary[ 6 ] = &parser::cls;
      dictionary[ 7 ] = &parser::rect;
      dictionary[ 8 ] = &parser::fill;
      dictionary[ 9 ] = &parser::circle;
      dictionary[ 10 ] = &parser::invert;
      dictionary[ 11 ] = &parser::rotate;
      dictionary[ 12 ] = &parser::triangle;
      dictionary[ 13 ] = &parser::text;
      dictionary[ 14 ] = &parser::at;
      dictionary[ 15 ] = &parser::textsize;
      dictionary[ 16 ] = &parser::circle;
    }

    void setup( ) 
    {
      Serial.begin( BAUD_RATE );
      tft.reset( );
      uint16_t id = tft.readID( );
      tft.begin( id );
      tft.fillScreen( 0x0000 );
    }

    void loop( )
    {
      monitor_touch( );
      
      while ( Serial.available( ) )
      {
        uint8_t op;
        read( op );
        lookup( op );
      }
    }

  protected:
    void ping( )
    {
    }
    
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

      // Turn fill off
      FILL = 0x00;

      tft.setCursor( 0, 0 );
      tft.setTextColor( FG, BG );
      tft.setTextSize( 1 );
      tft.setTextWrap( true );

      touched = 0;
    }
    
    void bg( )
    {
      UPDATE( BG );
      tft.setTextColor( FG, BG );
    }
    
    void fg( )
    {
      UPDATE( FG );
      tft.setTextColor( FG, BG );
    }
    
    void plot( )
    {
      CREATE( uint16_t, x );
      CREATE( uint16_t, y );
      tft.drawPixel( x, y, FG );
    }
    
    void line( )
    {
      CREATE( uint16_t, x1 );
      CREATE( uint16_t, y1 );
      CREATE( uint16_t, x2 );
      CREATE( uint16_t, y2 );
      tft.drawLine( x1, y1, x2, y2, FG );
    }

    void cls( )
    {
      tft.fillScreen( BG );
      tft.setCursor( 0, 0 );
    }
    
    void fill( )
    {
      UPDATE( FILL );
    }

    void rect( )
    {
      CREATE( uint16_t, x );
      CREATE( uint16_t, y );
      CREATE( uint16_t, w );
      CREATE( uint16_t, h );
      if ( FILL == 0 )
        tft.drawRect( x, y, w, h, FG );
      else
        tft.fillRect( x, y, w, h, FG );
    }

    void circle( )
    {
      CREATE( uint16_t, x );
      CREATE( uint16_t, y );
      CREATE( uint16_t, r );
      if ( FILL == 0 )
        tft.drawCircle( x, y, r, FG );
      else
        tft.fillCircle( x, y, r, FG );     
    }
    
    void invert( )
    {
      CREATE( uint8_t, i );
      tft.invertDisplay( i != 0 );     
    }

    void rotate( )
    {
      CREATE( uint8_t, r );
      tft.setRotation( r );     
    }
    
    void triangle( )
    {
      CREATE( uint16_t, x1 );
      CREATE( uint16_t, y1 );
      CREATE( uint16_t, x2 );
      CREATE( uint16_t, y2 );
      CREATE( uint16_t, x3 );
      CREATE( uint16_t, y3 );

      if ( FILL == 0 )
        tft.drawTriangle( x1, y1, x2, y2, x3, y3, FG );
      else
        tft.fillTriangle( x1, y1, x2, y2, x3, y3, FG );
    }

    void text( )
    {
      uint8_t len;
      char data[ 256 ];
      read( len );
      read( data, len );
      data[ len ] = 0;
      tft << data;
    }

    void at( )
    {
      CREATE( uint16_t, x );
      CREATE( uint16_t, y );
      tft.setCursor( x, y );
    }
    
    void textsize( )
    {
      CREATE( uint8_t, s );
      tft.setTextSize( s );
    }

    void monitor_touch( )
    {
      TSPoint p = ts.getPoint( );
    
      // if sharing pins, you'll need to fix the directions of the touchscreen pins
      pinMode( XP, OUTPUT );
      pinMode( XM, OUTPUT );
      pinMode( YP, OUTPUT );
      pinMode( YM, OUTPUT );
    
      if ( touched < 900 && p.z > MINPRESSURE && p.z < MAXPRESSURE ) 
      {
        touched = 1000;
        write( uint8_t( 0x02 ) );
        write( uint16_t( map( p.x, TS_MINX, TS_MAXX, 0, tft.width( ) ) ) );
        write( uint16_t( map( p.y, TS_MINY, TS_MAXY, 0, tft.height( ) ) ) );
        write( uint16_t( p.z ) );
      }
      else if ( touched > 0 )
      {
        if ( -- touched == 0 ) write( uint8_t( 0x03 ) );
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

    // Fill
    uint8_t FILL;

    // State for touch
    int touched;
};

}

