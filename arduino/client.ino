#include <Servo.h>

Servo myservo;  // Servo 객체 생성

void setup() {
  myservo.attach(9);  // 서보모터 신호선을 아두이노 9번 핀에 연결
  myservo.write(0);   // 초기 각도 설정 (0도)
  Serial.begin(9600);
  delay(1000);        // 1초 대기
}

void loop() {
  if(Serial.available()){
    char receive_msg = Serial.read();
    if (receive_msg == 'o') {
      myservo.write(90);
      delay(1000);
      Serial.write("opened");
    }else if (receive_msg == 'c') {
      myservo.write(0);
      delay(1000);
      Serial.write("closed");
    }else{
      Serial.write(receive_msg);
    }
  }
}