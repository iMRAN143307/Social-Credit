#include <ArduinoJson.h>
#include <ArduinoJson.hpp>

#include <LovyanGFX.hpp>
#include <lvgl.h>

#include <MFRC522.h>
#include <SPI.h>

#include <WiFi.h>
#include <esp_http_client.h>

#include "config.h"

lv_obj_t *textbox1;
lv_obj_t *image;
lv_obj_t *textbox2;

MFRC522 rfid(CS_READER, RST_READER);

// Init array that will store new NUID
byte nuidPICC[4];

LV_IMAGE_DECLARE(Hammer_Sickle);

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

#define MAX_HTTP_OUTPUT_BUFFER 8192

typedef struct
{
  char buffer[MAX_HTTP_OUTPUT_BUFFER + 1];
  int buffer_idx;
} http_response_t;

static esp_http_client_handle_t client = NULL;
static http_response_t local_response = { 0 };

esp_err_t _http_event_handler(esp_http_client_event_t *evt) {
  switch (evt->event_id) {
    case HTTP_EVENT_ERROR:
      Serial.println("HTTP_EVENT_ERROR");
      break;
    case HTTP_EVENT_ON_CONNECTED:
      Serial.println("HTTP_EVENT_ON_CONNECTED");
      break;
    case HTTP_EVENT_HEADER_SENT:
      Serial.println("HTTP_EVENT_HEADER_SENT");
      break;
    case HTTP_EVENT_ON_HEADER:
      Serial.printf("HTTP_EVENT_ON_HEADER, key=%s, value=%s\n", evt->header_key, evt->header_value);
      break;
    case HTTP_EVENT_ON_DATA:
      {
        Serial.println("HTTP_EVENT_ON_DATA");
        http_response_t *output = (http_response_t *)evt->user_data;

        if (output && (output->buffer_idx + evt->data_len < sizeof(output->buffer) - 1)) {
          memcpy(output->buffer + output->buffer_idx, evt->data, evt->data_len);
          output->buffer_idx += evt->data_len;
          output->buffer[output->buffer_idx] = '\0';
        } else {
          return ESP_FAIL;
        }
        break;
      }
    case HTTP_EVENT_ON_FINISH:
      Serial.println("HTTP_EVENT_ON_FINISH");
      break;
    case HTTP_EVENT_DISCONNECTED:
      Serial.println("HTTP_EVENT_DISCONNECTED");
      break;
    default:
      break;
  }
  return ESP_OK;
}

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

static void reset_screen(void) {
  if (textbox1 != NULL) {
    lv_label_set_text(textbox1, "Scan Card:");
    Serial.println("Set textbox1");
  }
  if (image != NULL) {
    lv_image_set_src(image, &Hammer_Sickle);
    lv_obj_remove_flag(image, LV_OBJ_FLAG_HIDDEN);
    Serial.println("Set image");
  }
  if (textbox2 != NULL) {
    lv_obj_add_flag(textbox2, LV_OBJ_FLAG_HIDDEN);
    Serial.println("Set textbox2");
  }
}

static void reset_screen_cb(lv_timer_t *timer) {
  reset_screen();
  lv_timer_del(timer);
}

void setup() {
  Serial.begin(115200);
  while (!Serial)
    ;

  //----SPI STUFF----
  SPI.begin(CLK, MISO, MOSI, CS_READER);
  rfid.PCD_Init();
  delay(4);
  rfid.PCD_DumpVersionToSerial();
  Serial.println("Ready to scan");


  //----TFT STUFF----
  tft.init();
  tft.setRotation(0);
  tft.fillScreen(TFT_BLUE);
  tft.setSwapBytes(true);

  //----LVGL STUFF----
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
    lv_obj_set_flex_flow(scr, LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(scr, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
    Serial.println("Set background");
  }

  textbox1 = lv_label_create(scr);
  image = lv_image_create(scr);
  textbox2 = lv_label_create(scr);

  reset_screen();

  //----WiFi Stuff---- woof
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.println("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED)
    ;

  Serial.print("WiFi Connected. IP:");
  Serial.println(WiFi.localIP());
}

void loop() {
  lv_timer_handler();
  delay(5);

  int balance = 0;

  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    lv_obj_add_flag(image, LV_OBJ_FLAG_HIDDEN);
    lv_label_set_text(textbox1, "Balance:");

    Serial.print(F("PICC type: "));
    MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
    Serial.println(rfid.PICC_GetTypeName(piccType));

    // Check is the PICC of Classic MIFARE type
    if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI && piccType != MFRC522::PICC_TYPE_MIFARE_1K && piccType != MFRC522::PICC_TYPE_MIFARE_4K) {
      Serial.println(F("Your tag is not of type MIFARE Classic."));
      return;
    }

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

    // Halt PICC
    rfid.PICC_HaltA();

    // Stop encryption on PCD
    rfid.PCD_StopCrypto1();

    if (WiFi.status() == WL_CONNECTED) {
      memset(local_response.buffer, 0, sizeof(local_response.buffer));
      local_response.buffer_idx = 0;

      char url[256] = { 0 };
      snprintf(url, sizeof(url), "%s?user_id=U081ENVL1K2", API_ENDPOINT);

      Serial.println(url);

      esp_http_client_config_t config = {
        .url = url,
        .method = HTTP_METHOD_GET,
        .timeout_ms = 5000,
        .event_handler = _http_event_handler,  // Order changed
        .user_data = &local_response,
      };


      client = esp_http_client_init(&config);
      if (client == NULL) {
        return;
      }

      esp_err_t err = esp_http_client_perform(client);

      if (err == ESP_OK) {
        int status = esp_http_client_get_status_code(client);
        Serial.printf("HTTP GET Status = %d, content_length = %d\n", status, esp_http_client_get_content_length(client));

        Serial.println(local_response.buffer);

        if (status == 200) {
          esp_err_t err = parse_data(&balance);
        }
      } else {
        Serial.printf("HTTP GET request failed: %s\n", esp_err_to_name(err));
      }

        esp_http_client_cleanup(client);
    }

    char balance_str[32];
    snprintf(balance_str, sizeof(balance_str), "%d", balance);

    lv_label_set_text(textbox2, balance_str);
    lv_obj_clear_flag(textbox2, LV_OBJ_FLAG_HIDDEN);

    lv_timer_t *timer = lv_timer_create(reset_screen_cb, 5000, NULL);
  }
}

esp_err_t parse_data(int *res_buffer) {
  esp_err_t ret = ESP_OK;

  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, local_response.buffer);

  // Line 312 fix:
  if (res_buffer != nullptr) {  // Safety check to prevent crashes
    *res_buffer = doc["balance"].as<int>();
  }


  if (err) {
    return ESP_FAIL;
  }
  return ret;
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

//Yip yip

//Yip yip yip

//Hehehehehehehehehehehehehehehe-
//Hehehehehehehehehehehehehehehe-

//Yip

//Yip
