// set default CCD integrate time to 1 ms
unsigned long CCD_integrate_time_in_microsecond = 1000;
unsigned long data_last_sent_time = micros();
unsigned long now = micros();
unsigned long data_transmission_delay_in_microsecond = 100000;
bool data_transmission_interrupted_flag = false;


void setup() {
    // initialize serial communication at 9600 bits per second:
    Serial.begin(9600);
}

void start() {
    if (CCD_integrate_time_in_microsecond <= 100000) {
        data_transmission_delay_in_microsecond = 100000;
    } else {
        data_transmission_delay_in_microsecond = CCD_integrate_time_in_microsecond;
    }
    while (true) {
        now = micros();
        if (now - data_last_sent_time >= data_transmission_delay_in_microsecond) {
            data_last_sent_time = now;
            for (int i=0; i<3694; i++) {
                Serial.write(i%255);
            }
        }
        if (Serial.available()){
            data_transmission_interrupted_flag = true;
            break;
        }
    }
}

void loop() {
    // put your main code here, to run repeatedly:
    if (Serial.available()) {
        String command = Serial.readString();
        if (command == "#Start%") {
            start();
        }
        if (command == "#Stop%") {
            data_transmission_interrupted_flag = false;
        }
        if (command == "#Onestep%") {
            for (int i=0; i<3694; i++) {
                Serial.write(i%255);
            }
        }
        if (command.substring(0,4) == "#IT:") {
            unsigned long unit_convert_c = 0;
            if (command.substring(7,8) == "m") {
                unit_convert_c = 1000;
            } else {
                unit_convert_c = 1000000;
            }
            CCD_integrate_time_in_microsecond = command.substring(4,7).toInt() * unit_convert_c;
            if (data_transmission_interrupted_flag) {
                start();
            }
        }
    }
}
