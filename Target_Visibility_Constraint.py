import datetime
from math import ceil
from astroplan import Observer
import astropy.units as u
from astropy.coordinates import EarthLocation
from astropy.time import Time
from astropy.coordinates import SkyCoord
from astroplan import FixedTarget
from astropy.coordinates import Angle
from astropy.time import Time
from configuration import Configuration
from Timeslots import *
import time
import pandas as pd
from ObsRecords import *
from astropy.coordinates import Angle


def makezero(resourcelist):
    length = len(resourcelist)
    resourcelist.clear()
    for x in range(length):
        resourcelist.append(0)
    return resourcelist

# simulate the observation facilities
def get_observer(index:int, obs_ra: float, obs_dec: float, elevation: float) -> list:
    location = EarthLocation.from_geodetic(obs_ra * u.deg, obs_dec * u.deg, elevation * u.m)
    observer = Observer(location=location)
    observer_list = []
    observer_list.append(index)
    observer_list.append(observer)
    return observer_list

# simulated the observation field, whose position is represented by the center position of the field
def get_target(index:int, target_ra: float, target_dec: float) -> list:
    coordinates = SkyCoord(target_ra * u.deg , target_dec * u.deg, frame='icrs')
    target = FixedTarget(coord=coordinates)
    target_list = []
    target_list.append(index)
    target_list.append(target)
    return target_list


# calculate the available observation time for each specific pair of the field and telescope
def get_observable_time_window(observer: Observer, target: FixedTarget, time:Time, which: str) -> list:
    window = []
    rise= observer.target_rise_time(time,target,which=which)
    set = observer.target_set_time(time,target,which=which)
    # print(rise)
    target_rise = rise + 5*u.minute
    target_set = set - 5*u.minute
    sunset = observer.sun_set_time(time, which=which)
    sunrise = observer.sun_rise_time(time,which=which)
    # start = np.max([sunset, target_rise]).iso
    start = np.max([sunset,target_rise])
    end = np.min([sunrise,target_set])
    window.append(start)
    window.append(end)
    return window

#set constraints according to the specific survey project
# can change to other astronomical observation constraints (sun,moon,etc)
def alt_constraint(observer,target,window:list):
    window_result =[]
    for x in range(len(window)):
        t = pd.to_datetime(str(window[x]))
        convert_time = Time(t.strftime("%Y-%m-%d %H:%M:%S"))
        target_altaz = observer.altaz(convert_time, target)

        if target_altaz.alt > 0 and float(observer.altaz(convert_time, target).secz) < 2.5:
            window_result.append(window[x])
    return window_result


# a metric score designed for fields to optimize the sky coverage uniformity
def get_next_score(record:ObsRecord,index,start_time, current_time,observer,target,convert_time,lamda = 1):

    if index in list(record.total_obstime.keys()):
        obs_time = record.total_obstime[index]
        obs_frequency = record.frequency[index]
        obs_lastend_time = record.obs_start_end_time_not_clear[index][-1]
        print(current_time)
        print(obs_lastend_time)
        print(current_time-obs_lastend_time)
        # the score is proportional to the time interval since the last observation of the field
        up = lamda * (current_time - obs_lastend_time)
        down = obs_time * obs_frequency
        airmass = observer.altaz(convert_time, target).secz
        score_function = 1 / obs_frequency

        return score_function

    else:
        # if the field has not been observed before
        # the score is proportional to the time interval since the start time of the survey
        # thus give a high priority
        score_function = 1
        return score_function


def target_visibility(round,resource_input,surveyplan_input,priorities,survey_start_time,anight_observation_end222,a_timeslot_length,obs,timeslots,obsrecords):

    # for each pair of field and observation site
    for obs_id in range(1, len(surveyplan_input) + 1):
        tar = get_target(int(surveyplan_input[obs_id - 1][0]), float(surveyplan_input[obs_id - 1][1]),
                         float(surveyplan_input[obs_id - 1][2]))
        for res_id in range(1, len(resource_input) + 1):
            observation = get_observer(int(resource_input[res_id - 1][0]), float(resource_input[res_id - 1][2]),
                                       float(resource_input[res_id - 1][3]), float(resource_input[res_id - 1][4]))
            try:
                window = get_observable_time_window(observation[1], tar[1], survey_start_time, "next")
                start = min(window[0], window[1])

                start_datetime = datetime.datetime(*time.strptime(start.iso.split(".")[0], "%Y-%m-%d %H:%M:%S")[:6])
                end = max(window[0], window[1])
                end_datetime = min(datetime.datetime(*time.strptime(end.iso.split(".")[0], "%Y-%m-%d %H:%M:%S")[:6]),
                                   anight_observation_end222)

                tmp = np.arange(start_datetime, end_datetime, datetime.timedelta(minutes=a_timeslot_length))
                tmp3 = np.arange(
                    datetime.datetime(*time.strptime(survey_start_time.iso.split(".")[0], "%Y-%m-%d %H:%M:%S")[:6])
                    , anight_observation_end222, datetime.timedelta(minutes=a_timeslot_length))

                global thestart,theend
                for i in range(len(list(tmp3))-1):
                    if tmp3[i] < tmp[0] and tmp[0] <= tmp3[i+1]:
                        thestart = tmp3[i+1]
                    if  tmp3[i] and tmp[-1]< tmp3[i+1]:
                        theend = tmp3[i]


                tmp2 = np.arange(thestart, theend,datetime.timedelta(minutes=a_timeslot_length))

                tmp2 = alt_constraint(observation[1],tar[1],tmp2)
                start_slot_list = list(tmp2)
                

                adjusted_list_len = max(0, len(start_slot_list) - int(ceil(5 / 5)))
                start_slot_list = start_slot_list[0:adjusted_list_len]

                tmp_list = list(tmp3)
                if res_id == 1:
                    resourcelist = []
                    for x in range(288):
                        resourcelist.append(0)

                    start_slot_list_num = []
                    for x in start_slot_list:
                        for i in range(len(tmp_list)):
                            if str(x) == str(tmp_list[i]):
                                start_slot_list_num.append(i)
                    print("[1]")
                    # print(start_slot_list_num)
                    for x in start_slot_list_num:
                            resourcelist[int(x)]=1


                    resource = Resource.S1
                    obs_length = datetime.timedelta(minutes=a_timeslot_length) * 1
                    iobs_length = a_timeslot_length * 1

                    if round == 1:
                        obs.add_obs(int(surveyplan_input[obs_id - 1][0]), resource,
                                    [TS(idx, idx, idx + iobs_length,1) for idx in start_slot_list_num], obs_length, 1)
                    else:

                        obs.add_obs(int(surveyplan_input[obs_id-1][0]), resource,
                                    [TS(idx,idx,idx+iobs_length,  get_next_score(obsrecords, str(int(surveyplan_input[obs_id - 1][0])), datetime.datetime(
                            *time.strptime(survey_start_time.iso.split(".")[0], "%Y-%m-%d %H:%M:%S")[
                             :6]),1440*(round-1)+(idx-1)*a_timeslot_length,observation[1],tar[1],survey_start_time + (idx-1)*a_timeslot_length)
                                        ) for idx in start_slot_list_num], obs_length,1)

                if res_id == 2:
                    resourcelist = []
                    for x in range(288):
                        resourcelist.append(0)

                    start_slot_list_num2 = []
                    for x in start_slot_list:
                        for i in range(len(tmp_list)):
                            if str(x) == str(tmp_list[i]):
                                start_slot_list_num2.append(i)

                    print("[2]")

                    for x in start_slot_list_num2:
                        resourcelist[int(x)] = 1
                    # print(resourcelist)

                    resource = Resource.S2
                    obs_length = datetime.timedelta(minutes=a_timeslot_length) * 1
                    iobs_length = a_timeslot_length * 1

                    if round == 1:
                        obs.add_obs(int(surveyplan_input[obs_id - 1][0]), resource,
                                    [TS(idx + timeslots.num_timeslots_per_site, idx + timeslots.num_timeslots_per_site,
                                        idx + timeslots.num_timeslots_per_site + iobs_length,1)
                                     for idx in start_slot_list_num2], obs_length, 1)
                    else:
                        obs.add_obs(int(surveyplan_input[obs_id-1][0]), resource,
                                [TS(idx + timeslots.num_timeslots_per_site,idx + timeslots.num_timeslots_per_site,
                                idx + timeslots.num_timeslots_per_site+iobs_length,
                                    get_next_score(obsrecords, str(int(surveyplan_input[obs_id - 1][0])), datetime.datetime(
                                        *time.strptime(survey_start_time.iso.split(".")[0], "%Y-%m-%d %H:%M:%S")[
                                         :6]), 1440*(round-1)+(idx-1)*a_timeslot_length,observation[1],tar[1],survey_start_time + (idx-1)*a_timeslot_length))
                                 for idx in start_slot_list_num2], obs_length, 1)


                if res_id == 3:
                    resourcelist = []
                    for x in range(288):
                        resourcelist.append(0)

                    start_slot_list_num3 = []
                    for x in start_slot_list:
                        for i in range(len(tmp_list)):
                            if str(x) == str(tmp_list[i]):
                                start_slot_list_num3.append(i)

                    print("[3]")

                    for x in start_slot_list_num3:
                        resourcelist[int(x)] = 1
                    # print(resourcelist)

                    resource = Resource.S3
                    obs_length = datetime.timedelta(minutes=a_timeslot_length) * 1
                    iobs_length = a_timeslot_length * 1

                    if round == 1:
                        obs.add_obs(int(surveyplan_input[obs_id - 1][0]), resource,
                                    [TS(idx + timeslots.num_timeslots_per_site*2, idx + timeslots.num_timeslots_per_site*2,
                                        idx + timeslots.num_timeslots_per_site*2 + iobs_length,1)
                                     for idx in start_slot_list_num3], obs_length, 1)
                    else:
                        obs.add_obs(int(surveyplan_input[obs_id-1][0]), resource,
                                [TS(idx + timeslots.num_timeslots_per_site*2,idx + timeslots.num_timeslots_per_site*2,
                                idx + timeslots.num_timeslots_per_site*2+iobs_length,
                                    get_next_score(obsrecords, str(int(surveyplan_input[obs_id - 1][0])), datetime.datetime(
                                        *time.strptime(survey_start_time.iso.split(".")[0], "%Y-%m-%d %H:%M:%S")[
                                         :6]), 1440*(round-1)+(idx-1)*a_timeslot_length,observation[1],tar[1],survey_start_time + (idx-1)*a_timeslot_length))
                                 for idx in start_slot_list_num3], obs_length, 1)


                if res_id == 4:
                    resourcelist = []
                    for x in range(288):
                        resourcelist.append(0)

                    start_slot_list_num4 = []
                    for x in start_slot_list:
                        for i in range(len(tmp_list)):
                            if str(x) == str(tmp_list[i]):
                                start_slot_list_num4.append(i)

                    print("[4]")
                    for x in start_slot_list_num4:
                        resourcelist[int(x)] = 1
                    # print(resourcelist)

                    resource = Resource.S4
                    obs_length = datetime.timedelta(minutes=a_timeslot_length) * 1
                    iobs_length = a_timeslot_length * 1

                    if round == 1:
                        obs.add_obs(int(surveyplan_input[obs_id - 1][0]), resource,
                                    [TS(idx + timeslots.num_timeslots_per_site * 3,
                                        idx + timeslots.num_timeslots_per_site * 3,
                                        idx + timeslots.num_timeslots_per_site * 3 + iobs_length, 1)
                                     for idx in start_slot_list_num4], obs_length, 1)
                    else:
                        obs.add_obs(int(surveyplan_input[obs_id - 1][0]), resource,
                                    [TS(idx + timeslots.num_timeslots_per_site * 3,
                                        idx + timeslots.num_timeslots_per_site * 3,
                                        idx + timeslots.num_timeslots_per_site * 3 + iobs_length,
                                        get_next_score(obsrecords, str(int(surveyplan_input[obs_id - 1][0])),
                                                       datetime.datetime(
                                                           *time.strptime(survey_start_time.iso.split(".")[0],
                                                                          "%Y-%m-%d %H:%M:%S")[
                                                            :6]), 1440 * (round - 1) + (idx - 1) * a_timeslot_length,observation[1],tar[1],survey_start_time + (idx-1)*a_timeslot_length))
                                     for idx in start_slot_list_num4], obs_length, 1)
                if res_id == 5:
                    resourcelist = []
                    for x in range(288):
                        resourcelist.append(0)

                    start_slot_list_num5 = []
                    for x in start_slot_list:
                        for i in range(len(tmp_list)):
                            if str(x) == str(tmp_list[i]):
                                start_slot_list_num5.append(i)

                    print("[5]")

                    for x in start_slot_list_num5:
                        resourcelist[int(x)] = 1
                    # print(resourcelist)

                    resource = Resource.S5
                    obs_length = datetime.timedelta(minutes=a_timeslot_length) * 1
                    iobs_length = a_timeslot_length * 1

                    if round == 1:
                        obs.add_obs(int(surveyplan_input[obs_id - 1][0]), resource,
                                    [TS(idx + timeslots.num_timeslots_per_site * 4,
                                        idx + timeslots.num_timeslots_per_site * 4,
                                        idx + timeslots.num_timeslots_per_site * 4 + iobs_length, 1)
                                     for idx in start_slot_list_num5], obs_length, 1)
                    else:
                        obs.add_obs(int(surveyplan_input[obs_id - 1][0]), resource,
                                    [TS(idx + timeslots.num_timeslots_per_site * 4,
                                        idx + timeslots.num_timeslots_per_site * 4,
                                        idx + timeslots.num_timeslots_per_site * 4 + iobs_length,
                                        get_next_score(obsrecords, str(int(surveyplan_input[obs_id - 1][0])),
                                                       datetime.datetime(
                                                           *time.strptime(survey_start_time.iso.split(".")[0],
                                                                          "%Y-%m-%d %H:%M:%S")[
                                                            :6]), 1440 * (round - 1) + (idx - 1) * a_timeslot_length,observation[1],tar[1],survey_start_time + (idx-1)*a_timeslot_length))
                                     for idx in start_slot_list_num5], obs_length, 1)


            except TypeError:
                window = [0, 0]
                # uncount += 1
