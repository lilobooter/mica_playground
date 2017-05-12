#pragma once

#define YP A3  // must be an analog pin, use "An" notation!
#define XM A2 // must be an analog pin, use "An" notation!
#define YM 9   // can be a digital pin
#define XP 8   // can be a digital pin

#define LCD_CS A3
#define LCD_CD A2
#define LCD_WR A1
#define LCD_RD A0
#define LCD_RESET A4

// Callibration settings
#define DEFAULT_TS_MINX 140
#define DEFAULT_TS_MINY 96
#define DEFAULT_TS_MAXX 965
#define DEFAULT_TS_MAXY 875

#define BAUD_RATE 57600
