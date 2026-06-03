/*
 * hx711_to_usb - Reads raw 24 bit samples from HX711 and send them via USB (serial / joystick HID).
 * Note: joystick HID only available on atmega32u4.
 * Arad Eizen 22/06/19.
 */

#include "hx711_raw.h"

// uart (serial) baud rate
#define SERIAL_BAUD_RATE		(115200)
// gpios mapping
#define HX711_DT_PIN			(A5)
#define HX711_SCK_PIN			(A4)

// define only one output method
// #define OUTPUT_AS_JOYSTICK
#define OUTPUT_AS_SERIAL_NUMBER
// #define OUTPUT_AS_SERIAL_BUFFER

#ifdef OUTPUT_AS_JOYSTICK
	#include <HID-Project.h>
#endif

Hx711Raw hx711_raw;


void setup()
{
#ifdef OUTPUT_AS_JOYSTICK
	// initialize usb joystick hid
	Gamepad.begin();
#else
	// initialize uart
	Serial.begin(SERIAL_BAUD_RATE);
	while (!Serial);
#endif
	// initialize hx711 module
	hx711_raw.begin(HX711_DT_PIN, HX711_SCK_PIN);
}

void loop()
{
	// waite and read next sample
	hx711_raw.update();

#ifdef OUTPUT_AS_JOYSTICK
	Gamepad.xAxis(hx711_raw.value.as_uint16.lso);
	Gamepad.yAxis(hx711_raw.value.as_uint16.mso);
	Gamepad.write();
#endif

#ifdef OUTPUT_AS_SERIAL_BUFFER
	Serial.write(hx711_raw.value.as_buff, sizeof(hx711_raw.value.as_buff));
#else
	Serial.println(hx711_raw.value.as_uint32);
#endif
}
