import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')

if src_path not in sys.path:
    sys.path.insert(0,src_path)

import numpy as np
import matplotlib.pyplot as plt
from wound_model import WoundModel
from noise import NoiseGenerator
from sensor_channel import SensorChannel
from alert_logic import AlertLogic

# ==================================
# CONFIGURATION
# ==================================
SIMULATION_DAYS = 10
SAMPLING_INTERVAL_MIN = 15
SCENARIO = 'normal'  # 'normal' or 'infection'

# Noise parameters (from specifications)
pH_NOISE = NoiseGenerator(
    noise_sigma=0.05,
    drift_sigma_per_hour=0.002,
    sampling_interval_minutes=SAMPLING_INTERVAL_MIN
)

TEMP_NOISE = NoiseGenerator(
    noise_sigma=0.10,
    drift_sigma_per_hour=0.01,
    sampling_interval_minutes=SAMPLING_INTERVAL_MIN
)

# ===================================
# SIMULATION SETUP
# ===================================
wound = WoundModel(scenario=SCENARIO)

ph_channel = SensorChannel(wound, pH_NOISE, 'pH')
temp_channel = SensorChannel(wound, TEMP_NOISE, 'temperature')

alert_engine = AlertLogic(
    pH_threshold=7.5,
    temp_delta_threshold=1.0,   # Changed from1.5
    persistence_hours=12,
    sampling_interval_minutes=SAMPLING_INTERVAL_MIN,
    violation_threshold=0.75
)

print("=" * 60)
print("ALERT LOGIC CONFIGURATION (RUNTIME VERIFICATION)")
print("=" * 60)
print(f"pH threshold: {alert_engine.pH_threshold}")
print(f"Persistence hours: 12 (windowed)")
print(f"Window size: {alert_engine.window_size} samples")
print(f"ΔT threshold: {alert_engine.temp_delta_threshold}")
print(f"Violation threshold: {alert_engine.violation_threshold*100:.0f}%")
print(f"Persistence hours: {alert_engine.window_size * (SAMPLING_INTERVAL_MIN/60):.1f}")
print(f"Baseline mode: {'Dynamic' if alert_engine.temp_baseline is None else 'Fixed'}")
print("=" * 60)

# =======================
# RUN SIMULATION
# =======================
hours = SIMULATION_DAYS * 24
time_points = np.arange(0, hours, SAMPLING_INTERVAL_MIN / 60.0)

pH_clean = []
pH_noisy = []
temp_clean = []
temp_noisy = []
alert_states = []

for t in time_points:
    # Clean values
    pH_clean.append(wound.get_pH(t))
    temp_clean.append(wound.get_temperature(t))

    # Noisy sensor readings
    pH_reading = ph_channel.read(t)
    temp_reading = temp_channel.read(t)

    pH_noisy.append(pH_reading)
    temp_noisy.append(temp_reading)

    # Update alert logic
    alert = alert_engine.update(pH_reading, temp_reading, t)
    alert_states.append(alert)

baseline = alert_engine.temp_baseline

# ==========================
# VISUALIZATION
# ==========================
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# pH plot
axes[0].plot(time_points, pH_clean, 'b-', label='Clean (Ground Truth)', linewidth=2)
axes[0].plot(time_points, pH_noisy, 'b-', alpha=0.3, label='Noisy + Drift', markersize=2)
axes[0].axhline(7.5, color='r', linestyle='--', label='Alert Threshold')
axes[0].set_ylabel('pH')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Temperature plot
axes[1].plot(time_points, temp_clean, 'orange', label='Clean (Ground Truth)', linewidth=2)
axes[1].plot(time_points, temp_noisy, 'orange', alpha=0.3, marker='.',markersize=2, linestyle='', label='Noisy + Drift')
axes[1].axhline(baseline + 1.0, color='r', linestyle='--', label='Alert Threshold (ΔT=1.0°C)')
axes[1].set_ylabel('Temperature (degrees celcius)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Alert state
axes[2].fill_between(time_points, 0, alert_states, color='red', alpha=0.5, label='Alert Active')
axes[2].set_ylabel('Alert State')
axes[2].set_xlabel('Time (hours)')
axes[2].set_ylim([-0.1, 1.1])
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('phase1-simulation/data/plots/m1_2_noise_drift_validation.png', dpi=300)
plt.show()

print(f"\n{'='*60}")
print(f"M1.2 VALIDATION SUMMARY")
print(f"{'='*60}")
print(f"Scenario: {SCENARIO}")
print(f"Alert triggered: {any(alert_states)}")
if any(alert_states):
    first_alert_idx = alert_states.index(True)
    first_alert_time = time_points[first_alert_idx]
    print(f"First alert at: {first_alert_time:.1f} hours ({first_alert_time/24:.1f} days)")
print(f"{'='*60}\n")


