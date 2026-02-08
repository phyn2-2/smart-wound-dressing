import numpy as np
import matplotlib.pyplot as plt
from wound_model import WoundModel

# Time axis:0-168 hours (7 days)
t_hours = np.arange(0, 169)

normal = WoundModel(scenario='normal')
infection = WoundModel(scenario='infection')

# Generate curves
pH_normal = [normal.get_pH(t) for t in t_hours]
T_normal = [normal.get_temperature(t) for t in t_hours]

pH_inf = [infection.get_pH(t) for t in t_hours]
T_inf = [infection.get_temperature(t) for t in t_hours]

# Plot
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(t_hours, pH_normal, label='Normal')
plt.plot(t_hours, pH_inf, label='infection')
plt.axhline(7.5, linestyle='--')
plt.title("pH vs Time")
plt.xlabel("Time (hours)")
plt.ylabel("pH")
plt.legend()

plt.subplot(1,2,2)
plt.plot(t_hours, T_normal, label='Normal')
plt.plot(t_hours, T_inf, label='Infection')
plt.title("Temperature vs Time")
plt.xlabel("Time (hours)")
plt.ylabel("Temperature (degrees celcius)")
plt.legend()

plt.tight_layout()
plt.show()
