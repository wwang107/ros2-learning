from setuptools import find_packages, setup

package_name = 'lidar_wander'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubuntu',
    maintainer_email='ubuntu@todo.todo',
    description='Drives the robot around a room using only /scan',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'wander = lidar_wander.wander:main',
            'reset_button = lidar_wander.reset_button:main',
        ],
    },
)
