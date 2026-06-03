#ifndef _HX711_RAW_H_
#define _HX711_RAW_H_

#include <Arduino.h>

#define HX711_OFFSET			(4000000)


class Hx711Raw {
public:
    void begin(uint8_t dt_pin, uint8_t sck_pin);
	void update(void);
	union {
		uint32_t as_uint32;
		struct {
			uint16_t mso;
			uint16_t lso;
		} as_uint16;
		uint8_t as_buff[sizeof(uint32_t)];
	} value;
private:
	uint8_t _dt_pin;
	uint8_t _sck_pin;
};

#endif
