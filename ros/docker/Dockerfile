# ROS 2 Jazzy desktop in the browser (noVNC on port 6080), plus Gazebo, Nav2 and slam_toolbox
FROM docker.io/tiryoh/ros2-desktop-vnc:jazzy

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-jazzy-ros-gz \
        ros-jazzy-navigation2 \
        ros-jazzy-nav2-bringup \
        ros-jazzy-slam-toolbox \
        ros-jazzy-teleop-twist-keyboard \
    && rm -rf /var/lib/apt/lists/*
