import datetime
from astropy.time import Time
from Target_Visibility_Constraint import target_visibility
from configuration import Configuration
from gurobi_solver import *
from plot_footprint import *
from calculate_uniformity import *
import time

if __name__ == '__main__':
    time_start = time.time()
    solver_time_start = 0
    solver_time_end = 0
    preprocess_end = 0
    site_start_time = 0
    site_end_time = 0
    f = open("log2x50.txt", 'w')

    # initialize the record of the completion of tasks
    obsrecords = ObsRecord()

    round = 1
    config = Configuration('input_data/configuration.json')

    #read the input simulated telescope facilities and fields
    with open(config.default_input_resource) as ff:
        resource_input = [line.split() for line in ff][1:]

    with open(config.default_input_surveyplan) as f2:
        surveyplan_input = [line.split() for line in f2][1:]

    survey_start_time = config.survey_start_time
    anight_observation_length = datetime.timedelta(hours=config.default_scheduling_block_length)
    a_timeslot_length = config.default_timeslot_length

    # execution priorities of fields set by astronomers before the survey
    # astronomers may wish to focus on certain fields and increase their frequency of observations
    priorities = [row[4] for row in surveyplan_input]

    survey_start_time_cp = config.survey_start_time

    while (survey_start_time < config.survey_end_time):

        anight_observation_end222 = datetime.datetime(
            *time.strptime(str(survey_start_time).split(".")[0], "%Y-%m-%d %H:%M:%S")[:6]) \
                                    + anight_observation_length

        # Creat the timeslots: there should be 288, each of 5 minutes.
        timeslots = TimeSlots(a_timeslot_length, 288)

        # Create the observations
        obs = Observations()

        # Calculate the available observations considering all observation conditions
        target_visibility(round,resource_input,surveyplan_input,priorities,survey_start_time,anight_observation_end222,a_timeslot_length,obs,timeslots,obsrecords)
        preprocess_end = time.time()
        # print("The pre-pocessing time is " + str(preprocess_end - time_start) + "s.")
        print_observations(obs, timeslots)

        # the basic scheduling algorithm which can be replaced or further improved
        solver_time_start = time.time()
        final_schedule, final_score = schedule(timeslots, obs)
        solver_time_end = time.time()

        # result of the global scheduler
        site_tasks_list = print_schedule(timeslots, obs, final_schedule, final_score,f)

        # the scheduling result of the global scheduler
        print(final_schedule)

        # storage the completion of observation tasks
        obsrecords.add_record(round, timeslots, obs, final_schedule)
      
        obs_cadence_uniformity(obsrecords)
       
        obsrecords.clear_obs_start_end_time()


        survey_start_time = survey_start_time_cp + round * anight_observation_length
        round += 1

    time_end = time.time()

    print("The pre-pocessing time is " + str(preprocess_end - time_start) + "s.")
    print("The center solver time is " + str(solver_time_end - solver_time_start) + "s.")
    print("The total time is " + str(time_end - time_start) + "s.")

    # survey progress visualization
    # plot_frequency(obsrecords)
    plot_obstime(obsrecords)

    f.close()

    print()
    # statistics and evaluations
    num_uniformity = obs_num_uniformity(obsrecords)
    time_uniformity = obs_totaltime_uniformity(obsrecords)

    l1 = "The uniformity of observation frequency is " + str(num_uniformity)
    l2 = "The uniformity of observation time is " + str(time_uniformity)
    l3 = "The uniformity of cadence are " + str(np.std(obsrecords.all_cadence))

    print(l1)
    print(l2)
    print(l3)
