import os
from launch import LaunchDescription
from launch.actions import EmitEvent, RegisterEventHandler, ExecuteProcess
from launch.events import matches_action
from launch_ros.actions import Node, LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_launch_description():
    sim = ExecuteProcess(
        cmd=['gz', 'sim', '-s', '-r', os.path.join(ROOT, 'worlds', 'room.sdf')],
        output='screen')

    # Gazebo 3D window; needs a display (the container's VNC desktop)
    gui = ExecuteProcess(cmd=['gz', 'sim', '-g'], output='screen')

    bridge = Node(
        package='ros_gz_bridge', executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/model/diff_bot/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],
        remappings=[('/model/diff_bot/tf', '/tf')],
        parameters=[{'use_sim_time': True}])

    # base -> lidar_link, matching the sensor pose in worlds/room.sdf
    lidar_tf = Node(
        package='tf2_ros', executable='static_transform_publisher',
        arguments=['--x', '0.1', '--z', '0.2',
                   '--frame-id', 'base', '--child-frame-id', 'lidar_link'],
        parameters=[{'use_sim_time': True}])

    # slam_toolbox is a lifecycle node: it must be configured, then activated
    slam = LifecycleNode(
        package='slam_toolbox', executable='async_slam_toolbox_node',
        name='slam_toolbox', namespace='',
        parameters=[{
            'use_sim_time': True,
            'odom_frame': 'odom',
            'base_frame': 'base',
            'map_frame': 'map',
            'scan_topic': '/scan',
            'mode': 'mapping',
            'resolution': 0.05,
            'max_laser_range': 10.0,
            'minimum_travel_distance': 0.2,
            'minimum_travel_heading': 0.2,
        }])

    configure = EmitEvent(event=ChangeState(
        lifecycle_node_matcher=matches_action(slam),
        transition_id=Transition.TRANSITION_CONFIGURE))
    activate = RegisterEventHandler(OnStateTransition(
        target_lifecycle_node=slam, goal_state='inactive',
        entities=[EmitEvent(event=ChangeState(
            lifecycle_node_matcher=matches_action(slam),
            transition_id=Transition.TRANSITION_ACTIVATE))]))

    return LaunchDescription([sim, gui, bridge, lidar_tf, slam, activate, configure])
