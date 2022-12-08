import numpy as np
from Timeslots import *
from typing import List, Union, Tuple

class Observations:

    def __init__(self):

        #initialize
        self.num_obs = 0
        self.name = np.empty((0,), dtype=str)
        self.resource = np.empty((0,), dtype=Resource)
        self.obs_time = np.empty((0,), dtype=float)
        self.start_slots = []
        self.priority = np.empty((0,), dtype=float)

    def add_obs(self, name: str, resource: Resource, start_slot_idx: List[TS],
                obs_time: float, priority: float) -> None:

        # add an observation to the collection of observations.

        self.name = np.append(self.name, name)
        self.resource = np.append(self.resource, resource)
        self.start_slots.append(start_slot_idx)
        self.obs_time = np.append(self.obs_time, obs_time)
        self.num_obs += 1
        self.priority = np.append(self.priority, priority)



