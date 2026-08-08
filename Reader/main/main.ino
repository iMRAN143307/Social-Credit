#include <LovyanGFX.hpp>
#include <lvgl.h>

#include <MFRC522.h>
#include <SPI.h>


#define LV_CONF_SKIP 1
#define LV_USE_STDLIB_MALLOC 1
#define LV_COLOR_DEPTH 16

#define CLK 7
#define MISO 5
#define MOSI 6
#define CS_LCD 10
#define CS_READER 15
#define RST_LCD 13
#define RST_READER 4
#define DC_LCD 9

lv_obj_t *textbox;

MFRC522 rfid(CS_READER, RST_READER);

// Init array that will store new NUID 
byte nuidPICC[4];

// Setup the custom LovyanGFX configuration class for ST7735 128x160
class LGFX : public lgfx::LGFX_Device {
  lgfx::Panel_ST7735S _panel_instance;
  lgfx::Bus_SPI _bus_instance;

public:
  LGFX(void) {
    {
      auto cfg = _bus_instance.config();
      cfg.spi_host = SPI2_HOST;  // Use ESP32-S3 Hardware SPI2
      cfg.spi_mode = 0;
      cfg.freq_write = 27000000;  // 27MHz transmission rate
      cfg.pin_sclk = CLK;         // Move away from 6-11 flash safety zone
      cfg.pin_mosi = MOSI;
      cfg.pin_miso = MISO;
      cfg.pin_dc = DC_LCD;

      _bus_instance.config(cfg);
      _panel_instance.setBus(&_bus_instance);
    }
    {
      auto cfg = _panel_instance.config();
      cfg.pin_cs = CS_LCD;
      cfg.pin_rst = RST_LCD;
      cfg.panel_width = 128;
      cfg.panel_height = 160;
      cfg.offset_x = 0;
      cfg.offset_y = 0;
      cfg.invert = false;    // Hardware-level color inversion (Fixes photo-negative text)
      cfg.rgb_order = true;  // Forces BGR layout (Fixes the weird purple text shift)

      cfg.bus_shared = true;

      _panel_instance.config(cfg);
    }
    setPanel(&_panel_instance);
  }
};

LGFX tft;  // Create the safe display driver object container

#define TFT_HOR_RES 128
#define TFT_VER_RES 160
#define DRAW_BUF_SIZE (TFT_HOR_RES * TFT_VER_RES * 2 / 10)  // Size in bytes (1/10th display)

uint8_t *draw_buf;  // Create a pointer to allocate via heap dynamic memory

void my_disp_flush(lv_display_t *disp, const lv_area_t *area, uint8_t *px_map) {
  uint32_t w = (area->x2 - area->x1 + 1);
  uint32_t h = (area->y2 - area->y1 + 1);

  tft.startWrite();
  tft.setAddrWindow(area->x1, area->y1, w, h);
  tft.writePixels((uint16_t *)px_map, w * h);
  tft.endWrite();

  lv_display_flush_ready(disp);
}

static uint32_t my_tick(void) {
  return millis();
}

void setup() {
  Serial.begin(115200);
  while (!Serial)
    ;

  pinMode(CS_LCD, OUTPUT);

  SPI.begin(CLK, MISO, MOSI, CS_READER);
  rfid.PCD_Init();
  delay(4);
  rfid.PCD_DumpVersionToSerial();
  Serial.println("Ready to scan");

  tft.init();
  tft.setRotation(0);
  tft.fillScreen(TFT_BLUE);
  tft.setSwapBytes(true);

  lv_init();
  Serial.println("LVGL initialized");
  lv_tick_set_cb(my_tick);

  draw_buf = (uint8_t *)heap_caps_malloc(DRAW_BUF_SIZE, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
  if (draw_buf == NULL) {
    Serial.println("ERROR: No drawing buffer");
    while (1) delay(100);
  }

  lv_display_t *disp = lv_display_create(TFT_HOR_RES, TFT_VER_RES);
  if (disp == NULL) {
    Serial.println("ERROR: Display is null");
    while (1) delay(100);
  }

  lv_display_set_flush_cb(disp, my_disp_flush);
  lv_display_set_buffers(disp, draw_buf, NULL, DRAW_BUF_SIZE, LV_DISPLAY_RENDER_MODE_PARTIAL);

  lv_obj_t *scr = lv_screen_active();
  if (scr != NULL) {
    lv_obj_set_style_bg_color(scr, lv_palette_main(LV_PALETTE_RED), LV_PART_MAIN);
    lv_obj_set_style_bg_opa(scr, LV_OPA_COVER, LV_PART_MAIN);
    Serial.println("Set background");
  }

  textbox = lv_label_create(scr);

  if (textbox != NULL) {
    lv_label_set_text(textbox, "LovyanGFX Active!");
    lv_obj_align(textbox, LV_ALIGN_CENTER, 0, 0);
    Serial.println("Set textbox");
  }
}

void loop() {
  lv_timer_handler();
  delay(5);


  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    Serial.print(F("PICC type: "));
    MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
    Serial.println(rfid.PICC_GetTypeName(piccType));

    // Check is the PICC of Classic MIFARE type
    if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI && piccType != MFRC522::PICC_TYPE_MIFARE_1K && piccType != MFRC522::PICC_TYPE_MIFARE_4K) {
      Serial.println(F("Your tag is not of type MIFARE Classic."));
      return;
    }

    if (rfid.uid.uidByte[0] != nuidPICC[0] || rfid.uid.uidByte[1] != nuidPICC[1] || rfid.uid.uidByte[2] != nuidPICC[2] || rfid.uid.uidByte[3] != nuidPICC[3]) {
      Serial.println(F("A new card has been detected."));
      lv_label_set_text(textbox, "A new card has been detected.");

      // Store NUID into nuidPICC array
      for (byte i = 0; i < 4; i++) {
        nuidPICC[i] = rfid.uid.uidByte[i];
      }

      Serial.println(F("The NUID tag is:"));
      Serial.print(F("In hex: "));
      printHex(rfid.uid.uidByte, rfid.uid.size);
      Serial.println();
      Serial.print(F("In dec: "));
      printDec(rfid.uid.uidByte, rfid.uid.size);
      Serial.println();
    } else {
      Serial.println(F("Card read previously."));
      lv_label_set_text(textbox, "Card read previously.");
    }

    // Halt PICC
    rfid.PICC_HaltA();

    // Stop encryption on PCD
    rfid.PCD_StopCrypto1();
  }
}

void printHex(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
}

void printDec(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(' ');
    Serial.print(buffer[i], DEC);
  }
}
