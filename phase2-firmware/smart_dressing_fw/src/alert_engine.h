#ifndef ALERT_ENGINE_H
#define ALERT_ENGINE_H
#pragma once

#ifdef ARDUINO
  #include <Arduino.h>
#else
  #include <cstdint>
  #include <deque>
  #include <vector>
  #include <algorithm>
  // This mocks the Serial.print calls so g++ doesn't complain
  struct MockSerial {
      void print(const char* s) {}
      void print(float f) {}
      void println(const char* s) {}
    };
#endif


class AlertEngine {
    private:
        // Thresholds (IMMUTABLE from Phase 1)
        const float pH_threshold = 7.5;
        const float temp_delta_threshold = 1.0;  // degrees C
        const uint8_t persistence_hours = 12;
        const float violation_threshold = 0.75;  // 75%

        // Derived parameters
        uint16_t window_size;  // Calculated from sampling interval

        // State variables
        std::vector<float> baseline_samples;
        std::deque<bool> violation_window;  // Rolling window (max 48 samples @ 15min)
        float temp_baseline;
        bool baseline_locked;
        bool alert_active;

        // Timing
        uint16_t uptime_hours; // Incremented externally

public:
        AlertEngine(uint8_t sampling_interval_minutes = 15);

        // Primary interface (matches Python)
        bool update(float pH_reading, float temp_reading, uint16_t uptime_hours);

        // Status queries
        bool isAlertActive() const { return alert_active; }
        float getBaseline() const { return temp_baseline; }
        bool isBaselineLocked() const { return baseline_locked; }

        // Diagnostics
        float getViolationRate() const;
        uint8_t getViolationCount() const;
};

#endif
