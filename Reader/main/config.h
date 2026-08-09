#define WIFI_SSID "Startuptive"
#define WIFI_PASS "start2014"
#define WIFI_PORT 80;

#define API_ENDPOINT "https://api-v3.mbta.com/predictions?filter[stop]=2044,2049&filter[route]=71&include=trip&page[limit]=4&sort=arrival_time"

#define CLK 7
#define MISO 5
#define MOSI 6
#define CS_LCD 10
#define CS_READER 15
#define RST_LCD 13
#define RST_READER 4
#define DC_LCD 9

#define LV_CONF_SKIP 1
#define LV_USE_STDLIB_MALLOC 1
#define LV_COLOR_DEPTH 16