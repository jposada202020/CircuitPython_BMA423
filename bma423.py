# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`bma423`
================================================================================

BMA423 Bosch Accelerometer CircuitPython Driver included in the Lilygo Watch V3


* Author(s): Jose D. Montoya


"""
import time
from micropython import const
from adafruit_bus_device import i2c_device
from adafruit_register.i2c_struct import ROUnaryStruct, UnaryStruct
from adafruit_register.i2c_bits import RWBits

try:
    from busio import I2C
    from typing import Tuple
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/CircuitPython_BMA423.git"

_REG_WHOAMI = const(0x00)
_PWR_CTRL = const(0x7D)
_ACC_RANGE = const(0x41)
_ACC_CONF = const(0x40)


# Acceleration range
ACC_RANGE_2 = const(0x00)
ACC_RANGE_4 = const(0x01)
ACC_RANGE_8 = const(0x02)
ACC_RANGE_16 = const(0x03)
acc_range_values = (ACC_RANGE_2, ACC_RANGE_4, ACC_RANGE_8, ACC_RANGE_16)
acc_range_factor = {0x00: 1024, 0x01: 512, 0x02: 256, 0x03: 128}


class BMA423:
    """Driver for the BMA400 Sensor connected over I2C.

    :param ~busio.I2C i2c_bus: The I2C bus the BMA423 is connected to.
    :param int address: The I2C device address. Defaults to :const:`0x19`

    :raises RuntimeError: if the sensor is not found

    **Quickstart: Importing and using the device**

    Here is an example of using the :class:`BMA423` class.
    First you will need to import the libraries to use the sensor

    .. code-block:: python

        import board
        import bma423

    Once this is done you can define your `board.I2C` object and define your sensor object

    .. code-block:: python

        i2c = board.I2C()  # uses board.SCL and board.SDA
        bma = bma423.BMA423(i2c)

    Now you have access to the attributes

    .. code-block:: python

        accx, accy, accz = bma.acceleration

    """

    _device_id = ROUnaryStruct(_REG_WHOAMI, "B")
    _acc_range = RWBits(2, _ACC_RANGE, 0)
    _acc_on = RWBits(1, _PWR_CTRL, 2)

    # ACC_CONF (0x40)
    # | ---- | ---- | ---- | ---- | odr(3) | odr(2) | odr(1) | odr(0) |
    _output_data_rate = RWBits(4, _ACC_CONF, 0)

    # Acceleration Data
    _accx_value_LSB = UnaryStruct(0x12, "B")
    _accx_value_MSB = UnaryStruct(0x13, "B")
    _accy_value_LSB = UnaryStruct(0x14, "B")
    _accy_value_MSB = UnaryStruct(0x15, "B")
    _accz_value_LSB = UnaryStruct(0x16, "B")
    _accz_value_MSB = UnaryStruct(0x17, "B")
    _temperature = ROUnaryStruct(0x22, "B")

    def __init__(self, i2c_bus: I2C, address: int = 0x19) -> None:
        self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)

        if self._device_id != 0x13:
            raise RuntimeError("Failed to find BMA423")

        self._acc_on = True
        self._acc_range_mem = self._acc_range

    @property
    def acceleration(self) -> Tuple[float, float, float]:
        """
        Acceleration
        :return: acceleration
        """
        alx = self._accx_value_LSB & 0xF0
        ahx = self._accx_value_MSB << 8
        totx = (alx + ahx) >> 4
        totalx = self._twos_comp(totx, 12)

        aly = self._accy_value_LSB & 0xF0
        ahy = self._accy_value_MSB << 8
        toty = (aly + ahy) >> 4
        totaly = self._twos_comp(toty, 12)

        alz = self._accz_value_LSB & 0xF0
        ahz = self._accz_value_MSB << 8
        totz = (alz + ahz) >> 4
        totalz = self._twos_comp(totz, 12)

        factor = acc_range_factor[self._acc_range_mem]
        return totalx / factor, totaly / factor, totalz / factor

    @property
    def acc_range(self) -> str:
        """
        Sensor acc_range

        +---------------------------------+------------------+
        | Mode                            | Value            |
        +=================================+==================+
        | :py:const:`bma400.ACC_RANGE_2`  | :py:const:`0x00` |
        +---------------------------------+------------------+
        | :py:const:`bma400.ACC_RANGE_4`  | :py:const:`0x01` |
        +---------------------------------+------------------+
        | :py:const:`bma400.ACC_RANGE_8`  | :py:const:`0x02` |
        +---------------------------------+------------------+
        | :py:const:`bma400.ACC_RANGE_16` | :py:const:`0x03` |
        +---------------------------------+------------------+
        """
        values = (
            "ACC_RANGE_2",
            "ACC_RANGE_4",
            "ACC_RANGE_8",
            "ACC_RANGE_16",
        )
        return values[self._acc_range_mem]

    @acc_range.setter
    def acc_range(self, value: int) -> None:
        if value not in acc_range_values:
            raise ValueError("Value must be a valid acc_range setting")
        self._acc_range = value
        self._acc_range_mem = value

    @property
    def temperature(self) -> float:
        """
        The temperature sensor is calibrated with a precision of +/-5°C.
        :return: Temperature
        """
        raw_temp = self._temperature
        time.sleep(0.16)
        temp = self._twos_comp(raw_temp, 8)
        return temp + 23

    @staticmethod
    def _twos_comp(val: int, bits: int) -> int:

        if val & (1 << (bits - 1)) != 0:
            return val - (1 << bits)
        return val
