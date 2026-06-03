#include "hx711_raw.h"


void Hx711Raw::begin(uint8_t dt_pin, uint8_t sck_pin)
{
	_dt_pin = dt_pin;
	_sck_pin = sck_pin;

	pinMode(_dt_pin, INPUT);
	pinMode(_sck_pin, OUTPUT);
}

void Hx711Raw::update(void)
{
	// wait for sample
	while (digitalRead(_dt_pin))
		delay(0);
        
	// disable interrupts because hx711 is sensitive
	noInterrupts();

	// read 24 bits
	uint32_t data = 0;
	data |= ((uint32_t)shiftIn(_dt_pin, _sck_pin, MSBFIRST)) << 16;
	data |= ((uint32_t)shiftIn(_dt_pin, _sck_pin, MSBFIRST)) << 8;
	data |= ((uint32_t)shiftIn(_dt_pin, _sck_pin, MSBFIRST));

	// set channel and 128 gain factor for the next reading
	digitalWrite(_sck_pin, HIGH);
	digitalWrite(_sck_pin, LOW);
    
	// re-enable interrupts
	interrupts();

	// SIGN EXTENSION: If the 24th bit is 1, fill the top 8 bits with 1s to make it a proper negative 32-bit integer
	if (data & 0x800000) {
		data |= 0xFF000000;
	}

	// Apply offset and save to union
	value.as_uint32 = data + HX711_OFFSET;
}