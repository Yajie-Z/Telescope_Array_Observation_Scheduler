from typing import List, Union, Tuple
from Resources import *
from Observations import *
from Timeslots import *


Schedule = List[Union[int, None]]
Score = float
Priority = int
GA_Schedule = List[Tuple[int, int]]


def schedule_transform(final_schedule: Schedule, observations: Observations, resource: Resource, timeslots: TimeSlots) -> GA_Schedule:

    # curr_time = 0
    sched = []

    resource_list = [Resource.S1,Resource.S2,Resource.S3,Resource.S4,Resource.S5]

    for i in range(len(resource_list)):
        if resource == resource_list[i]:
            for ts_idx, obs_idx in \
                    enumerate(final_schedule[timeslots.num_timeslots_per_site * i :timeslots.num_timeslots_per_site * (i+1)]):

                    if obs_idx is None or observations.resource[obs_idx] not in [resource]:
                        continue
                    if len(sched) == 0 or sched[-1][1] != obs_idx:
                        sched.append((ts_idx, obs_idx))
    return sched


def detailed_schedule(name: str, schedule: GA_Schedule, timeSlots: TimeSlots, observations: Observations,
                      stop_time: int) :
    gap_count = []
    line_start = '\n\t' if name is not None else '\n'
    data = name if name is not None else ''
    task_id = 0
    site_task_list =[]

    obs_prev_time = 0
    for obs_start_time_slot, obs_idx in schedule:
        obs_start_time = obs_start_time_slot * timeSlots.timeslot_length
        gap_size = int(obs_start_time - obs_prev_time)

        gap_count.append(gap_size)
        if gap_size > 0e-3:
            data += line_start + f'Gap1 of  {gap_size:>3} min{"s" if gap_size > 1 else ""}'
        data += line_start + f'At time {obs_start_time:>5}: Observation {observations.name[obs_idx]:<5}, ' \
                             f'resource={Resource(observations.resource[obs_idx]).name:<4}, ' \
                             f'obs_time={int(observations.obs_time[obs_idx].seconds/60):>3} mins, ' \
                             f'priority={observations.priority[obs_idx]:>4}'
        task_id += 1
        site_task_list.append(task_id)

        obs_prev_time = obs_start_time + observations.obs_time[obs_idx].seconds/60

    gap_size = int(stop_time - obs_prev_time)
    gap_count.append(gap_size)
    if gap_size > 0e-3:
        data += line_start + f'Gap of  {gap_size:>3} min{"s" if gap_size > 1 else ""}'

    return data,gap_count,site_task_list

fenzi = []
fenmu = []

def print_schedule(timeslots: TimeSlots, observations: Observations,
                   final_schedule: Schedule, final_score: Score, out = None):

    s1_sched = schedule_transform(final_schedule, observations, Resource.S1, timeslots)
    s2_sched = schedule_transform(final_schedule, observations, Resource.S2, timeslots)

    ### s1 ###
    printable_schedule_s1,s1,site_tasks1 = detailed_schedule("S1:", s1_sched, timeslots, observations,
                                              timeslots.num_timeslots_per_site * timeslots.timeslot_length)

    if out is None:
        print(printable_schedule_s1)
    else:
        out.write(printable_schedule_s1 + '\n')

    s1_obs = set([obs_idx for obs_idx in final_schedule[:timeslots.num_timeslots_per_site] if obs_idx is not None])
    s1_time=[]

    for obs_idx in s1_obs:
        s1_time.append(observations.obs_time[obs_idx].seconds/60)

    s1_usage = (timeslots.num_timeslots_per_site * timeslots.timeslot_length) - sum(s1)
    s1_pct =  s1_usage / (timeslots.num_timeslots_per_site * timeslots.timeslot_length -s1[0] -s1[-1]) * 100

    s1_summary = f'\tUsage: {s1_usage},{timeslots.num_timeslots_per_site * timeslots.timeslot_length -s1[0] -s1[-1]}, {s1_pct}%, Fitness: {final_score}'
    fenzi.append(s1_usage)
    fenmu.append(timeslots.num_timeslots_per_site * timeslots.timeslot_length -s1[0] -s1[-1])
    if out is None:
        print(s1_summary + '\n')
    else:
        out.write(s1_summary + ('\n' * 2))


    # *** S2 ***
    printable_schedule_s2,gap2, site_tasks2= detailed_schedule("S2:", s2_sched, timeslots, observations,
                                              timeslots.num_timeslots_per_site * timeslots.timeslot_length)

    if out is None:
        print(printable_schedule_s2)
    else:
        out.write(printable_schedule_s2 + '\n')

    s2_obs = set([obs_idx for obs_idx in final_schedule[timeslots.num_timeslots_per_site:] if obs_idx is not None])
    s2_time = []
    for obs_idx in s2_obs:
        s2_time.append(observations.obs_time[obs_idx].seconds / 60)

    s2_usage = (timeslots.num_timeslots_per_site * timeslots.timeslot_length) - sum(gap2)

    s2_pct = s2_usage / (timeslots.num_timeslots_per_site * timeslots.timeslot_length - gap2[0]-gap2[-1]) * 100

    s2_summary = f'\tUsage: {s2_usage}, {timeslots.num_timeslots_per_site * timeslots.timeslot_length - gap2[0]-gap2[-1]},{s2_pct}%'
    fenzi.append(s2_usage)
    fenmu.append(timeslots.num_timeslots_per_site * timeslots.timeslot_length - gap2[0]-gap2[-1])

    if out is None:
        print(s2_summary)
    else:
        out.write(s2_summary + '\n')

    overall_score = f"Final score: {final_score}"
    if out is None:
        print(overall_score)
    else:
        out.write(overall_score + '\n')

    print("[time usage:]")
    print(fenzi)
    print(fenmu)
    print(sum(fenzi)/sum(fenmu))

    # Unscheduled observations.
    str_planid = []
    for x in observations.name:
        if str(x) not in str_planid:
            str_planid.append(str(x))

    have_window_total = f'\nTotal observable plan: {", ".join(set(str_planid))}'
    if out is None:
        print(have_window_total)
    else:
        out.write(have_window_total + '\n')

    oid_list1 = []
    for obs_start_time_slot, obs_idx in s1_sched:
        oid_list1.append(observations.name[obs_idx])
    for obs_start_time_slot, obs_idx in s2_sched:
        oid_list1.append(observations.name[obs_idx])

    unscheduled = [o for o in str_planid if o not in oid_list1]
    # unscheduled = [str(o) for o in range(observations.num_obs) if o not in final_schedule]

    if len(set(oid_list1)) > 0:
        scheduled_summary = f'\nScheduled observations: {", ".join(set(oid_list1))}'
        if out is None:
            print(scheduled_summary)
        else:
            out.write(scheduled_summary + '\n')

    if len(unscheduled) > 0:
        unscheduled_summary = f'\nUnscheduled observations: {", ".join(unscheduled)}'
        if out is None:
            print(unscheduled_summary)
        else:
            out.write(unscheduled_summary + '\n')
    site_tasks_list = []
    site_tasks_list.append(site_tasks1)
    site_tasks_list.append(site_tasks2)
    return site_tasks_list

def print_observations(obs: Observations, timeslots: TimeSlots) -> None:

    print("Observations:")
    print("Index  ObsTime Priority  StartSlots")
    for idx in range(obs.num_obs):
        prev_site = 0
        ss = []
        for slot in obs.start_slots[idx]:
            slot_idx = slot.timeslot_idx
            slot_metric = slot.metric_score
            site, site_slot = divmod(slot_idx, timeslots.num_timeslots_per_site)
            if site != prev_site:
                ss.append('  |||  ')
                prev_site = site
            ss.append(f"{Resource(site).name}{site_slot}({slot_metric})")
        print(f"{idx:>5}  {int(obs.obs_time[idx].seconds/60):>7} {obs.priority[idx]:>8}  "
              f"{' '.join(ss)}")



