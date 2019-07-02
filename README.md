### MACAD-Gym

Multi-Agent Connected Autonomous Driving (MACAD) learning platform using CARLA Autonomous Driving simulator.

### Usage guide

1. [Getting Started](#getting-started)
1. [Installation](#installation)
1. [Developer Contribution Guide](README.md#developer-contribution-guide)
1. [Notes for Gym wrappers for CARLA 0.8.x (stable) versions](README.md#notes)


### Getting Started

> Assumes an Ubuntu (16.04/18.04 or later) system.

1. Install the system requirements:
	- Miniconda/Anaconda 3.x
		- `wget -P ~ https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh; bash ~/Miniconda3-latest-Linux-x86_64.sh`
	- cmake (`sudo apt install cmake`)
	- zlib (`sudo apt install zlib1g-dev`)
	- [optional] ffmpeg (`sudo apt install ffmpeg`)
    
3. Setup CARLA (0.9.x)

    3.1 `mkdir ~/software && cd ~/software`

    3.2 Example: Download the 0.9.4 release version from: [Here](https://drive.google.com/file/d/1p5qdXU4hVS2k5BOYSlEm7v7_ez3Et9bP/view)
    Extract it into `~/software/CARLA_0.9.4`
    
    3.3 `echo "export CARLA_SERVER=${HOME}/software/CARLA_0.9.4/CarlaUE4.sh" >> ~/.bashrc`
    
	
### Installation

 - Option1 for users: `pip install git+https://github.com/praveen-palanisamy/macad-gym.git`
 - Option2 for developers:
     - Fork/Clone the repository to your workspace:
    `git clone https://github.com/praveen-palanisamy/macad-gym.git`
    `cd macad-gym`
     - Create a new conda env named "macad-gym" and install the required packages:
      `conda env create -f conda_env.yaml`
     - Activate the `macad-gym` conda python env:
      `source activate carla-gym`
     - Install CARLA PythonAPI:
     > NOTE: Change the carla pip package version number below to match with your CARLA server version
      `pip install carla==0.9.4` (or `easy_install carla*.egg`)


#### Running scenarios (standalone)

`python env/envs/intersection/urban_signal_intersection_1b2c1p.py`

##### Config docs:
```json
{
    "actors": {
            "car1": {
                "type": "vehicle_4W",
                "enable_planner": true,
                "convert_images_to_video": false,
                "early_terminate_on_collision": true,
                "reward_function": "corl2017",
                "scenarios": "SSUI3C_TOWN3_CAR1",
                "manual_control": false,
                "auto_control": false,
                "camera_type": "rgb",
                "collision_sensor": "on",
                "lane_sensor": "on",
                "log_images": false,
                "log_measurements": false,
                "render": true,
                "x_res": 84,  --> Observation dimension along x (height)
                "y_res": 84,  --> Observation dimension along y (width)
                "use_depth_camera": false,
                "send_measurements": false
            }
            }
}
```

### Contribution Guide

- Be sure to `source activate macad-gym` before developing/testing
- Be sure to `git pull` often to make sure you are working on the latest copy
- Follow [PEP8 coding standards](https://www.python.org/dev/peps/pep-0008/) and [Google style](http://google.github.io/styleguide/pyguide.html). Before pushing your local commits, Run `bash .ci/format_code.sh`, this will reformat the files you have changed to automatically make them follow the recommended standard and show you the list of updated file. Review the changes and if all looks good, stage them again and then push
  - You can also auto format specific files using this command: `bash .ci/format_code.sh --files <PATH_TO_FILE1> <PATH_TO_FILE2>`
- Make sure the CI pipeline reports success. If not, please look at the CI run's log file, fix the reported errors

### **NOTEs**:
> MACAD-Gym is for CARLA 0.9.x . If you are
looking for an OpenAI Gym-compatible agent learning environment for CARLA 0.8.x (stable release),
use [this carla_gym environment](https://github.com/PacktPublishing/Hands-On-Intelligent-Agents-with-OpenAI-Gym/tree/master/ch8/environment).
