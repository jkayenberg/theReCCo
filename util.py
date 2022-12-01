from datetime import timedelta

import pandas as pd


class Battery:
    """(Way too) simple battery.

    Args:
        capacity: Battery capacity in Wh
        soc: Initial state of charge (SoC) in Wh
    """

    def __init__(self, capacity, soc=0):
        self.capacity = capacity
        self.soc = soc

    def update(self, energy):
        """Can be called during simulation to charge or discharge energy.

        Args:
            energy: Energy in Wh to be charged/discharged.
              If `energy` is positive the battery is charged.
              If `energy` is negative the battery is discharged.

        Returns the excess energy after the update:
        - Positive if your battery is fully charged
        - Nevative if your battery is empty
        - else 0
        """
        self.soc += energy
        excess_energy = 0

        if self.soc < 0:
            excess_energy = self.soc
            self.soc = 0
        elif self.soc > self.capacity:
            excess_energy = self.soc - self.capacity
            self.soc = self.capacity

        return excess_energy


def simtime_to_datetime(simtime_in_seconds, start_date):
    return start_date + timedelta(seconds=simtime_in_seconds)


def read_battery_process(env, battery, result):
    """Simpy process that reads and stores the battery state of charge (SoC) on every step."""
    while True:
        result.append(battery.soc)
        yield env.timeout(1)


def solar_charge_process(env, battery, solar_values, solar_area, solar_efficiency=0.18):
    """Simpy process that charges the battery on every timestep."""
    for solar in solar_values:
        for i in range(60):
            battery.update(solar * solar_area * solar_efficiency / 3600)
            yield env.timeout(1)

def wind_charge_process(env, battery, wind_area, wind_speed, wind_efficiency=0.25):
    """Simpy process that charges the battery on every timestep."""
    print("test")
    print("wind area: ", wind_area)
    if wind_area == "large":
        A= 2*0.8
    elif wind_area == "small":
        A = 0.52*0.75
    else:
        A = 0.

    for wind in wind_speed:
        for i in range(60):

            battery.update(0.5 * 1.225 * (wind**3) * A * wind_efficiency / 3600)
            yield env.timeout(1)

def compute_tasks_process(env, battery, start_date, task_arrival_times, task_stats):
    last_task_time = start_date
    for now in task_arrival_times:
        """TODO"""
        seconds_since_last_task = (now - last_task_time).seconds
        yield env.timeout(seconds_since_last_task)
        excess = battery.update(-1)
        successful = excess >= 0
        task_stats.append((now, successful))
        last_task_time = pd.to_datetime(now)
