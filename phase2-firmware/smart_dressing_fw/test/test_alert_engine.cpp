#include "../src/alert_engine.h"
#include "utils/csv_loader.h"
#include <cassert>
#include <cmath>
#include <iostream>

void test_m1_2_infection_replay() {
    std::cout << "\n=== M1.2 Infection Scenario Replay ===" << std::endl;

    AlertEngine engine(15);  // 15-min sampling

    // Load M1.2 infection scenario CSV
    std::vector<SensorReading> test_data = load_csv("smart_dressing_fw/test/data/m1_2_infection.csv");

    bool alert_triggered = false;
    uint32_t alert_time = 0.0;

    for (const auto& reading : test_data) {
        uint16_t uptime_hours = static_cast<uint16_t>(std::floor(reading.time_hours ));
        bool alert = engine.update(reading.pH, reading.temp, uptime_hours);

        if (alert && !alert_triggered) {
            alert_triggered = true;
            alert_time = reading.time_hours;
            std::cout << "Alert triggered at: " << alert_time << " hours" << std:: endl;
        }
    }

    // Expected from Python M1.2: 162.5 hours
    std::cout << "Expected alert time: 156.0 hours" << std::endl;
    std::cout << "Actual alert time: " << alert_time << " hours" << std::endl;

    assert(alert_triggered == true);
    assert(std::abs(alert_time - 156.0f) < 1.0f);  // Within 1 hour tolerance

    std::cout << "M1.2 Infection Replay: PASS" << std::endl;
}

void test_m1_2_normal_replay() {
    std::cout << "\n=== M1.2 Normal Scenario Replay ===" << std::endl;

    AlertEngine engine(15);

    std::vector<SensorReading> test_data = load_csv("smart_dressing_fw/test/data/m1_2_normal.csv");

    bool alert_triggered = false;

    for (const auto& reading : test_data) {
        bool alert = engine.update(reading.pH, reading.temp,
                static_cast<uint32_t>(reading.time_hours));

        if (alert) {
            alert_triggered = true;
            std::cout << "Unexpected alert at: " << reading.time_hours << "hours" << std::endl;
        }
    }

    // Expected: Zero alerts in normal healing
    assert(alert_triggered == false);

    std::cout << "M1.2 Normal Replay: PASS (0 false positives)" << std::endl;
}

int main() {
    std::cout << "============================================" << std::endl;
    std::cout << "M2.2 AlertEngine Validation (Offline)" << std::endl;
    std::cout << "============================================" << std::endl;

    try {
        test_m1_2_infection_replay();
        test_m1_2_normal_replay();

        std::cout << "\n All tests PASSED" << std::endl;
        return 0;

    } catch (const std::exception& e) {
        std::cerr << "\n Test FAILED: " << e.what() << std::endl;
        return 1;
    }
}

