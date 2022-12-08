from Resources import *
from dataclasses import dataclass

class TimeSlot:

    def __init__(self, resource: Resource, start_time: int):
        self.start_time = start_time
        self.resource = resource

class TimeSlots:
    """
    A collection of TimeSlot objects.
    """
    def __init__(self, timeslot_length: int = 5, num_timeslots_per_site: int = 288):

        self.timeslot_length = timeslot_length
        self.num_timeslots_per_site = num_timeslots_per_site

        self.timeslots = []
        for r in Resource:
            for idx in range(num_timeslots_per_site):
                self.timeslots.append(TimeSlot(r, idx * timeslot_length))

    def get_timeslot(self, resource: Resource, index: int) -> TimeSlot:

        return self.timeslots[resource * self.num_timeslots_per_site + index]

    def __iter__(self):
        return TimeSlotsIterator(self)


class TimeSlotsIterator:
    """
    Iterator class for TimeSlots.
    """
    def __init__(self, timeslots: TimeSlots):
        self._timeslots = timeslots
        self._index = 0

    def __next__(self) -> TimeSlot:
        if self._index < len(self._timeslots.timeslots):
            slot = self._timeslots.timeslots[self._index]
            self._index += 1
            return slot
        raise StopIteration


@dataclass
class TS:
    timeslot_idx: int
    start_time: float
    end_time: float
    metric_score: float = 1.0

