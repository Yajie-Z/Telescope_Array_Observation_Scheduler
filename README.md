# A Multi-level Scheduling Framework for Distributed Time Domain Large-area Sky Survey Telescope Array

Paper: https://iopscience.iop.org/article/10.3847/1538-3881/acac24

arXiv preprint: https://arxiv.org/abs/2301.07860

We propose a multi-level scheduling model oriented towards the problem of telescope array scheduling for time-domain surveys.


- [Global Scheduler](#global)
  * [Multi-level Telescope Array Scheduling Model](#more-about-telescope-array-scheduler)
    
  * [Running](#running)
    + [Dependencies](#dependencies)
    + [Data](#data)
    + [Minimal example](#minimal-example)
  * [Community Contribution and Advice](#community-contribution-and-advice)



## More About Telecope Array Scheduler

This work was published in the Astronomical Journal, so please cite our article if you use the framework.

```latex
@article{Zhang_2023,
doi = {10.3847/1538-3881/acac24},
url = {https://dx.doi.org/10.3847/1538-3881/acac24},
year = {2023},
month = {feb},
publisher = {The American Astronomical Society},
volume = {165},
number = {3},
pages = {77},
author = {Yajie Zhang and Ce Yu and Chao Sun and Zhaohui Shang and Yi Hu and Huiyu Zhi and Jinmao Yang and Shanjiang Tang},
title = {A Multilevel Scheduling Framework for Distributed Time-domain Large-area Sky Survey Telescope Array},
journal = {The Astronomical Journal}
}

```
As shown in the following Figure, <P align="center"><img src=figs/model.png hidth="48%" width="70%"></img></p>
a multi-level scheduling model is proposed to describe the optical time domain sky survey observation process of the telescope array. The telescope array observation scheduling problem can be solved by the global scheduler and multiple site schedulers or telescope schedulers respectively. The global scheduler is designed as a long-term scheduler which acts as a central node to compute the scheduling strategies. It coordinates the telescopes of all observation sites and globally controls the progress of the sky survey and  utilization of resources. Periodically, it determines the suitable observation time of each site for each field according to the observation conditions and the image quality feedback. The preliminary scheduling results will be sent to astronomical observatories. At the same time, the global scheduler receives the execution feedback from the telescopes and makes decision changes to update and adjust the observation plans for the next scheduling coverage time for special cases (such as transient source tracking, telescope failure, poor observation quality, internet connection down, etc.). 
The proposed site scheduler and telescope scheduler, as the scheduling decision-maker for a short period of time, are responsible for allocating the tasks issued by the global scheduler to each telescope in the observation site, calculating the specific start and end time of observations with finer granularity, and determining the final observation task queue for each telescope. During this process, the effects of real-time weather conditions around the observation sites, as well as the performance and status of telescopes are taken into account in detail.Furthermore, the overall progress of the survey, that is, the completion of observation tasks, will be recorded and statistically analyzed, and important indicators will be visualized.


## Running

### Dependencies

- Astropy
- Astroplan
- Numpy
- Matplotlib
- [Gurobi](http://www.gurobi.com/) ([Free academic licenses](http://www.gurobi.com/academia/for-universities) are readily available)


## Getting Started

### Data
We provide simple test data with 2 observation sites and 50 fields in the `input_data/` directory. We used the positions of global real observatories from the Astropy library to simulate the distribution of observation sites in a distributed telescope array. You can also get more field data from [ZTF project](https://github.com/ZwickyTransientFacility/ztf_sim/blob/master/data) or generate simulated data according to specific project requirements. 


### Minimal example

1. Specify the input data and set the relevant parameters in the configuration file ( `input_data/configuration.json`)

2. Use the following command to start the scheduling:

```shell
$  python main.py
```

An open-source library from [LSST](https://github.com/lsst/rubin_sim) was utilised to evaluate the 5-sigma limiting magnitude for the scheduled observations. Note that it calculates the limiting magnitude of LSST, and the results will be different for different telescopes. Similar models can be used for the calculation of
observation conditions in the telescope array scheduling problem.

## Community Contribution and Advice

The scheduler for telescope arrays is being further improved, if you have any question or ideas, please don't skimp on your suggestions and welcome make a pull request. Moreover, you can contact us through the follow address.

- zyj0928@tju.edu.cn
