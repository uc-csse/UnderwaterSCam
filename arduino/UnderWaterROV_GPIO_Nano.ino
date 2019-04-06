#define LIGHTS_SW 4
#define REC_SW 5
#define STATUS_LED 3
#define LIGHTS_PWM_PIN 9
#define LED_PIN 13
#define TRIGER_PIN 6
#define VOLTAGE_ADC_PIN 7
#define CURRENT_ADC_PIN 6

//Camera trigger stuff
#define TRIG_FPS 10
#define TRIGGER_RATE_MICROS (1000000/TRIG_FPS)
#define TRIGGER_RATE_MICROS_HALF (TRIGGER_RATE_MICROS/2)

#define SERIAL_BAUD_RATE 115200
#define SWITCH_BOUNCE_DELAY 500000
#define LIGHT_POWER_TOGGLE_DELAY 10000
#define SERIAL_TX_DELAY 500000
#define NUM_LIGHT_INCS 5

#define BATT_AMP_OFFSET 0.330
#define BATT_AMP_PERVOLT 37.8788
#define ADC_VOLTAGE_MUL 0.0048828
#define BATT_VOLT_MULT 11

void setup() {
  // put your setup code here, to run once:
  delay(2000);
  Serial.begin(SERIAL_BAUD_RATE);
  pinMode(LIGHTS_SW, INPUT_PULLUP);
  pinMode(REC_SW, INPUT_PULLUP);
  pinMode(STATUS_LED, OUTPUT);
  pinMode(LIGHTS_PWM_PIN, OUTPUT);
  pinMode(VOLTAGE_ADC_PIN, INPUT);
  pinMode(CURRENT_ADC_PIN, INPUT);
  TCCR1B = TCCR1B & 0b11111000 | 0x04;
  analogWrite(LIGHTS_PWM_PIN, 0);
  pinMode(LED_PIN, OUTPUT);
  pinMode(TRIGER_PIN, OUTPUT);
}


void loop() {
  static boolean rec, prev_light_sw_state, prev_rec_sw_state, start_trig, trigger_state;
  static int light_power;
  static unsigned long prev_rec_sw_micros;
  static unsigned long prev_light_sw_micros;
  static unsigned long prev_trigger_micros;
  static unsigned long prev_serial_tx_micros;
  
  bool light_sw_state, rec_sw_state;
  int bt;
  byte batt_voltage, batt_current;
  float adc_volt, adc_amps;
  unsigned long time_us = micros();
  
  light_sw_state = !digitalRead(LIGHTS_SW);
  rec_sw_state = !digitalRead(REC_SW);
  
  // SERIAL RX
  while (Serial.available() > 0) {
      bt = Serial.read();
      switch(bt) {
          case 1:
              start_trig = true;
              break;
          case 0:
              start_trig = false;
              break;
          default:
              break;
      }
  }
  
  //SERIAL TX
  if ((time_us - prev_serial_tx_micros) > SERIAL_TX_DELAY) {
    prev_serial_tx_micros = time_us;
    
    adc_volt = (float) analogRead(VOLTAGE_ADC_PIN);
    adc_amps = (float) analogRead(CURRENT_ADC_PIN);
    batt_voltage = (byte) min(round(10 * adc_volt * ADC_VOLTAGE_MUL * BATT_VOLT_MULT), 254);
    batt_current = (byte) min(round(10 * adc_amps * ADC_VOLTAGE_MUL * BATT_AMP_PERVOLT + BATT_AMP_OFFSET), 254);
    byte messege[4] = {255, (byte) rec, batt_voltage, batt_current};
    Serial.write(messege, 4);
  }
  
  // Task to trigger cameras
  if ((time_us - prev_trigger_micros) > TRIGGER_RATE_MICROS_HALF) {
      prev_trigger_micros += TRIGGER_RATE_MICROS_HALF;

      if (!trigger_state && start_trig) {
          // trigger low and currently triggering
          digitalWrite(LED_PIN, HIGH);
          digitalWrite(TRIGER_PIN, HIGH);
          trigger_state = true;
      }
      else {
          // trigger high (always bring lines low even if trigger has been turned off)
          digitalWrite(LED_PIN, LOW);
          digitalWrite(TRIGER_PIN, LOW);
          trigger_state = false;
      }
  }
  
  if (rec_sw_state != prev_rec_sw_state) {
    prev_rec_sw_micros = time_us;
    prev_rec_sw_state = rec_sw_state;
  } else if (((time_us - prev_rec_sw_micros) >= SWITCH_BOUNCE_DELAY) && (rec != rec_sw_state)) {
    rec = rec_sw_state;
  }
  
  ///////////// TODO: send rec signal to upsquared ////////////////// 
  ///////////// TODO: recieve and show rov status through LED flashing? //////////////
  if (rec) {
    digitalWrite(STATUS_LED, HIGH);
  } else digitalWrite(STATUS_LED, LOW);
  
  if (light_sw_state != prev_light_sw_state && (time_us - prev_light_sw_micros) >= LIGHT_POWER_TOGGLE_DELAY) {
    prev_light_sw_micros = time_us;
    if (light_power < NUM_LIGHT_INCS) light_power++;
    else {
      light_power = 0;
      analogWrite(LIGHTS_PWM_PIN,0);
    }
    if (light_power != 0) analogWrite(LIGHTS_PWM_PIN, 35 + ((double) light_power)*25/NUM_LIGHT_INCS);
    prev_light_sw_state = light_sw_state;
  }

}
