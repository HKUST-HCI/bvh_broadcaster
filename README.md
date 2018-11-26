<<<<<<< HEAD
# BVHBroadcaster
BVHBroadcaster: broadcasting bvh motion capture as tf in ROS
=======
# bvh_broadcaster
[ROS wiki](http://wiki.ros.org/bvh_broadcaster)

bvh_broadcaster: broadcasting bvh motion capture as tf in ROS
>>>>>>> fc6a6f9091a7dad353140f9d9081b9d570421d6b

## Overview
This package broadcasts [BVH files (a motion capture data format)](https://research.cs.wisc.edu/graphics/Courses/cs-838-1999/Jeff/BVH.html) as [TF transfromations](http://wiki.ros.org/rviz/DisplayTypes/TF).

## Data input

Input contains two string parameters:

 * A path to BVH file, e.g., [example.bvh](https://research.cs.wisc.edu/graphics/Courses/cs-838-1999/Jeff/Example1.bvh)
 * A name of frame for motion capture to be loaded on, e.g., "world" frame, or "odom" frame.

<<<<<<< HEAD
You can find relevant BVH-formatted CMU MoCap from [this post](https://github.com/mingfeisun/BVHBroadcaster/blob/master/cmu_mocap_bvh.md). Get BVH-formatted motion capture data from [here](http://www.cgspeed.com/).
=======
You can find relevant BVH-formatted CMU MoCap from [this post](https://github.com/mingfeisun/bvh_broadcaster/blob/master/cmu_mocap_bvh.md). Get BVH-formatted motion capture data from [here](http://www.cgspeed.com/).
>>>>>>> fc6a6f9091a7dad353140f9d9081b9d570421d6b

## Usage

``` shell
<<<<<<< HEAD
python BVHBroadcaster.py [-h] [-n NAME] [-l] bvh_file base_frame
=======
python bvh_broadcaster.py [-h] [-n NAME] [-l] bvh_file base_frame
>>>>>>> fc6a6f9091a7dad353140f9d9081b9d570421d6b

positional arguments:
  bvh_file              A path to bvh file that you want to broadcast
  base_frame            An existing frame in rviz on which the skeleton will
                        be loaded

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Node name, default: BVHBroadcaster
  -l, --loop            Loop broadcasting
```

For example:
``` shell
# add execution access
<<<<<<< HEAD
chmod +x scripts/BVHBroadcaster.py
# loop broadcasting bvh to world frame
python BVHBroadcaster.py ../example/13_14.bvh world -l
=======
chmod +x scripts/bvh_broadcaster.py
# loop broadcasting bvh to world frame
python bvh_broadcaster.py ../example/13_14.bvh world -l
>>>>>>> fc6a6f9091a7dad353140f9d9081b9d570421d6b
```


## BVH resources for Motion Capture
<<<<<<< HEAD
CMU provides a lot of useful motion capture data, see [CMU MoCap](http://mocap.cs.cmu.edu/). Nevertheless, these data are not presented in BVH format. You can find relevant BVH-formatted CMU MoCap from [this post](https://github.com/mingfeisun/BVHBroadcaster/blob/master/cmu_mocap_bvh.md).
=======
CMU provides a lot of useful motion capture data, see [CMU MoCap](http://mocap.cs.cmu.edu/). Nevertheless, these data are not presented in BVH format. You can find relevant BVH-formatted CMU MoCap from [this post](https://github.com/mingfeisun/bvh_broadcaster/blob/master/cmu_mocap_bvh.md).
>>>>>>> fc6a6f9091a7dad353140f9d9081b9d570421d6b
