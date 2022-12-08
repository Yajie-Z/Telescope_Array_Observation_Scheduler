import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from itertools import chain

def draw_map(m,scale=0.2):
    m.shadedrelief(scale=scale)
    # lats = m.drawparallels(np.linspace(-90,90,7))
    # lons = m.drawparallels(np.linspace(-180,180,7))
    # lat_lines = chain(*(tup[1][0] for tup in lats.items()))
    # lon_lines = chain(*(tup[1][0] for tup in lons.items()))
    # all_lines = chain(lat_lines,lon_lines)
    m.drawmeridians(np.arange(-180, 181, 30), labels=[0, 0, 0, 1], fontsize=10, linewidth=0.8, color='silver')  # 经线
    m.drawparallels(np.arange(-90, 91, 30), labels=[1, 0, 0, 0], fontsize=10, linewidth=0.8, color='silver')  # 纬线


def draw_point(m,x,y,name):
    x,y = m(x,y)
    # plt.plot(x,y,marker='v',markersize = 5,color='#00BFFF')
    m.scatter(x, y, marker='v', s=88, facecolor='#00BFFF',
                edgecolor='k', linewidth=1)
    # plt.text(x,y,name,fontsize=12,color='red')

fig = plt.figure(figsize=(8,6),edgecolor='w')
m = Basemap(projection='cyl',resolution=None,llcrnrlat=-90,urcrnrlat=90,llcrnrlon=-180,urcrnrlon=180)
draw_map(m)


with open("input_data/resources-5") as f2:
    resource_location = [line.split() for line in f2][1:]
# print(resource_location)

for loc in resource_location:
    draw_point(m,float(loc[2]),float(loc[3]),loc)


plt.show()
