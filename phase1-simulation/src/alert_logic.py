import numpy as np
from collections import deque

class AlertLogic:
    """
    Windowed persistence-based infection detection.
    Alert triggers when a high proportion of recent samples exceed physiological thresholds.
    """
    def __init__(self,
                 pH_threshold=7.5,
                 temp_delta_threshold=1.0,
                 persistence_hours=12,
                 sampling_interval_minutes=15,
                 violation_threshold=0.75):  # NEW PARAMETER
        """
        Args:
            pH_threshold: pH alert level
            temp_delta_threshold: Temperature rise above baseline (degrees celcius)
            persistence_hours: How long conditions must persist
            sampling_interval_minutes: Sampling rate
            temp_baseline: Normal wound temperature
        """
        self.pH_threshold = pH_threshold
        self.temp_delta_threshold = temp_delta_threshold

        # Calculate window size
        samples_per_hour = 60 / sampling_interval_minutes
        self.window_size = int(persistence_hours * samples_per_hour)

        # Rolling window for violations (NEW)
        self.violation_window = deque(maxlen=self.window_size)
        self.violation_threshold = violation_threshold

        # Baseline tracking
        self.temp_baseline = None
        self.baseline_samples = []
        self.baseline_window_hours = 24
        self.baseline_locked = False

        # Alert state
        self.alert_active = False

    def update(self, pH_reading, temp_reading, t_hours):
        """
        Process new sensor readings and update alert state.
        Args:
            pH_reading: Current pH value (possibly noisy)
            temp_reading: Current temperature (possibly noisy)
        Returns
            bool: True if alert is active
        """
        # Collect baseline during first 24 hours
        if not self.baseline_locked:
            self.baseline_samples.append(temp_reading)

            if t_hours >= self.baseline_window_hours:
                self.temp_baseline = np.median(self.baseline_samples)
                self.baseline_locked = True
                print(f"Baseline locked: {self.temp_baseline:.2f} degrees celcius")
            else:
                return False  # still calibrating

        # Threshold checks
        pH_violated = (pH_reading > self.pH_threshold)
        temp_delta = temp_reading - self.temp_baseline
        temp_violated = (temp_delta > self.temp_delta_threshold)

        both_violated = pH_violated and temp_violated

        # Add to rolling window
        self.violation_window.append(1 if both_violated else 0)

        # Check if window is full
        if len(self.violation_window) < self.window_size:
            return False  # Not enough data yet

        # Calculate violation rate over window
        violation_rate = sum(self.violation_window) / self.window_size

        # Trigger alert if rate exceeds threshold
        self.alert_active = (violation_rate >= self.violation_threshold)

        return self.alert_active

    def reset(self):
        """Reset alert state (for new simulation runs)"""
        self.violation_window.clear()
        self.alert_active = False
        self.baseline_locked = False
        self.baseline_samples = []
        self.temp_baseline = None

    def get_status(self):
        """Return diagnostic information."""
        current_violations = sum(self.violation_window)
        required = int(self.window_size * self.violation_threshold)

        return {
            'alert_active': self.alert_active,
            'window_size': self.window_size,
            'violation_count': current_violations,
            'required_violations': required,
            'violation_rate': current_violations / self.window_size if self.window_size else 0.0
        }

