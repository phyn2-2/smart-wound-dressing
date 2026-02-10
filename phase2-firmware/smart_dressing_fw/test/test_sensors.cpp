void test_temperature_accuracy() {
    DS18B20 temp_sensor(PIN_ONEWIRE);

    float reading = temp_sensor.read();
    float refrence = 37.0;  // From calibrated instrument

    assert(abs(reading - refrence) < 0.2);  // Within spec
}




