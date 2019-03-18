// ILI9341 example with embedded color bitmaps in sketch.
// WILL NOT FIT ON ARDUINO UNO OR OTHER AVR BOARDS;
// uses large bitmap image stored in array!

// Options for converting images to the format used here include:
//   http://www.rinkydinkelectronics.com/t_imageconverter565.php
// or
//  GIMP (https://www.gimp.org/) as follows:
//    1. File -> Export As
//    2. In Export Image dialog, use 'C source code (*.c)' as filetype.
//    3. Press export to get the export options dialog.
//    4. Type the desired variable name into the 'prefixed name' box.
//    5. Uncheck 'GLIB types (guint8*)'
//    6. Check 'Save as RGB565 (16-bit)'
//    7. Press export to save your image.
//  Assuming 'image_name' was typed in the 'prefixed name' box of step 4,
//  you can have to include the c file, then using the image can be done with:
//    tft.drawRGBBitmap(0, 0, image_name.pixel_data, image_name.width, image_name.height);
//  See also https://forum.pjrc.com/threads/35575-Export-for-ILI9341_t3-with-GIMP

#include "SPI.h"
#include <Adafruit_ILI9341.h>
#include "dragon.h"

// For the Adafruit shield, these are the default.
//#define TFT_DC 9
//#define TFT_CS 10

// Feather 32u4 or M0 with TFT FeatherWing:
//#define TFT_DC 10
//#define TFT_CS  9
// ESP8266:
#define TFT_DC 15
#define TFT_CS 0
// Other boards (including Feather boards) may have other pinouts;
// see learn.adafruit.com/adafruit-2-4-tft-touch-screen-featherwing/pinouts

Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC);
// If using the breakout, change pins as desired
//Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC, TFT_MOSI, TFT_CLK, TFT_RST, TFT_MISO);

//int incomingByte = 0;
#define W 320
#define H 10

uint8_t dataBitmap[W*H*2]; 

void setup() {
  tft.begin();
  Serial.begin(3000000);
  //Serial.begin(115200);
  tft.setRotation(3);
  tft.fillScreen(ILI9341_BLACK);
  //pinMode(2, OUTPUT);
  //digitalWrite(2, LOW);
  Serial.setTimeout(2);

}

void __loop(void) {
    if (0 || Serial.available() > 0) {
      //for (int i=0;i<W*H*2;i++) dataBitmap[i] = Serial.read();
      Serial.readBytes(dataBitmap,W*H*2);
      //Serial.readByes(dataBitmap,10);
      //digitalWrite(2, LOW);
      tft.drawRGBBitmap(
          0,0,
         (uint16_t*)dataBitmap,
      W, H);
      //tft.drawRGBBitmap(
      //    0,0,
      //    dragonBitmap,
      //    DRAGON_WIDTH, DRAGON_HEIGHT);
      //delay(1000); // Allow ESP8266 to handle watchdog & WiFi stuff
      //digitalWrite(LED_BUILTIN, HIGH);
    }
    delay(1); // Allow ESP8266 to handle watchdog & WiFi stuff
}

void loop(void) {
    int ibyte;
    while (1 ) {
      if (Serial.available() == 0) delay(1);
      else {
        ibyte=Serial.read();
        if (ibyte=='\xa5') {
          ibyte=Serial.read();
          if (ibyte=='\xa5') break;
        }
      }
    }
    ibyte = Serial.read();
    if (ibyte>=0) {
      Serial.readBytes(dataBitmap,W*H*2);
      tft.drawRGBBitmap(
          0,H*ibyte,
         (uint16_t*)dataBitmap,
      W, H);     
    }
    delay(1); // Allow ESP8266 to handle watchdog & WiFi stuff
}

void loop3(void) {
    int ibyte;
    while (1 ) {
      if (Serial.available() == 0) delay(1);
      else {
        ibyte=Serial.read();
        if (ibyte=='\xa5') {
          ibyte=Serial.read();
          if (ibyte=='\xa5') break;
        }
      }
    }
    
    drawRGBBitmapSer();
    delay(1); // Allow ESP8266 to handle watchdog & WiFi stuff
}

void drawRGBBitmapSer() {
    uint16_t pixel;
    tft.startWrite();
    for(int16_t j=0; j<H; j++) {
        for(int16_t i=0; i<W; i++ ) {
            //if (Serial.readBytes((char*)&pixel,2)!=2){
            //  tft.endWrite();
            //  return;
            //}
            pixel=Serial.read()*256+Serial.read();
            tft.writePixel(i, j, pixel);
        }
    }
    tft.endWrite();
}
