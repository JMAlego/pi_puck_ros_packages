#!/usr/bin/env python
"""ROS Node to expose a topics for the short range IR sensors on the Pi-puck."""

import math

# ROS imports
import rospy
from sensor_msgs.msg import Range

# Standard imports
from smbus import SMBus

# Constants
I2C_CHANNEL = 4
EPUCK_I2C_ADDR = 0x1e

IR_CONTROL = 6
IR0_REFLECTED = 7
IR1_REFLECTED = 8
IR2_REFLECTED = 9
IR3_REFLECTED = 10
IR4_REFLECTED = 11
IR5_REFLECTED = 12
IR6_REFLECTED = 13
IR7_REFLECTED = 14

IRX_REFLECTED = (IR0_REFLECTED, IR1_REFLECTED, IR2_REFLECTED, IR3_REFLECTED, IR4_REFLECTED, IR5_REFLECTED,
                 IR6_REFLECTED, IR7_REFLECTED)

IR0_AMBIENT = 15
IR1_AMBIENT = 16
IR2_AMBIENT = 17
IR3_AMBIENT = 18
IR4_AMBIENT = 19
IR5_AMBIENT = 20
IR6_AMBIENT = 21
IR7_AMBIENT = 22

IRX_AMBIENT = (IR0_AMBIENT, IR1_AMBIENT, IR2_AMBIENT, IR3_AMBIENT, IR4_AMBIENT, IR5_AMBIENT, IR6_AMBIENT, IR7_AMBIENT)

IR_SENSOR_COUNT = 8

BUS = SMBus(I2C_CHANNEL)


def calculate_distance(x):
    """Calculates an estimate of the range in metres."""
    return round(-(1000000.0 * math.log((50 y)/199313.0)) / 101211.0, 2) / 1000.0


def close_bus():
    """Close the I2C bus after the ROS Node is shutdown."""
    BUS.write_word_data(EPUCK_I2C_ADDR, IR_CONTROL, 0)  # Stop IR
    BUS.close()


def pi_puck_short_range_ir_server():
    """ROS Node server."""
    rospy.on_shutdown(close_bus)
    BUS.write_word_data(EPUCK_I2C_ADDR, IR_CONTROL, 1)  # Turn IR sensors on

    ir_proximity_publishers = {}

    for ir_sensor in range(IR_SENSOR_COUNT):
        ir_proximity_publishers[ir_sensor] = rospy.Publisher('proximity/short_range_ir/{}'.format(ir_sensor),
                                                             Range,
                                                             queue_size=10)

    rospy.init_node("proximity")

    rate = rospy.Rate(rospy.get_param('rate', 5))

    while not rospy.is_shutdown():
        for ir_sensor in range(IR_SENSOR_COUNT):
            distance_reading_raw = int(BUS.read_word_data(EPUCK_I2C_ADDR, IRX_REFLECTED[ir_sensor]))
            converted_distance_reading = calculate_distance(distance_reading_raw)
            range_result = Range(radiation_type=Range.INFRARED,
                                 min_range=0,
                                 max_range=0.1,
                                 range=converted_distance_reading)
            ir_proximity_publishers[ir_sensor].publish(range_result)
        rate.sleep()


if __name__ == "__main__":
    pi_puck_short_range_ir_server()