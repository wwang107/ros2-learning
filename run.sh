#!/usr/bin/env bash
# Start the ROS 2 desktop container; open http://localhost:6080 (user/password: ubuntu/ubuntu)
set -euo pipefail
cd "$(dirname "$0")"

podman rm -f ros-gz >/dev/null 2>&1 || true

# ip_unprivileged_port_start=0: noVNC runs as user "ubuntu" and must bind port 80 (Podman, unlike Docker, doesn't allow this by default)
# seccomp=unconfined: recommended by the base image for Ubuntu Noble
podman run -d --name ros-gz \
  -p 6080:80 --shm-size=1g \
  --sysctl net.ipv4.ip_unprivileged_port_start=0 \
  --security-opt seccomp=unconfined \
  -v "$PWD":/opt/sim \
  localhost/ros-gz-vnc:jazzy
