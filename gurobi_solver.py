from __future__ import print_function
from math import ceil
from time import monotonic
from gurobipy import *
from output_format import *


def schedule(timeslots: TimeSlots, observations: Observations, out = None) -> Tuple[Schedule, Score]:

    if out is None:
        print(f"*** Building model...")
    else:
        out.write(f"*** Building model...\n")
    start_time = monotonic()

    enumerated_timeslots = list(enumerate(timeslots))

    # Create the MIP solver.
    solver = Model('global_scheduler')
    solver.Params.OutputFlag = 0
    solver.Params.MIPGap = 0.0001
    solver.Params.Method = 3
    solver.update()

    # *** DECISION VARIABLES ***
    # Create the decision variables, Y_is: observation i can start in start slot s.
    y = []
    for obs_idx in range(observations.num_obs):
        yo = {ss.timeslot_idx: solver.addVar(vtype=GRB.BINARY, name=('y_%d_%d' % (obs_idx, ss.timeslot_idx)))
              for ss in observations.start_slots[obs_idx]}
        y.append(yo)
        solver.update()

    # *** CONSTRAINTS ***
    for timeslot_idx, timeslot in enumerated_timeslots:

        expression = 0
        for obs_idx in range(observations.num_obs):
            # For each possible start slot for this observation:
            for ss in observations.start_slots[obs_idx]:
                startslot_idx = ss.timeslot_idx

                if startslot_idx <= timeslot_idx < startslot_idx + \
                        int(ceil((observations.obs_time[obs_idx].seconds/60) / timeslots.timeslot_length)):
                    expression += y[obs_idx][startslot_idx]
        solver.addConstr(expression <= 1)

    # Create the objective function.
    solver.setObjectiveN(sum([observations.priority[obs_idx] * y[obs_idx][ss.timeslot_idx]
                              * (observations.obs_time[obs_idx].seconds/60)  / \
                         (timeslots.timeslot_length * timeslots.num_timeslots_per_site)
                              for obs_idx in range(observations.num_obs)
                              for ss in observations.start_slots[obs_idx]]), 0,1)

    solver.setObjectiveN(sum([observations.priority[obs_idx] * y[obs_idx][ss.timeslot_idx]
                              * ss.metric_score
                              for obs_idx in range(observations.num_obs)
                              for ss in observations.start_slots[obs_idx]]), 1,0)

    solver.ModelSense = GRB.MAXIMIZE

    solver.update()

    time_expr = f"*** Model complete: {monotonic() - start_time} s"
    if out is None:
        print(time_expr)
    else:
        out.write(time_expr + '\n')

    start_time = monotonic()
    if out is None:
        print("*** Solving model...")
    else:
        out.write("*** Solving model...\n")
    solver.optimize()

    time_expr = f"*** Model solved: {monotonic() - start_time} s"
    if out is None:
        print(time_expr)
    else:
        out.write(time_expr + '\n')

    if out is None:
        print("*** Translating model...")
    else:
        out.write("*** Translating model...\n")

    start_time = monotonic()
    schedule_score = solver.getObjective().getValue()

    final_schedule = [None] * (timeslots.num_timeslots_per_site * 2)
    for timeslot_idx in range(timeslots.num_timeslots_per_site * 2):
        for obs_idx in range(observations.num_obs):

            if timeslot_idx in y[obs_idx] and y[obs_idx][timeslot_idx].X == 1.0:
                for i in range(int(ceil((observations.obs_time[obs_idx].seconds/60) / timeslots.timeslot_length))):
                    final_schedule[timeslot_idx + i] = obs_idx

    time_expr = f"*** Translation done: {monotonic() - start_time} s"
    if out is None:
        print(time_expr)
    else:
        out.write(time_expr + '\n')

    return final_schedule, schedule_score
