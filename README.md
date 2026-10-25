# Wheeled robot in simulation (ROS 2 + Gazebo)

A differential-drive robot with a 2D lidar drives around a simulated room. `slam_toolbox` builds a map
and `nav2` is set up to drive to goals. Everything runs inside one Podman container with a Linux desktop
you open in the browser. See `MILESTONE.md` for the goals and steps.

## Status
- Works: the simulated robot, driving it with `/cmd_vel`, lidar on `/scan`, odometry on `/odom`, mapping with `slam_toolbox`.
- Starts but does not work yet: Nav2 goals. The planner aborts with `NO_VALID_PATH` (error 208),
  because the global costmap marks the robot's own surroundings as obstacles.
  - Cause found so far: the lidar's beam hit the floor when the robot tilted. I raised the lidar and added a front caster,
    which reduced the tilt (bad lidar rays went from 88 to 11) but I did not confirm that goals now succeed.
- Not tried: teleop by hand and RViz inside the container. Only scripted driving was tested.

## Folder layout
| Path | What it is |
|---|---|
| `ros/docker/Dockerfile` | Builds the container image `ros-gz-vnc:jazzy` (ROS 2 Jazzy, Gazebo, Nav2, slam_toolbox, desktop). |
| `ros/worlds/room.sdf` | The simulated world: 8x8 m room, one box, and the robot with its lidar. |
| `ros/launch/sim_slam.launch.py` | Starts Gazebo, the ROS bridge, the lidar transform and `slam_toolbox`. |
| `ros/launch/sim_nav.launch.py` | Starts everything above plus Nav2. This is the main launch file. |
| `ros/config/nav2_params.yaml` | Nav2 settings (frames, robot radius, controller). |
| `MILESTONE.md` | Project goals and steps. |

`ros/worlds`, `ros/launch` and `ros/config` are mounted into the container at `/opt/sim/`, so you can edit them on your Mac.
Anything else you create inside the container is lost if the container is deleted.

## One-time setup
1. Podman needs about 8 GB of RAM for its VM: `podman machine set --memory 8192` (stop the machine first with `podman machine stop`, then start it).
2. Build the image (takes several minutes): `cd ros/docker && podman build -t ros-gz-vnc:jazzy .`
3. Create the container, from the `ros/` folder:

```
podman run -d --name ros-gz -p 6080:80 --shm-size=1g \
  --sysctl net.ipv4.ip_unprivileged_port_start=0 \
  -v "$PWD/worlds":/opt/sim/worlds:Z \
  -v "$PWD/launch":/opt/sim/launch:Z \
  -v "$PWD/config":/opt/sim/config:Z \
  localhost/ros-gz-vnc:jazzy
```

## Every time you work
1. Start Podman and the container: `podman machine start` (if stopped), then `podman start ros-gz`.
2. Open **http://localhost:6080** in your browser. The VNC password is `ubuntu`. You now see a Linux desktop.
3. On that desktop, open a terminal (the Terminator icon) and run the simulation:
   ```
   ros2 launch /opt/sim/launch/sim_nav.launch.py
   ```
   Wait about 30-60 seconds. A Gazebo window opens with the room and the robot.
   Use `sim_slam.launch.py` instead if you want mapping without Nav2.
4. Open a second terminal and drive the robot by hand:
   ```
   ros2 run teleop_twist_keyboard teleop_twist_keyboard
   ```
   Keep that terminal focused and press `i` (forward), `j`/`l` (turn), `k` (stop).
5. Open a third terminal and start RViz: `rviz2`
   - Set **Fixed Frame** to `map`.
   - Click **Add**, open the **By topic** tab, and add **Map** under `/map` and **LaserScan** under `/scan`.
   - Add **TF** to see the robot's frames move.
6. Stop with `Ctrl+C` in the launch terminal, and `podman stop ros-gz` when you are done.

If you change `room.sdf` or a launch file, stop the launch with `Ctrl+C` and start it again.
If processes are stuck, run `podman restart ros-gz`.

## Working from your Mac terminal
Copy and paste (`Cmd+C`, `Cmd+V`) does not cross into the browser desktop. A Mac terminal avoids that: all your usual
shortcuts work, and you only use the browser tab to look at Gazebo and RViz.

**Open a shell inside the container** (do this in each new Mac terminal tab):
```
podman exec -it -u ubuntu ros-gz bash
source /opt/ros/jazzy/setup.bash
```
Then use `ros2` commands, teleop and your Python scripts as in the sections below.

**Programs with windows** (RViz, Gazebo) draw on the container's desktop at `:1`, so you can start them from the Mac
terminal. Add `-e DISPLAY=:1` when you open the shell, and the window appears in the browser tab:
```
podman exec -it -u ubuntu -e DISPLAY=:1 ros-gz bash
source /opt/ros/jazzy/setup.bash
rviz2
```

**Typical session with three Mac terminal tabs**
| Tab | Shell opened with | Command |
|---|---|---|
| 1 | `-e DISPLAY=:1` | `ros2 launch /opt/sim/launch/sim_nav.launch.py` |
| 2 | no display needed | `ros2 run teleop_twist_keyboard teleop_twist_keyboard` |
| 3 | `-e DISPLAY=:1` | `rviz2` |

Keep the browser tab at http://localhost:6080 open to see the windows.

**Good to know**
- A program started in a Mac terminal stops when you close that tab or press `Ctrl+C`.
- Teleop reads keys from the terminal it runs in, so keep that tab focused. It works the same as in the desktop terminal.
- To save typing, add an alias to `~/.zshrc`:
  ```
  alias rosg='podman exec -it -u ubuntu -e DISPLAY=:1 ros-gz bash -c "source /opt/ros/jazzy/setup.bash; exec bash"'
  ```
  Then `rosg` opens a ready shell.
- I tested starting the launch file and scripts this way with `podman exec`, but I have not tried teleop or RViz from a Mac terminal.

## ROS 2 in five ideas
- **Node:** a program that does one job (for example, the lidar bridge or `slam_toolbox`). A robot is many nodes running together.
- **Topic:** a named channel nodes use to send messages. One node publishes, others subscribe.
  Here: `/cmd_vel` (drive commands), `/odom` (wheel odometry), `/scan` (lidar), `/map` (the map).
- **Message type:** the shape of the data on a topic, for example `geometry_msgs/Twist` for velocity or `sensor_msgs/LaserScan` for lidar.
- **Frame and TF:** every part of the robot and the world has a coordinate frame, and TF is the tree of transforms between them.
  Here: `map` -> `odom` -> `base` -> `lidar_link`. `slam_toolbox` provides `map` -> `odom`, the simulator provides `odom` -> `base`.
- **Action:** a long-running request with feedback and a result, like "drive to this pose" (`/navigate_to_pose` in Nav2).
- **Launch file:** a Python file that starts many nodes together with their settings.

## How the pieces connect
```
 Gazebo (physics, lidar)  <--ros_gz_bridge-->  ROS 2 topics: /scan /odom /tf /clock /cmd_vel
                                                      |
                                    slam_toolbox  (reads /scan + /odom, publishes /map and map->odom)
                                                      |
                                    nav2 (reads /map + /scan, plans a path, publishes /cmd_vel)
```
Gazebo has its own message system, and `ros_gz_bridge` copies messages between it and ROS 2.
The simulated time comes from `/clock`, which is why nodes are started with `use_sim_time: true`.

## Useful commands (run in a container terminal)
| Command | What it does |
|---|---|
| `ros2 topic list` | List all topics. |
| `ros2 topic echo /odom` | Print messages on a topic. Add `--once` for one message. |
| `ros2 topic hz /scan` | Show how often a topic publishes. |
| `ros2 topic info /cmd_vel` | Show the type and who publishes or subscribes. |
| `ros2 node list` | List running nodes. |
| `ros2 run tf2_ros tf2_echo map base` | Print the robot's pose in the map. |
| `ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}}"` | Send one drive command. |
| `ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map}, pose: {position: {x: -2.0, y: -2.0}, orientation: {w: 1.0}}}}"` | Send a Nav2 goal. |
| `ros2 run tf2_tools view_frames` | Save a diagram of the TF tree to a PDF. |

## Troubleshooting
- **Port 6080 does not load:** the container needs the `--sysctl net.ipv4.ip_unprivileged_port_start=0` flag. Recreate it with the command above.
- **RViz says "empty topic name":** the display's Topic field is blank. Set it, or add the display from the **By topic** tab.
- **No map in RViz:** check that the launch is running. For the Map display, set Durability Policy to `Transient Local`.
- **Nav2 goal aborts (code 208):** see Status above. Inspect `/global_costmap/costmap` in RViz (add a Map display on that topic).
- **Slow or laggy:** the container has no GPU and renders in software. Close extra RViz displays.
- **Gazebo window is black:** the models need materials and the scene needs ambient light. `room.sdf` already sets both.

## Learning resources
- ROS 2 Jazzy tutorials: https://docs.ros.org/en/jazzy/Tutorials.html (start with "Beginner: CLI tools" and "Client libraries")
- Nav2 documentation: https://docs.nav2.org
- `slam_toolbox`: https://github.com/SteveMacenski/slam_toolbox
- Gazebo Sim documentation: https://gazebosim.org/docs/harmonic
