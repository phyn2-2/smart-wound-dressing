#include "alert_engine.h"
#include <algorithm>  // std::median
#include <numeric>  // std::accumulate


AlertEngine::AlertEngine(uint8_t sampling_interval_minutes) {
    // Calculate window size (samples in 12 hours)
    uint8_t samples_per_hour = 60 / sampling_interval_minutes;
    window_size = persistence_hours * samples_per_hour;

    // Initialize state
    temp_baseline = 0.0;
    baseline_locked = false;
    alert_active = false;
    uptime_hours = 0;

    // Reserve space for baseline calibration (24h @ 15min = 96 samples)
    baseline_samples.reserve(96);
}

bool AlertEngine::update(float pH_reading, float temp_reading, uint16_t current_uptime_hours) {
    uptime_hours = current_uptime_hours;

    // ===== BASELINE CALIBRATION (first 24 hours) =======
    if (!baseline_locked){
        baseline_samples.push_back(temp_reading);

        if (uptime_hours >= 24) {
            // Lock baseline as MEDIAN (not mean) - robust to outliers
            std::sort(baseline_samples.begin(), baseline_samples.end());
            temp_baseline = baseline_samples[baseline_samples.size() / 2];
            baseline_locked = true;

#ifdef ARDUINO

            Serial.print("Baseline locked: ");
            Serial.print(temp_baseline);
            Serial.println(" degrees C");
#endif
        } else {
            return false;  // Still calibrating
        }
    }

    // ===== THRESHOLD CHECKS ======
    bool pH_violated = (pH_reading > pH_threshold);
    float temp_delta = temp_reading - temp_baseline;
    bool temp_violated = (temp_delta > temp_delta_threshold);
    bool both_violated = pH_violated && temp_violated;

    // ===== WINDOWED PERSISTENCE =====
    violation_window.push_back(both_violated);

    // Trim window if exceeds max size (deque auto-handles with maxlen in Python)
    if (violation_window.size() > window_size) {
        violation_window.pop_front();
    }

    // Check if window is full
    if (violation_window.size() < window_size) {
        return false;  // Not enough data yet
    }

    // Calculate violation rate
    uint8_t violation_count = std::count(violation_window.begin(),
            violation_window.end(), true);
    float violation_rate = static_cast<float>(violation_count) / window_size;

    // Trigger alert if rate exceeds threshold
    alert_active = (violation_rate >= violation_threshold);

    return alert_active;
}

float AlertEngine::getViolationRate() const {
    if (violation_window.empty()) return 0.0;
    uint8_t count = std::count(violation_window.begin(), violation_window.end(), true);
    return static_cast<float>(count) / violation_window.size();
}

uint8_t AlertEngine::getViolationCount() const {
    return std::count(violation_window.begin(), violation_window.end(), true);
}


