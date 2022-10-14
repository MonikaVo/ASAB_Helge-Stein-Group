//define variables sent from python
String inByte;
String currentState;

// Give the motor control pins names:
int relay1 = 4;
int relay2 = 7;
int relay3 = 8;
int relay4 = 12;

void setup() {
  // Set the pins:
  Serial.begin(9600);
  pinMode(relay1, OUTPUT);
  pinMode(relay2, OUTPUT);
  pinMode(relay3, OUTPUT);
  pinMode(relay4, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available()>0){
    inByte = Serial.readStringUntil('\n');
    if (inByte == "1_1"){
      digitalWrite(relay1, HIGH);
      currentState = digitalRead(relay1);
      Serial.print(currentState);
    }
    else if (inByte == "1_0"){
      digitalWrite(relay1, LOW);
      currentState = digitalRead(relay1);
      Serial.print(currentState);
    }
    else if (inByte == "1_pulse"){
      digitalWrite(relay1, HIGH);
      delay(250);
      digitalWrite(relay1, LOW);
    }
    else if (inByte == "2_1"){
      digitalWrite(relay2, HIGH);
      currentState = digitalRead(relay2);
      Serial.print(currentState);
    }
    else if (inByte == "2_0"){
      digitalWrite(relay2, LOW);
      currentState = digitalRead(relay2);
      Serial.print(currentState);
    }
    else if (inByte == "2_pulse"){
      digitalWrite(relay2, HIGH);
      delay(250);
      digitalWrite(relay2, LOW);
    }
    else if (inByte == "3_1"){
      digitalWrite(relay3, HIGH);
      currentState = digitalRead(relay3);
      Serial.print(currentState);
    }
    else if (inByte == "3_0"){
      digitalWrite(relay3, LOW);
      currentState = digitalRead(relay3);
      Serial.print(currentState);
    }
    else if (inByte == "3_pulse"){
      digitalWrite(relay3, HIGH);
      delay(250);
      digitalWrite(relay3, LOW);
    }
    else if (inByte == "4_1"){
      digitalWrite(relay4, HIGH);
      currentState = digitalRead(relay4);
      Serial.print(currentState);
    }
    else if (inByte == "4_0"){
      digitalWrite(relay4, LOW);
      currentState = digitalRead(relay4);
      Serial.print(currentState);
    }
    else if (inByte == "4_pulse"){
      digitalWrite(relay4, HIGH);
      delay(250);
      digitalWrite(relay4, LOW);
    }
    // Read the state of a pin and send it back
    else if (inByte == "1_read"){
      currentState = digitalRead(relay1);
      Serial.print(currentState);
    }
    else if (inByte == "2_read"){
      currentState = digitalRead(relay2);
      Serial.print(currentState);
    }
    else if (inByte == "3_read"){
      currentState = digitalRead(relay3);
      Serial.print(currentState);
    }
    else if (inByte == "4_read"){
      currentState = digitalRead(relay4);
      Serial.print(currentState);
    }
    else{
      Serial.write("Invalid input");
    }
  }
}
