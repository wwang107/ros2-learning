import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class Wander(Node):
    def __init__(self):
        super().__init__('wander')
        self.declare_parameter('forward_speed', 0.2)    # m/s
        self.declare_parameter('turn_speed', 0.8)       # rad/s
        self.declare_parameter('stop_distance', 0.5)    # m, turn in place below this
        self.declare_parameter('slow_distance', 1.0)    # m, slow down and steer below this
        self.create_subscription(LaserScan, 'scan', self.on_scan, 10)
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.turn_dir = 1.0   # keep turning the same way until the front is clear

    def sector_min(self, scan: LaserScan, lo_deg: float, hi_deg: float) -> float:
        """Closest valid range between two angles (0 deg = straight ahead, left positive)."""
        best = scan.range_max
        for i, r in enumerate(scan.ranges):
            angle = math.degrees(scan.angle_min + i * scan.angle_increment)
            if lo_deg <= angle <= hi_deg and scan.range_min <= r < best:
                best = r
        return best

    def on_scan(self, scan: LaserScan):
        front = self.sector_min(scan, -30.0, 30.0)
        left = self.sector_min(scan, 30.0, 90.0)
        right = self.sector_min(scan, -90.0, -30.0)

        stop = self.get_parameter('stop_distance').value
        slow = self.get_parameter('slow_distance').value
        speed = self.get_parameter('forward_speed').value
        turn = self.get_parameter('turn_speed').value

        cmd = Twist()
        if front < stop:
            if self.turn_dir == 0.0 or abs(left - right) > 0.1:
                self.turn_dir = 1.0 if left > right else -1.0
            cmd.angular.z = self.turn_dir * turn
        else:
            self.turn_dir = 0.0
            cmd.linear.x = speed * min(1.0, (front - stop) / (slow - stop) + 0.3)
            # steer away from the nearer side wall
            cmd.angular.z = max(-turn, min(turn, 0.5 * (left - right) / slow))
        self.cmd_pub.publish(cmd)

    def stop(self):
        self.cmd_pub.publish(Twist())


def main(args=None):
    rclpy.init(args=args)
    node = Wander()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
