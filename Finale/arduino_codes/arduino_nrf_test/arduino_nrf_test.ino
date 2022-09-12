#include <RF24.h>

#define PIN_RF24_CSN             9
#define PIN_RF24_CE             10
 
#define NRF24_DYNAMIC_PAYLOAD 1
byte rf24_tx[6] = "readp"; // sending
byte rf24_rx[6] = "00001"; // receiving

byte payload[32];
char chars[32];

#include <Servo.h>

Servo motor;

RF24 radio(PIN_RF24_CE, PIN_RF24_CSN);

void setup() {
  Serial.begin(115200);
  nrf24_setup();
  radio.startListening();
  motor.attach(5);
  motor.write(0);
}

void loop() {
  if(Serial.available()){
    String s = Serial.readStringUntil('\n');
    motor.write(s.toInt());
  }
  
  while (radio.available()) {
    read_response();
  }
}

void read_response() {
  memset(chars, 0, 32);
  uint8_t Size = radio.getDynamicPayloadSize();
  radio.read(&chars, Size); //String str((char*)chars);

  radio.stopListening();
  delay(10);
  boolean success = radio.write(chars, Size);
  radio.startListening();
  
  Serial.println("Received msg " + String(chars) + " Ack: " + String(success));
}


void nrf24_setup() {
  radio.begin();
  radio.enableDynamicPayloads();
  radio.setAutoAck(true);                 
  radio.setPALevel(RF24_PA_MIN);
  radio.setRetries(10, 15);              
  radio.setDataRate(RF24_250KBPS);          
  radio.setChannel(0x76);
  radio.setCRCLength(RF24_CRC_16);
  radio.setPayloadSize(32);
  radio.openWritingPipe(rf24_tx);
  radio.openReadingPipe(0, rf24_rx);
  radio.startListening();
}
