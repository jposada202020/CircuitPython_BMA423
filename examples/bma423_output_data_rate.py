# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
import board
import bma423

i2c = board.I2C()
bma = bma423.BMA423(i2c)

bma.output_data_rate = bma423.BANDWIDTH_25_2

while True:
    for output_data_rate in bma423.output_data_rate_values:
        print("Current Output data rate setting: ", bma.output_data_rate)
        for _ in range(10):
            accx, accy, accz = bma.acceleration
            print("x:{:.2f}m/s2, y:{:.2f}m/s2, z:{:.2f}m/s2".format(accx, accy, accz))
            time.sleep(0.5)
        bma.output_data_rate = output_data_rate
