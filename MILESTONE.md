# Milestone 1: wheeled robot drives, navigates and explores a space (simulation)

## Project goal
Build a wheeled robot that can move around and explore an unknown space.
Simulation first (Gazebo with ROS 2), real hardware after the simulation works.

## Setup
- Folder: `~/robotic-projects`
- Everything runs inside one Podman container: ROS 2 Jazzy, Gazebo Harmonic, Nav2, slam_toolbox, RViz.
  Image: `ros/docker/Dockerfile` (tag `ros-gz-vnc:jazzy`). Desktop in the browser at http://localhost:6080 (password `ubuntu`).
  Start with `podman start ros-gz`. `ros/worlds`, `ros/launch` and `ros/config` are mounted at `/opt/sim/`.
  Podman VM has 8 GB RAM. The container needs `--sysctl net.ipv4.ip_unprivileged_port_start=0`.
- Why a container: Gazebo's 3D window does not render in the native macOS (RoboStack) build, so that setup was removed.
- Mac, no CUDA, software rendering in the container.

## Scope of milestone 1
A differential-drive base in a room with walls and obstacles. It drives under `/cmd_vel` commands, builds a map with
lidar SLAM, navigates to goals, and explores the room. It is also where you learn the ROS 2 basics that the hardware
milestones need. No RL and no camera-based perception yet (range sensing only).

Out of scope for now: arm, gripper, cloth or any object manipulation, learned perception, real hardware.

## Steps
Status: done / in progress / not started.

1. **Drive the wheeled base.** *Status: done, partly checked.* A differential-drive base in Gazebo (`ros/worlds/room.sdf`)
   driven by `/cmd_vel`, with `/odom`.
   Check: wheel velocities drive straight and turn in place, and the measured pose matches the command within a set tolerance.
   So far: straight drive and a turn were tried. A tolerance was never measured, and arcs were not tried.
2. **Map with lidar SLAM.** *Status: done, partly checked.* A simulated 2D lidar on `/scan`, bridged to ROS 2, with `slam_toolbox`.
   Check: a scripted drive builds a map that matches the room size, saved as an image.
   So far: a 157x157 cell map (about 7.85 m) was built. It was not saved as an image.
3. **ROS 2 basics in Python.** *Status: not started.* Write your own nodes with `rclpy`: a publisher, a subscriber, and a node that
   reads `/scan` and publishes `/cmd_vel` (for example, stop before a wall).
   Check: the node drives the robot to stop 0.5 m from a wall in 5 of 5 runs.
   This needs a code folder mounted into the container (for example `ros/scripts`), which does not exist yet.
4. **TF, time and QoS.** *Status: not started.* Draw the TF tree with `ros2 run tf2_tools view_frames`, add a static transform by hand,
   and explain `use_sim_time` and QoS settings in your own words.
   Check: a short note in `README.md` and a working custom transform.
5. **Navigate to a goal.** *Status: in progress, blocked.* Nav2 starts, but goals abort with `NO_VALID_PATH` (error 208).
   Findings so far: the lidar saw the floor when the robot tilted, which filled the costmap with false obstacles.
   I raised the lidar and added a front caster. That reduced the bad rays (88 to 11) but I did not confirm goals now work.
   Fix Nav2, or write a small navigator of your own.
   Check: the base reaches 10 random goals without collisions.
6. **Explore the space.** *Status: not started.* Pick frontiers on the map and drive to them until the map is complete.
   Check: at least 90% of the free area is mapped, and the map is saved as an image.
7. **Randomize.** *Status: not started.* Vary room layout, obstacle positions and start pose.
   Check: exploration success rate over 50 runs, recorded in a table.

## Done when
Steps 1-7 pass and a short video of an exploration run is saved.

## Risks (milestone 1)
- Sim-to-real gaps in wheel slip and sensor noise.
- Nav2 has many settings and is hard to debug. Goals currently abort with `NO_VALID_PATH`; see `README.md`.

---

# Milestone 2: lidar on a Raspberry Pi with ROS 2 (hardware, no wheels yet)

## Goal
Learn how a real sensor gets into ROS 2. A 2D lidar on a Raspberry Pi 5 publishes `/scan`, and you view
and use it from your Mac. The robot does not move yet; carry or push it by hand.

## Before you start
Milestone 1 steps 3 and 4 (ROS 2 basics in Python, TF, time and QoS) are the background for this milestone.

## Parts to choose (not decided yet)
- Raspberry Pi 5, 8 GB, with a fan or heatsink, a 5 V / 5 A power supply and a microSD card or SSD.
- A 2D lidar with a ROS 2 driver (for example an RPLIDAR or LDROBOT/LD-series model; check the driver supports Jazzy on arm64).

## Steps
1. **Install ROS 2 Jazzy on the Pi.** Ubuntu 24.04 on the Pi, then ROS 2 Jazzy in a container or natively.
   Check: `ros2 topic list` works, and a talker on the Pi is heard by a listener on your Mac container over Wi-Fi
   (this needs matching `ROS_DOMAIN_ID` and working DDS discovery, which may take some debugging).
2. **Bring up the lidar.** Install its driver, set the USB device permissions, and start the node.
   Check: `/scan` publishes at the lidar's stated rate, and `ros2 topic hz /scan` matches it.
3. **View the data.** Open `/scan` in RViz on your Mac with the right frame.
   Check: you can see the walls of the room in the scan, and the picture changes as you move the robot by hand.
4. **Record a bag.** Record `/scan` (and `/tf`) with `ros2 bag` while walking the lidar around a room.
   Check: the bag replays on your Mac.
5. **Map by hand.** Run `slam_toolbox` on the bag, or live on the Pi, with only the lidar (no wheel odometry).
   Check: a recognizable map of one room, saved as an image. Note where it drifts or fails.

## Done when
Steps 1-5 pass and you can explain which node publishes `/scan`, in which frame, and at what rate.

## Risks
- DDS discovery between the Pi and your Mac over Wi-Fi is a common source of problems.
- Lidar-only SLAM without odometry drifts in long corridors or empty rooms.
- The Pi may get hot or slow if SLAM and RViz both run on it. Run RViz on your Mac.

---

# Milestone 3: ESP32 and wheels with the Pi (hardware, the robot drives)

## Goal
Make the robot move under ROS 2. An ESP32-class microcontroller runs the motors and reads the wheel encoders;
the Pi runs ROS 2 and sends it velocity commands. Wheel odometry and the lidar then feed SLAM.

## Parts to choose (not decided yet)
- A microcontroller board (a Nano ESP32, a generic ESP32 dev board or a Raspberry Pi Pico).
- Two DC gear motors with encoders, wheels and a caster, a motor driver, and a battery with a regulator for the Pi.
- A chassis for the Pi, the lidar and the battery.

## Steps
1. **Spin one motor.** Firmware that sets a motor's speed from a serial command.
   Check: speed commands from a laptop over USB serial run the motor forward and backward.
2. **Read the encoders.** Count encoder pulses with the hardware pulse counters.
   Check: one full wheel turn by hand gives the expected count, within 1%.
3. **Wheel speed control.** A PID loop on the microcontroller holds a wheel at a set speed.
   Check: the measured speed stays within 5% of the target under load.
4. **Serial protocol.** Define a simple protocol: wheel speed commands in, encoder counts out, and a stop if no command arrives for 0.5 s.
   Check: unplugging the Pi's cable stops the motors.
5. **ROS 2 driver node on the Pi.** A node that turns `/cmd_vel` into wheel speeds, and encoder counts into `/odom` and the `odom` -> `base` transform.
   Check: a `/cmd_vel` of 0.2 m/s drives the real robot straight, and `/odom` travels 1.0 m in 5 s within 5%.
6. **Calibrate.** Measure the wheel radius and the wheel separation by driving a known distance and turning a known angle.
   Check: a 1 m square driven by teleop returns within 10 cm of the start.
7. **Drive and map.** Run `slam_toolbox` with wheel odometry and the lidar, and drive the robot around a room by teleop.
   Check: a clean map of a room, compared with a map made without odometry (milestone 2 step 5).

## Done when
Steps 1-7 pass and a short video of the robot driving and building a map is saved.

## Risks
- Wheel slip and an inaccurate wheel separation make odometry drift. Calibration matters.
- Motor noise can reset or confuse the microcontroller, and the Pi can brown out on a weak power supply.
- Moving from the simulator to the real robot means retuning Nav2 and SLAM settings.

---

# Milestone 4: the robot localizes and maps with cameras (visual SLAM)

## Goal
Replace the lidar with a stereo or RGB-D camera, build a map with visual SLAM, and learn the ROS 2 pieces
needed on the way. The lidar map from milestone 1 (and the real lidar from milestones 2 and 3) is the baseline to compare against.

## Scope
Simulation first. Real hardware (RGB-D camera such as RealSense or OAK-D) comes after the simulated version works,
and builds on the Pi and the wheeled robot from milestones 2 and 3. Manipulation is out of scope; it moves to milestone 5.

## Steps
1. **Cameras in the sim.** Add a stereo pair or `rgbd_camera` to the robot, bridge the images and `CameraInfo`
   to ROS 2, and give the room textured walls and floor (visual SLAM needs image features).
   Check: images show in RViz or `rqt_image_view`, and measured depth matches the lidar range within about 10%.
2. **Record data.** Record a drive with `ros2 bag` (images, `/odom`, `/scan`, `/tf`).
   Check: replaying the bag reproduces the same SLAM result.
3. **Visual odometry.** Run RTAB-Map in visual odometry mode, then add a simulated IMU and fuse it
   with `robot_localization`.
   Check: you can name the motions that make tracking fail (fast turns, blank walls), and the IMU reduces drift on them.
4. **Visual SLAM.** Run RTAB-Map with stereo or RGB-D and compare its pose and map to the lidar's.
   Check: trajectory error against the lidar-based pose is recorded in a table, and loop closures are visible in RViz.
5. **Navigate on the visual map.** Feed the camera depth to Nav2 (depth to laser scan, or a voxel layer) and reach goals
   without the lidar.
   Check: 8 of 10 goals reached without collisions using the camera only.
6. **Optional: ORB-SLAM3.** Try it to see how a feature-based system works. Expect extra setup.
   Check: it runs on the same bag, and its trajectory is added to the comparison table.

## Done when
Steps 1-5 pass and a short video of a camera-only mapping and navigation run is saved.

## Risks (milestone 4)
- The container has no GPU, so camera rendering and SLAM may run below real time.
- Visual SLAM loses tracking on blank walls and fast turns. The world needs textures, and an IMU may be required.
- Bad camera calibration ruins results.
- I have not checked that RTAB-Map and ORB-SLAM3 build and run on arm64 Linux in this container.
- Isaac ROS cuVSLAM needs an NVIDIA GPU and is not an option here.

## Next (milestone 5 ideas)
- Manipulation (arm, gripper, picking up objects), once mobility and mapping work.
- A camera on the real robot, running visual SLAM on the Pi (or offloaded to a laptop).
