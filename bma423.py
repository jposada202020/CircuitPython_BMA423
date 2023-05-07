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
from adafruit_register.i2c_bit import RWBit

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

# Output Data Rate
BANDWIDTH_25_32 = const(0b0001)
BANDWIDTH_25_16 = const(0b0010)
BANDWIDTH_25_8 = const(0b0011)
BANDWIDTH_25_4 = const(0b0100)
BANDWIDTH_25_2 = const(0b0101)
BANDWIDTH_25 = const(0b0110)
BANDWIDTH_50 = const(0b0111)
BANDWIDTH_100 = const(0b1000)
BANDWIDTH_200 = const(0b1001)
BANDWIDTH_400 = const(0b1010)
BANDWIDTH_800 = const(0b1011)
BANDWIDTH_1600 = const(0b1100)
output_data_rate_values = (
    BANDWIDTH_25_32,
    BANDWIDTH_25_16,
    BANDWIDTH_25_8,
    BANDWIDTH_25_4,
    BANDWIDTH_25_2,
    BANDWIDTH_25,
    BANDWIDTH_50,
    BANDWIDTH_100,
    BANDWIDTH_200,
    BANDWIDTH_400,
    BANDWIDTH_800,
    BANDWIDTH_1600,
)

# Oversample Rate
OSR1 = const(0x00)
OSR2 = const(0x01)
OSR4 = const(0x02)
OSR8 = const(0x03)
OSR16 = const(0x04)
OSR32 = const(0x05)
OSR64 = const(0x06)
OSR128 = const(0x07)
oversample_rate_values = (OSR1, OSR2, OSR4, OSR8, OSR16, OSR32, OSR64, OSR128)

CIC_AVG = const(0x00)
CONT = const(0x01)
filter_performance_values = (CIC_AVG, CONT)

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

    _acc_on = RWBit(_PWR_CTRL, 2)

    # ACC_CONF (0x40)
    # | acc_perf_mode | acc_bwp(2) | acc_bwp(1) | acc_bwp(0) | odr(3) | odr(2) | odr(1) | odr(0) |
    _output_data_rate = RWBits(4, _ACC_CONF, 0)
    _oversample_rate = RWBits(3, _ACC_CONF, 4)
    _filter_performance = RWBit (_ACC_CONF, 7)

    # ACC_RANGE (0x41)
    # | ---- | ---- | ---- | ---- | ---- | ---- | acc_range(1) | acc_range(0) |
    _acc_range = RWBits(2, _ACC_RANGE, 0)

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
        totx = (alx | ahx) >> 4
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
        | :py:const:`bma423.ACC_RANGE_2`  | :py:const:`0x00` |
        +---------------------------------+------------------+
        | :py:const:`bma423.ACC_RANGE_4`  | :py:const:`0x01` |
        +---------------------------------+------------------+
        | :py:const:`bma423.ACC_RANGE_8`  | :py:const:`0x02` |
        +---------------------------------+------------------+
        | :py:const:`bma423.ACC_RANGE_16` | :py:const:`0x03` |
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

    @property
    def output_data_rate(self) -> str:
        """
        Sensor output_data_rate

        +------------------------------------+--------------------+
        | Mode                               | Value              |
        +====================================+====================+
        | :py:const:`bma423.BANDWIDTH_25_32` | :py:const:`0b0001` |
        +------------------------------------+--------------------+
        | :py:const:`bma423.BANDWIDTH_25_16` | :py:const:`0b0010` |
        +------------------------------------+--------------------+
        | :py:const:`bma423.BANDWIDTH_25_8`  | :py:const:`0b0011` |
        +------------------------------------+--------------------+
        | :py:const:`bma423.BANDWIDTH_25_4`  | :py:const:`0b0100` |
        +------------------------------------+--------------------+
        | :py:const:`bma423.BANDWIDTH_25_2`  | :py:const:`0b0101` |
        +------------------------------------+--------------------+
        | :py:const:`bma423.BANDWIDTH_25`    | :py:const:`0b0110` |
        +------------------------------------+--------------------+
        | :py:const:`bma423.BANDWIDTH_50`    | :py:const:`0b0111` |
        +------------------------------------+--------------------+
        | :py:const:`bma423.BANDWIDTH_100`   | :py:const:`0b1000` |
        +------------------------------------+--------------------+
        | :py:const:`bma423.BANDWIDTH_200`   | :py:const:`0b1001` |
        +------------------------------------+--------------------+
        | :py:const:`bma423.BANDWIDTH_400`   | :py:const:`0b1010` |
        +------------------------------------+--------------------+
        | :py:const:`bma423.BANDWIDTH_800`   | :py:const:`0b1011` |
        +------------------------------------+--------------------+
        | :py:const:`bma423.BANDWIDTH_1600`  | :py:const:`0b1100` |
        +------------------------------------+--------------------+
        """
        values = (
            "BANDWIDTH_25_32",
            "BANDWIDTH_25_16",
            "BANDWIDTH_25_8",
            "BANDWIDTH_25_4",
            "BANDWIDTH_25_2",
            "BANDWIDTH_25",
            "BANDWIDTH_50",
            "BANDWIDTH_100",
            "BANDWIDTH_200",
            "BANDWIDTH_400",
            "BANDWIDTH_800",
            "BANDWIDTH_1600",
        )
        return values[self._output_data_rate]

    @output_data_rate.setter
    def output_data_rate(self, value: int) -> None:
        if value not in output_data_rate_values:
            raise ValueError("Value must be a valid output_data_rate setting")
        self._output_data_rate = value

    @property
    def oversample_rate(self) -> str:
        """
        Sensor oversample_rate. Bandwidth parameter, determines filter configuration
        (acc_perf_mode=1) and averaging for undersampling mode (acc_perf_mode=0)

        +---------------------------+------------------+
        | Mode                      | Value            |
        +===========================+==================+
        | :py:const:`bma423.OSR1`   | :py:const:`0x00` |
        +---------------------------+------------------+
        | :py:const:`bma423.OSR2`   | :py:const:`0x01` |
        +---------------------------+------------------+
        | :py:const:`bma423.OSR4`   | :py:const:`0x02` |
        +---------------------------+------------------+
        | :py:const:`bma423.OSR8`   | :py:const:`0x03` |
        +---------------------------+------------------+
        | :py:const:`bma423.OSR16`  | :py:const:`0x04` |
        +---------------------------+------------------+
        | :py:const:`bma423.OSR32`  | :py:const:`0x05` |
        +---------------------------+------------------+
        | :py:const:`bma423.OSR64`  | :py:const:`0x06` |
        +---------------------------+------------------+
        | :py:const:`bma423.OSR128` | :py:const:`0x07` |
        +---------------------------+------------------+
        """
        values = ("OSR1", "OSR2", "OSR4", "OSR8", "OSR16", "OSR32", "OSR64", "OSR128",)
        return values[self._oversample_rate]

    @oversample_rate.setter
    def oversample_rate(self, value: int) -> None:
        if value not in oversample_rate_values:
            raise ValueError("Value must be a valid oversample_rate setting")
        self._filter_performance = True
        self._oversample_rate = value

    @property
    def filter_performance(self) -> str:
        """
        Sensor filter_performance

        +----------------------------+------------------+
        | Mode                       | Value            |
        +============================+==================+
        | :py:const:`bma423.CIC_AVG` | :py:const:`0x00` |
        +----------------------------+------------------+
        | :py:const:`bma423.CONT`    | :py:const:`0x01` |
        +----------------------------+------------------+
        """
        values = ("CIC_AVG", "CONT",)
        return values[self._filter_performance]

    @filter_performance.setter
    def filter_performance(self, value: int) -> None:
        if value not in filter_performance_values:
            raise ValueError("Value must be a valid filter_performance setting")
        self._filter_performance = value

    @staticmethod
    def _twos_comp(val: int, bits: int) -> int:

        if val & (1 << (bits - 1)) != 0:
            return val - (1 << bits)
        return val
