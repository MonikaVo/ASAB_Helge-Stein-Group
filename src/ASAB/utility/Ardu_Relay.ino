//define variables sent from python
String inByte;

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
    if (inByte == "1_on"){
      digitalWrite(relay1, HIGH);
      Serial.write("Relay_1 on");
    }
    else if (inByte == "1_off"){
      digitalWrite(relay1, LOW);
      Serial.write("Relay_1 off");
    }
    else if (inByte == "1_pulse"){
      digitalWrite(relay1, HIGH);
      delay(250);
      digitalWrite(relay1, LOW);
    }
    else if (inByte == "2_on"){
      digitalWrite(relay2, HIGH);
      Serial.write("Relay_2 on");
    }
    else if (inByte == "2_off"){
      digitalWrite(relay2, LOW);
      Serial.write("Relay_2 off");
    }
    else if (inByte == "2_pulse"){
      digitalWrite(relay2, HIGH);
      delay(250);
      digitalWrite(relay2, LOW);
    }
    else if (inByte == "3_on"){
      digitalWrite(relay3, HIGH);
      Serial.write("Relay_3 on");
    }
    else if (inByte == "3_off"){
      digitalWrite(relay3, LOW);
      Serial.write("Relay_3 off");
    }
    else if (inByte == "3_pulse"){
      digitalWrite(relay3, HIGH);
      delay(250);
      digitalWrite(relay3, LOW);
    }
    else if (inByte == "4_on"){
      digitalWrite(relay4, HIGH);
      Serial.write("Relay_4 on");
    }
    else if (inByte == "4_off"){
      digitalWrite(relay4, LOW);
      Serial.write("Relay_4 off");
    }
    else if (inByte == "4_pulse"){
      digitalWrite(relay4, HIGH);
      delay(250);
      digitalWrite(relay4, LOW);
    }
    else{
      Serial.write("Invalid input");
    }
  }
}
