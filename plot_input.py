import numpy as np
import matplotlib.pyplot as plt

with open('input_data/surveyplan-100') as f2:
    surveyplan_input = [line.split() for line in f2][1:]
# print(surveyplan_input)

location = []
for plan in surveyplan_input:
    location.append(float(plan[1]))
    location.append(float(plan[2]))
plan_num = len(location)



def plot_sky(RA,Dec,z,org=0,title='', projection='hammer'):
    ''' RA, Dec are arrays of the same length.
    RA takes values in [0,360), Dec in [-90,90],
    which represent angles in degrees.
    org is the origin of the plot, 0 or a multiple of 30 degrees in [0,360).
    projection is the kind of projection: 'mollweide', 'aitoff', 'hammer', 'lambert'
    '''
    x = np.remainder(RA+360-org,360) # shift RA values
    ind = x>180
    x[ind] -=360    # scale conversion to [-180, 180]
    x=-x    # reverse the scale: East to the left
    tick_labels = np.array([150, 120, 90, 60, 30, 0, 330, 300, 270, 240, 210])
    tick_labels = np.remainder(tick_labels+360+org,360)
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111, projection=projection)
    ax1 = ax.scatter(np.radians(x),np.radians(Dec),c=z,cmap='Blues')  # convert degrees to radians

    ax.set_xticklabels(tick_labels)     # we add the scale on the x axis
    ax.set_title(title)
    ax.title.set_fontsize(12)
    ax.set_xlabel("RA")
    ax.xaxis.label.set_fontsize(12)
    ax.set_ylabel("Dec")
    ax.yaxis.label.set_fontsize(12)
    ax.grid(True)
    fig.colorbar(ax1)

z = np.array([1])

for x in range(int(plan_num/2)-1):
    z = np.append(z, 1)

coord = np.zeros(shape=0)
for i in range(int(plan_num)):
    coord=np.insert(coord,i,location[i])
coord = coord.reshape(int(plan_num/2),2)

plot_sky(coord[:,0],coord[:,1], z, org=90, title ='')

plt.show()