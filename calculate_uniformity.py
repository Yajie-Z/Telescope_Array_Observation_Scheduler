import numpy as np


# calculate the uniformity of the cumulative observation times of tasks
def obs_num_uniformity(obsrecords):
    nums = obsrecords.frequency.values()
    sd = np.std(list(nums))
    return sd

# calculate the uniformity of the accumulated observation time of the observation tasks
def obs_totaltime_uniformity(obsrecords):
    totaltimes = obsrecords.total_obstime.values()
    sd = np.std(list(totaltimes))
    return sd

# calculate the uniformity of cadence between observation tasks
def obs_cadence_uniformity(obsrecords):
    cadence_each_target = {}
    for key in list(obsrecords.obs_start_end_time.keys()):
        if key in list(cadence_each_target.keys()):
            value = obsrecords.obs_start_end_time[key]
            for i in range(1,len(value)):
                cadence_each_target[key].append(value[i][0] - value[i-1][1])

        else:
            value = obsrecords.obs_start_end_time[key]
            cadence_each_target[key] = []
            for i in range(1, len(value)):
                cadence_each_target[key].append(value[i][0] - value[i - 1][1])

    # print(cadence_each_target)

    for cadence_list in list(cadence_each_target.values()):
        item_cadence = []
        for cadence in cadence_list:
            item_cadence.append(cadence)
            obsrecords.all_cadence.append(cadence)
    # print(obsrecords.all_cadence)



