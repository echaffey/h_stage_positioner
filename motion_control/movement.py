# Built in python libraries
import time
import numpy as np
from dataclasses import dataclass

# libraries from this project
from settings import Settings
from device_io.v_out import volt_out


# Read the board and channel numbers for the motors as defined in the settings.py file
motor_board_num = Settings.DAC_BOARD_NUM
motor_1 = Settings.MOTOR_1_CHANNEL
motor_2 = Settings.MOTOR_2_CHANNEL

# A way to store how fast the motor is currently moving based on the voltage
@dataclass
class Speed:
    speed_1 = 0.0
    speed_2 = 0.0
    cur_pos_1 = None
    cur_pos_2 = None


"""This file defines all of the movement functions for the system. 
To create new shapes or movement patterns, define them as a function in here."""


def get_position(d_phi_1: float, d_phi_2: float):

    radius = Settings.PULLEY_RADIUS
    phi = np.array([d_phi_1, d_phi_2])

    A = np.array([[-0.5, 0.5], [-0.5, -0.5]]) * radius

    dx, dy = A.dot(phi)

    return dx, dy


def get_pos(encoder_val_1, encoder_val_2):

    radius = Settings.PULLEY_RADIUS

    revolutions_1 = encoder_val_1 / Settings.ENCODER_VALS_PER_REV
    revolutions_2 = encoder_val_2 / Settings.ENCODER_VALS_PER_REV

    phi_1 = revolutions_1 * 2 * np.pi
    phi_2 = revolutions_2 * 2 * np.pi

    phi = np.array([phi_1, phi_2])

    A = np.array([[-0.5, 0.5], [-0.5, -0.5]]) * radius

    dx, dy = A.dot(phi)

    return dx, dy


def stop_motors():
    """
    Stops all voltage output to the motors.
    """
    Speed.speed_1 = 0
    Speed.speed_2 = 0
    volt_out(motor_board_num, motor_1, 0)
    volt_out(motor_board_num, motor_2, 0)


def pos_X(voltage: float) -> None:
    """Moves the end effector in the defined positive x direction."""
    stop_motors()
    Speed.speed_1 = -voltage
    Speed.speed_2 = voltage
    volt_out(motor_board_num, motor_1, -voltage)
    volt_out(motor_board_num, motor_2, voltage)


def neg_X(voltage: float) -> None:
    """Moves the end effector in the defined negative x direction."""
    stop_motors()
    Speed.speed_1 = voltage
    Speed.speed_2 = -voltage

    volt_out(motor_board_num, motor_1, voltage)
    volt_out(motor_board_num, motor_2, -voltage)


def pos_Y(voltage: float) -> None:
    """Moves the end effector in the defined positive y direction."""
    stop_motors()
    Speed.speed_1 = voltage
    Speed.speed_2 = voltage
    volt_out(motor_board_num, motor_1, voltage)
    volt_out(motor_board_num, motor_2, voltage)


def neg_Y(voltage: float) -> None:
    """Moves the end effector in the defined negative x direction."""
    stop_motors()
    Speed.speed_1 = -voltage
    Speed.speed_2 = -voltage
    volt_out(motor_board_num, motor_1, -voltage)
    volt_out(motor_board_num, motor_2, -voltage)


def ne(voltage: float) -> None:
    """
    Moves the end effector in the northeast direction (+X, -Y)
    This is counter-clockwise rotation of Motor 2

    Args:
        voltage (float): Voltage to apply, in engineering units.
    """
    stop_motors()
    Speed.speed_1 = voltage
    Speed.speed_2 = 0

    volt_out(motor_board_num, motor_2, Speed.speed_1)


def se(voltage: float) -> None:
    """
    Moves the end effector in the southeast direction (-X, -Y)
    This is counter-clockwise rotation of Motor 1

    Args:
        voltage (float): Voltage to apply, in engineering units.
    """
    stop_motors()
    Speed.speed_1 = voltage
    Speed.speed_2 = 0

    volt_out(motor_board_num, motor_1, Speed.speed_1)


def nw(voltage: float) -> None:
    """
    Moves the end effector in the northwest direction (+X, +Y)
    This is clockwise rotation of Motor 1

    Args:
        voltage (float): Voltage to apply, in engineering units.
    """
    stop_motors()
    Speed.speed_1 = voltage
    Speed.speed_2 = 0

    volt_out(motor_board_num, motor_1, -Speed.speed_1)


def sw(voltage: float) -> None:
    """
    Moves the end effector in the southwest direction (-X, -Y)
    This is clockwise rotation of Motor 2

    Args:
        voltage (float): Voltage to apply, in engineering units.
    """
    stop_motors()
    Speed.speed_1 = voltage
    Speed.speed_2 = 0

    volt_out(motor_board_num, motor_2, -Speed.speed_1)


def slow_pos_y(sensor_input: float, volts: float):
    v_out = abs(sensor_input / 10) * volts

    volt_out(motor_board_num, motor_1, v_out)
    volt_out(motor_board_num, motor_2, v_out)


def adjust_speed(sensor_input: float) -> None:
    v_out = abs(sensor_input / 10) * Speed.speed_1

    volt_out(motor_board_num, motor_1, v_out)
    volt_out(motor_board_num, motor_2, v_out)


def draw_square(voltage: float) -> None:
    """
    Moves the end effector in a square pattern.

    Args:
        voltage (float): Voltage to be applied to the motors, in engineering units.
    """

    time_sleep = 1.5 / voltage
    stop_motors()
    neg_X(voltage)
    time.sleep(time_sleep)
    neg_Y(voltage)
    time.sleep(time_sleep)
    pos_X(voltage)
    time.sleep(time_sleep)
    pos_Y(voltage)
    time.sleep(time_sleep)
    stop_motors()


def draw_diamond(voltage: float) -> None:
    """
    Moves the end effector in a diamond pattern.

    Args:
        voltage (float): Voltage to be applied to the motors, in engineering units.
    """
    time_sleep = np.sqrt(2 * 1.5**2) / voltage
    print(np.sqrt(2 * 1.5**2))
    stop_motors()

    sw(voltage)
    time.sleep(time_sleep)

    nw(voltage)
    time.sleep(time_sleep)

    ne(voltage)
    time.sleep(time_sleep)

    se(voltage)
    time.sleep(time_sleep)
    stop_motors()
