# ROS 2 Jazzy sim playground

A differential-drive robot with a 360° lidar in a small Gazebo room, set up for SLAM (slam_toolbox) and navigation (Nav2). Everything runs in a Podman container with a Linux desktop served in the browser via noVNC.

## Layout

| Path | Contents |
|---|---|
| `docker/Dockerfile` | `tiryoh/ros2-desktop-vnc:jazzy` + Gazebo (`ros-gz`), Nav2, slam_toolbox, teleop |
| `worlds/room.sdf` | Walled room with a box and `diff_bot` (diff drive, `gpu_lidar` on `/scan`) |
| `launch/sim_slam.launch.py` | Gazebo server + GUI, ROS–Gazebo bridge, `base`→`lidar_link` static TF, slam_toolbox (mapping) |
| `launch/sim_nav.launch.py` | `sim_slam` + Nav2 servers (map comes from slam_toolbox, so no map_server/AMCL) |
| `config/nav2_params.yaml` | Nav2 parameters (robot frame is `base`) |
| `run.sh` | (Re)creates and starts the `ros-gz` container |

## Setup

Build the image once:

```bash
podman build -t ros-gz-vnc:jazzy docker/
```

Start the container:

```bash
./run.sh
```

Open http://localhost:6080 (user/password: `ubuntu`/`ubuntu`). The project folder is mounted at `/opt/sim`, so edits on the Mac show up in the container immediately.

To get a shell without the browser:

```bash
podman exec -it -u ubuntu ros-gz bash
```

## Running the sim

In a terminal on the noVNC desktop:

```bash
cd /opt/sim
ros2 launch launch/sim_slam.launch.py      # sim + mapping
```

Drive the robot to build the map (second terminal):

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Or run the full stack with autonomous navigation:

```bash
ros2 launch launch/sim_nav.launch.py
```

To see the map, start `rviz2`, set **Fixed Frame** to `map`, and add `/map` and `/scan` displays. With Nav2 running, use **2D Goal Pose** to send the robot somewhere.

Stop launches with **Ctrl+C** and wait for them to finish. Closing the terminal or browser tab can leave Gazebo and bridge processes running in the background.

## Writing your own packages

Create a colcon workspace in the project so the code lives on the Mac:

```bash
cd /opt/sim
mkdir -p src && cd src
ros2 pkg create --build-type ament_python my_first_pkg --dependencies rclpy std_msgs
cd /opt/sim
colcon build --symlink-install
source install/setup.bash
ros2 run my_first_pkg <executable>
```

## IDE (IntelliJ / PyCharm)

`rclpy` can't be installed on macOS, so the IDE gets completion and linting from a copy of the container's ROS Python sources:

- The sources are copied to `~/.local/share/ros-jazzy-python`:
  ```bash
  mkdir -p ~/.local/share/ros-jazzy-python
  podman cp ros-gz:/opt/ros/jazzy/lib/python3.12/site-packages/. ~/.local/share/ros-jazzy-python/
  ```
- `../venv/lib/python3.12/site-packages/ros_jazzy.pth` adds that folder to the venv's `sys.path` (after the venv's own packages, so they take priority).
- The IDE project interpreter is `../venv` (Python 3.12, same as the container).

This is for editing only. The copied modules include Linux-only compiled code, so `import rclpy` fails if you run it on the Mac. Build and run in the container terminal. Re-run the `podman cp` after installing new ROS packages in the image. To undo, delete the `.pth` file.

Using the container itself as the interpreter (**Add Interpreter → On Docker**) needs the paid **Python** plugin (`Pythonid`), not *Python Community Edition*. If you switch to that: connect via **Settings → Build, Execution, Deployment → Docker → +** → *Podman* with executable `/opt/podman/bin/podman`, then add `/opt/ros/jazzy/lib/python3.12/site-packages` under **Show Interpreter Paths**.

## Troubleshooting

**localhost:6080 doesn't load.** noVNC runs as `ubuntu` and binds port 80. Unlike Docker, Podman doesn't let non-root users bind ports below 1024, so the container needs `--sysctl net.ipv4.ip_unprivileged_port_start=0`. `run.sh` sets this. Check with:

```bash
podman logs ros-gz | grep novnc
```

**`[RTPS_TRANSPORT_SHM Error] Failed init_port ... open_and_lock_file failed`.** These are stale Fast DDS shared-memory files in `/dev/shm`, left by processes that were killed. The error is harmless (Fast DDS falls back to another port or UDP). Restart the container to clear them, or set `export FASTDDS_BUILTIN_TRANSPORTS=UDPv4` to skip shared memory entirely.

**Robot pose or clock jumps; SLAM or Nav2 behave strangely.** Check for leftover sims from earlier launches:

```bash
podman exec ros-gz pgrep -af "gz sim|parameter_bridge"
```

More than one `gz sim` means several sims are publishing at once. Kill them or restart the container.

**`Permission denied` when creating or building packages.** Inside the container, files and folders created on the Mac belong to uid 501, while the container user `ubuntu` is uid 1000. Files the container created and the Mac then edited end up `rw-------`, which `ubuntu` can't read. Fix permissions from the Mac:

```bash
chmod -R a+rX src                        # let the container read everything in src/
podman exec ros-gz chown 1000:1000 /opt/sim/src   # let the container create packages in a src/ made on the Mac
```
