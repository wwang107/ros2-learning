import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Listener(Node):
    def __init__(self):
        super().__init__('listener')
        self.create_subscription(String,'chatter', self.on_message,10)

    def on_message(self, message: String):
        self.get_logger().info(f'Received message: {message.data}')


def main(args=None):
    rclpy.init(args=args)
    node = Listener()
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
