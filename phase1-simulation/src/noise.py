import numpy as np

class NoiseGenerator:
    """
    Generates Gaussian noise + random-walk drift for sensor simulation
    Design principle: Firmware-portable logic (no pandas, no ML)
    """
    def __init__(self, noise_sigma, drift_sigma_per_hour, sampling_interval_minutes=15):
        """
        Args:
            noise_sigma: Standard deviation of Gaussian noise per sample
            drift_sigma_per_hour: Drift accumulation rate (std dev per hour)
            sampling_interval_minutes: Time between samples
        """
        self.noise_sigma = noise_sigma
        self.drift_sigma_per_hour = drift_sigma_per_hour
        self.sampling_interval_minutes = sampling_interval_minutes

        # Calculate drift per sample (not per hour)
        hours_per_sample = sampling_interval_minutes / 60.0
        self.drift_sigma_per_sample = drift_sigma_per_hour * np.sqrt(hours_per_sample)

        # Internal state
        self.current_drift = 0.0

    def reset(self):
        """Reset drift accumulation (for new simulation runs)"""
        self.current_drift = 0.0

    def sample(self):
        """
        Generate one noisy sample with drift.
        Returns:
            (noise, drift): Separate components for debugging
        """
        #Gaussian noise (zero-mean, per-sample)
        noise = np.random.normal(0, self.noise_sigma)

        # Random-walk drift update
        drift_increment = np.random.normal(0, self.drift_sigma_per_sample)
        self.current_drift += drift_increment

        return noise, self.current_drift

    def add_noise_and_drift(self, clean_value):
        """
        Apply noise + drift to a clean sensor reading.

        Args:
            clean_value: Ground-truth value from WoundModel
        Returns:
            Noisy value with drift
        """
        noise, drift = self.sample()
        return clean_value + noise + drift
