import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_launch_description():
    # Sim + bridge + slam_toolbox (publishes /map and map->odom)
    sim_slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(ROOT, 'launch', 'sim_slam.launch.py')))

    # Nav2 servers only: the map and localization come from slam_toolbox, so no map_server or AMCL
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('nav2_bringup'), 'launch', 'navigation_launch.py')),
        launch_arguments={
            'use_sim_time': 'true',
            'autostart': 'true',
            'params_file': os.path.join(ROOT, 'config', 'nav2_params.yaml'),
        }.items())

    return LaunchDescription([sim_slam, nav2])
