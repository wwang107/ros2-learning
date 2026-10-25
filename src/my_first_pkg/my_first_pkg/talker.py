import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Talker(Node):
    """Publishes 'Hello ROS 2: <n>' on the /chatter topic twice a second."""

    def __init__(self):
        # The node name, as shown by `ros2 node list`
        super().__init__('talker')
        # Topic name and queue depth (how many messages to buffer if subscribers are slow)
        self.publisher = self.create_publisher(String, 'chatter', 10)
        # Call self.tick every 0.5 s
        self.timer = self.create_timer(0.5, self.tick)
        self.count = 0

    def tick(self):
        msg = String()
        msg.data = f'Hello ROS 2'
        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.count += 1


def main(args=None):
    rclpy.init(args=args)
    node = Talker()
    try:
        # Hand control to ROS: run timers and callbacks until Ctrl+C
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
