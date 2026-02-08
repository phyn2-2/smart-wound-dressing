import numpy as np

class WoundModel:
    def __init__(self, scenario='normal'):
        self.scenario = scenario
        self.PH_base = 6.0
        self.T_base = 36.8
        self.alpha = 2.0  # ph sensitivity to ISI
        self.beta = 1.65  # Temp sensitivity to ISI

    def compute_ISI(self, t_hours):
        """
        t_hours: time since wound ceareation (0-168 for 7 days)
        Returns: ISI value [0,1]
        """
        if self.scenario == 'normal':
            return 0.1
        elif self.scenario == 'infection':
            if t_hours < 48:  # Before Day 3
                return 0.0
            else:
                t_inf = t_hours - 48  # hours since infection onset
                return 0.2 + 0.6 * (1 - np.exp(-t_inf / 36))

        return 0.0

    def get_pH(self, t_hours):
        ISI = self.compute_ISI(t_hours)
        return self.PH_base + self.alpha * ISI

    def get_temperature(self, t_hours):
        ISI = self.compute_ISI(t_hours)
        return self.T_base + self.beta * ISI
