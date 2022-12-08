from output_format import *


def search_location(file,name):
    location = {}
    with open(file) as f2:
        surveyplan_input = [line.split() for line in f2][1:]
    for plan in surveyplan_input:
        locationitem = []
        locationitem.append(float(plan[1]))
        locationitem.append(float(plan[2]))
        location[int(plan[0])] = locationitem
    return location[name]


def takeSecond(ele):
    return ele[0]

class ObsRecord:
    '''
    The set of observation record which is used to collect the status of observation
    tasks sent by the global scheduler, including cadence, frequency, total observation time and etc.
    '''

    def __init__(self):
        self.ra = {}
        self.dec = {}
        self.current_round = {}
        self.frequency = {}
        self.total_obstime = {}
        self.each_obstime = {}
        self.obs_start_end_time = {}
        self.all_cadence = []
        self.obs_start_end_time_not_clear = {}
        self.status = {}

    def clear_obs_start_end_time(self):
        self.obs_start_end_time = {}

    def update_status(self):
        return


    def add_record(self,round,timeslots,observations: Observations,final_schedule: Schedule,
                   file = "input_data/surveyplan-50" ) -> None:

        oid_list = []

        sched1 = schedule_transform(final_schedule,observations,Resource.S1,timeslots)
        sched2 = schedule_transform(final_schedule, observations, Resource.S2, timeslots)

        sched = [sched1,sched2]
        for isched in sched:
            for obs_start_time_slot, obs_idx in isched:
                oid_list.append(observations.name[obs_idx])

        for name in oid_list:
            if name not in self.ra.keys():
                self.ra[name] = search_location(file,int(name))[0]
                self.dec[name] = search_location(file,int(name))[1]

            if name in self.frequency.keys():
                    self.frequency[name] += 1
            else:
                    self.frequency[name] = 1

            self.current_round[name] = round

        # print(self.frequency)

        for isched in sched:
            for obs_start_time_slot, obs_idx in isched:
                if observations.name[obs_idx] in self.total_obstime.keys():
                     self.total_obstime[observations.name[obs_idx]] += ((observations.obs_time[obs_idx].seconds) / 60)
                     self.each_obstime[observations.name[obs_idx]].append(((observations.obs_time[obs_idx].seconds) / 60))
                else:
                    self.total_obstime[observations.name[obs_idx]] = ((observations.obs_time[obs_idx].seconds) / 60)
                    self.each_obstime[observations.name[obs_idx]] = [((observations.obs_time[obs_idx].seconds) / 60)]

        # print(self.total_obstime)

        for isched in sched:
            for obs_start_time_slot, obs_idx in isched:
                tmp = []
                obs_start_time = obs_start_time_slot * timeslots.timeslot_length
                # print(obs_start_time)
                if observations.name[obs_idx] in self.obs_start_end_time.keys():
                    tmp.append(obs_start_time)
                    tmp.append(obs_start_time + observations.obs_time[obs_idx].seconds / 60)
                    self.obs_start_end_time[observations.name[obs_idx]].append(tmp)
                    # self.obs_start_end_time[observations.name[obs_idx]].append(obs_start_time+observations.obs_time[obs_idx].seconds/60)
                else:
                    self.obs_start_end_time[observations.name[obs_idx]]= []
                    tmp.append(obs_start_time)
                    tmp.append(obs_start_time+observations.obs_time[obs_idx].seconds/60)
                    self.obs_start_end_time[observations.name[obs_idx]].append(tmp)
                    # self.obs_start_end_time[observations.name[obs_idx]].append(obs_start_time+observations.obs_time[obs_idx].seconds/60)

        # print(self.obs_start_end_time)
        for i in list(self.obs_start_end_time.keys()):
            self.obs_start_end_time[i].sort(key=takeSecond)


        # not clear start and end
        for isched in sched:
            for obs_start_time_slot, obs_idx in isched:
                obs_start_time = obs_start_time_slot * timeslots.timeslot_length
                if observations.name[obs_idx] in self.obs_start_end_time_not_clear.keys():

                    self.obs_start_end_time_not_clear[observations.name[obs_idx]].append(obs_start_time)
                    self.obs_start_end_time_not_clear[observations.name[obs_idx]].append(obs_start_time + observations.obs_time[obs_idx].seconds / 60)
                else:
                    self.obs_start_end_time_not_clear[observations.name[obs_idx]]= []
                    self.obs_start_end_time_not_clear[observations.name[obs_idx]].append(obs_start_time)
                    self.obs_start_end_time_not_clear[observations.name[obs_idx]].append(obs_start_time + observations.obs_time[obs_idx].seconds / 60)


