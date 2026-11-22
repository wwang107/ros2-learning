import threading
import tkinter as tk

import rclpy
from rclpy.node import Node
from slam_toolbox.srv import Reset


class ResetButton(Node):
    def __init__(self):
        super().__init__('reset_button')
        self.client = self.create_client(Reset, '/slam_toolbox/reset')
        self.future = None

    def reset(self) -> str:
        if not self.client.service_is_ready():
            return 'slam_toolbox is not running'
        self.future = self.client.call_async(Reset.Request())
        return 'clearing...'

    def result_text(self):
        """None while the call is still pending, then a message for the label."""
        if self.future is None or not self.future.done():
            return None
        code = self.future.result().result
        self.future = None
        return 'map cleared' if code == Reset.Response.RESULT_SUCCESS else f'failed (code {code})'


def main(args=None):
    rclpy.init(args=args)
    node = ResetButton()
    # ROS callbacks run in a background thread; Tk owns the main thread
    threading.Thread(target=rclpy.spin, args=(node,), daemon=True).start()

    root = tk.Tk()
    root.title('SLAM')
    label = tk.Label(root, text='ready', width=28)

    def on_click():
        label.config(text=node.reset())

    def poll():
        text = node.result_text()
        if text is not None:
            label.config(text=text)
        root.after(100, poll)

    tk.Button(root, text='Clear map and start over', command=on_click,
              height=2, width=28).pack(padx=10, pady=(10, 4))
    label.pack(pady=(0, 10))
    poll()
    try:
        root.mainloop()
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
