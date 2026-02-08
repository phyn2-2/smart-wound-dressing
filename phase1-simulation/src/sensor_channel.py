from wound_model import WoundModel
from noise import NoiseGenerator

class SensorChannel:
    """
    Combines clean physiological model with realistic sensor imperfections.
    This is the BRIDGE between ideal physics and real hardware
    """
    def __init__(self, wound_model, noise_generator, sensor_name):
        """
        Args:
            wound_model: Instance of WoundModel
            noise_generator: Instance of NoiseGenerator
            sensor_name: 'pH' or 'temperature' (for extraction)
        """
        self.wound_model = wound_model
        self.noise_gen = noise_generator
        self.sensor_name = sensor_name

    def read(self, t_hours):
        """
        Simulate a sensorelf.reading at time t

        Args:
            t_hours: Time since wound creation
        Returns:
            Noisy sensor value
        """
        # Get clean ground truth
        if self.sensor_name == 'pH':
            clean_value = self.wound_model.get_pH(t_hours)
        elif self.sensor_name == 'temperature':
            clean_value = self.wound_model.get_temperature(t_hours)
        else:
            raise ValueError(f"Uknown sensor: {self.sensor_name}")

        # Add noise + drift
        noisy_value = self.noise_gen.add_noise_and_drift(clean_value)

        return noisy_value
