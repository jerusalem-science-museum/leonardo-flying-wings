
// 11 Dec 2019 Version with automatic compensation of Tara during setup 
// for scale and wing exhibit / Leonardo 
// read XH711, connected to 4 50Kg humen boady sensors/strain gauge (huff bridge connected)
// and send to to Python code 
// see 


#include "HX711_amir.h"

// HX711.DOUT	- pin #A5 original was #A1
// HX711.PD_SCK	- pin #A4 origianl was #A0

HX711 scale(A5, A4);		// for Arduino pro-mini, take care A5 and A6 ar analog only, parameter "gain" is ommited; the default value 128 is used by the library
long tara  = 0 ; // only for Oct 2019 problem 
void setup() {

//  Serial.begin(115200);
 Serial.begin(57600);
  delay (500);// wait 0.5 sec for stabilize 
  for (int i = 0; i <= 9; i++) {
    tara = tara + scale.read();
    delay (10);
    }
  tara = tara/10 ; //average tara
//  scale.tare();                // reset the scale to 0
//  scale.set_scale(2280.f);                      // this value is obtained by calibrating the scale with known weights; see the README for details
//  scale.tare();				        // reset the scale to 0
  
}

long raw_weight = 100;

void loop() {

//  weight = scale.get_value();//read one scale and shift (tara) measure 
raw_weight = scale.read();//read one raw measure (long, 3 byle original)
Serial.println (raw_weight-tara);
//  Serial.println (weight);
delay(1);

}
