"""
M1.3: Alert Logic Robustness & Sensitivity Analysis
Systematic characterization of validated M1.2 logic under perturbations.
NO ALGORITHMIC CHANGES PERMITTED.
"""
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from itertools import product

from wound_model import WoundModel
from noise import NoiseGenerator
from sensor_channel import SensorChannel
from alert_logic import AlertLogic

# ====================================
# TEST CONFIGURATIONS
# ===================================
SAMPLING_INTERVALS = [5, 15, 30, 60]    # T3.1
NOISE_MULTIPLIERS = [1.0, 2.0, 3.0]     # T3.2
pH_THRESHOLDS = [7.3, 7.5, 7.7]         # T3.3
DT_THRESHOLDS = [0.8, 1.0, 1.2]         # T3.4
VIOLATION_THRESHOLDS = [0.60, 0.75, 0.90]    # T3.5

SCENARIOS = ['normal', 'infection']
SIMULATION_DAYS = 10    # Extended for late alerts

# =================================
# BASELINE PARAMETERS
# =================================
BASELINE_PARAMS = {
    'sampling_interval': 15,
    'noise_multiplier': 1.0,
    'pH_threshold': 7.5,
    'dt_threshold': 1.0,
    'violation_threshold': 0.75
}

# =============================
# UTILITY FUNCTIONS
# ============================

def run_single_test(scenario, sampling_interval, noise_mult, pH_thresh, dt_thresh, viol_thresh):
    """
    Run one simulation with specified parameters.
    Returns:
        dict: {
        'alert_triggered': bool,
        'alert_time': float or None,
        'violation_rate_peak': float
    }
    """
    # Setup wound model
    wound = WoundModel(scenario=scenario)

    # Setup noise generators
    pH_noise = NoiseGenerator(
        noise_sigma=0.05 * noise_mult,
        drift_sigma_per_hour=0.002,
        sampling_interval_minutes=sampling_interval
    )

    temp_noise = NoiseGenerator(
        noise_sigma=0.10 * noise_mult,
        drift_sigma_per_hour=0.01,
        sampling_interval_minutes=sampling_interval
    )

    # Setup sensor channels
    pH_channel = SensorChannel(wound, pH_noise, 'pH')
    temp_channel = SensorChannel(wound, temp_noise, 'temperature')

    # Setup alert logic
    alert_engine = AlertLogic(
        pH_threshold=pH_thresh,
        temp_delta_threshold=dt_thresh,
        persistence_hours=12,
        sampling_interval_minutes=sampling_interval,
        violation_threshold=viol_thresh
    )

    # Run simulation
    hours = SIMULATION_DAYS * 24
    time_points = np.arange(0, hours, sampling_interval / 60.0)

    alert_triggered = False
    alert_time = None
    peak_violation_rate = 0.0

    for t in time_points:
        # Read sensors
        pH_reading = pH_channel.read(t)
        temp_reading = temp_channel.read(t)

        # Update alert logic
        alert_active = alert_engine.update(pH_reading, temp_reading, t)

        # Track first alert
        if alert_active and not alert_triggered:
            alert_triggered = True
            alert_time = t

        # Track peak violation rate
        status = alert_engine.get_status()
        if status['violation_rate'] > peak_violation_rate:
            peak_violation_rate = status['violation_rate']

    return {
            'alert_triggered': alert_triggered,
            'alert_time': alert_time,
            'violation_rate_peak': peak_violation_rate
        }


def run_test_suite(test_name, varied_param, param_values):
    """
    Run Systematic test varying one parameter.
    Args:
        test_name: eg., "T3.1_Sampling_Interval"
        varied_param: e.g, "sampling_interval"
        param_values: list of values to test
    Returns:
        pd.DataFrame with results
    """
    results = []

    for scenario in SCENARIOS:
        for value in param_values:
            # Build parameter dict
            params = BASELINE_PARAMS.copy()
            params[varied_param] = value

            # Run test
            result = run_single_test(
                scenario=scenario,
                sampling_interval=params['sampling_interval'],
                noise_mult=params['noise_multiplier'],
                pH_thresh=params['pH_threshold'],
                dt_thresh=params['dt_threshold'],
                viol_thresh=params['violation_threshold']
            )

            # Record
            results.append({
                'test': test_name,
                'scenario': scenario,
                varied_param : value,
                'alert_triggered': result['alert_triggered'],
                'alert_time_hours': result['alert_time'],
                'alert_time_days': result['alert_time'] / 24 if result['alert_time'] else None,
                'peak_violation_rate': result['violation_rate_peak']
            })

            # Progress
            print(f"{test_name} | {scenario} | {varied_param}={value} | Alert={result['alert_triggered']}")

    return pd.DataFrame(results)


# ==============================
# MAIN TEST EXECUTION
# =============================
def main():
    print("="*70)
    print("M1.3 ROBUSTNESS & SENSITIVITY ANALYSIS")
    print("="*70)
    print()

    all_results = []

    # ===== TEST 3.1: Sampling Interval =====
    print("Running T3.1: Sampling Interval Stress Test...")
    df_t31 = run_test_suite("T3.1_Sampling", "sampling_interval", SAMPLING_INTERVALS)
    all_results.append(df_t31)
    print()

    # ===== TEST 3.2: Noise Stress =====
    print("Running T3.2: Noise Robustness Test...")
    df_t32 = run_test_suite("T3.2_Noise", "noise_multiplier", NOISE_MULTIPLIERS)
    all_results.append(df_t32)
    print()

    # ====== TEST 3.3: pH Threshold =====
    print("Running T3.3: pH Threshold Sensitivity...")
    df_t33 = run_test_suite("T3.3_pH", "pH_threshold", pH_THRESHOLDS)
    all_results.append(df_t33)
    print()

    # ==== TEST 3.4: ΔT Threshold ====
    print("Running T3.4: Temperature Delta Sensitivity...")
    df_t34 = run_test_suite("T3.4_DeltaT", "dt_threshold", DT_THRESHOLDS)
    all_results.append(df_t34)
    print()

    # ==== TEST 3.5: Violation Threshold ====
    print("Running T3.5: Persistence Strictness...")
    df_t35 = run_test_suite("T3.5_Persistence", "violation_threshold", VIOLATION_THRESHOLDS)
    all_results.append(df_t35)
    print()

    # Consolidate results
    df_all = pd.concat(all_results, ignore_index=True)

    # Save to CSV
    output_path = 'phase1-simulation/data/validation/m1_3_results.csv'
    df_all.to_csv(output_path, index=False)
    print(f"Results saved to: {output_path}")

    # Generate summary report
    generate_summary_report(df_all)

    # Generate sensitivity plots
    generate_sensitivity_plots(df_all)

def generate_summary_report(df):
    """Print formatted summary of all tests."""
    print("\n" + "="*70)
    print("M1.3 SUMMARY REPORT")
    print("="*70)

    for test_name in df['test'].unique():
        print(f"\n### {test_name}")
        test_data = df[df['test'] == test_name]

        # Infection cases
        infection_data = test_data[test_data['scenario'] == 'infection']
        print("\n**Infection Scenario:**")
        print(infection_data[['sampling_interval', 'noise_multiplier', 'pH_threshold',
                              'dt_threshold', 'violation_threshold',
                              'alert_triggered', 'alert_time_days']].to_string(index=False))

        # Normal cases
        normal_data = test_data[test_data['scenario'] == 'normal']
        false_positives = normal_data[normal_data['alert_triggered'] == True]

        print("\n**Normal Scenario:**")
        if len(false_positives) > 0:
            print(f"FALSE POSITIVES DETECTED: {len(false_possitives)}")
            print(false_positives[['sampling_interval', 'noise_multiplier', 'pH_threshold',
                                    'dt_threshold', 'violation_threshold']].to_string(index=False))

        else:
            print("Zero false positives across all parameter variations")

def generate_sensitivity_plots(df):
    """Generate trade-off curves."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # T3.4: ΔT Threshold vs Alert Time
    t34_data = df[(df['test'] == 'T3.4_DeltaT') & (df['scenario'] == 'infection')]
    axes[0,0].plot(t34_data['dt_threshold'], t34_data['alert_time_days'],
                   'o-', linewidth=2, markersize=8)
    axes[0, 0].set_xlabel('ΔT Threshold (degrees celcius)')
    axes[0, 0].set_ylabel('Alert Time (days)')
    axes[0, 0].set_title('T3.4: Temperature Sensitivity')
    axes[0, 0].grid(True, alpha=0.3)

    # T3.3: pH Threshold vs Alert Time
    t33_data = df[(df['test'] == 'T3.3_pH') & (df['scenario'] == 'infection')]
    axes[0, 1].plot(t33_data['pH_threshold'], t33_data['alert_time_days'],
                    's-', linewidth=2, markersize=8, color='orange')
    axes[0, 1].set_xlabel('pH Threshold')
    axes[0, 1].set_ylabel('Alert Time (days)')
    axes[0, 1].set_title('T3.3: pH Sensitivity')
    axes[0, 1].grid(True, alpha=0.3)

    # T3.1: Sampling Interval vs Alert Time
    t31_data = df[(df['test'] == 'T3.1_Sampling') & (df['scenario'] == 'infection')]
    axes[1, 0].plot(t31_data['sampling_interval'], t31_data['alert_time_days'],
                    '^-', linewidth=2, markersize=8, color='green')
    axes[1, 0].set_xlabel('Sampling Interval (minutes)')
    axes[1, 0].set_ylabel('Alert Time (days)')
    axes[1, 0].set_title('T3.1: Sampling Rate Impact')
    axes[1, 0].grid(True, alpha=0.3)

    # T3.2 Noise Multiplier vs Violation Rate
    t32_data = df[(df['test'] == 'T3.2_Noise') & (df['scenario'] == 'infection')]
    axes[1,1].plot(t32_data['noise_multiplier'], t32_data['peak_violation_rate'] * 100,
                   'd-', linewidth=2, markersize=8, color='red')
    axes[1, 1].axhline(75, color='black', linestyle='--', label='75% Threshold')
    axes[1, 1].set_xlabel('Noise Multiplier')
    axes[1, 1].set_ylabel('Peak Violation Rate (%)')
    axes[1, 1].set_title('T3.2: Noise Robustness')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('phase1-simulation/data/validation/m1_3_sensitivity_curves.png', dpi=300)
    print("Sensitivity plots saved")
    plt.show()

if __name__ == "__main__":
    main()


