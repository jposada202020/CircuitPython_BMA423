# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
import board
import bma423

i2c = board.I2C()
bma = bma423.BMA423(i2c)

bma.oversample_rate = bma423.OSR32

while True:
    for oversample_rate in bma423.oversample_rate_values:
        print("Current Oversample rate setting: ", bma.oversample_rate)
        for _ in range(10):
            accx, accy, accz = bma.acceleration
            print("x:{:.2f}m/s2, y:{:.2f}m/s2, z:{:.2f}m/s2".format(accx, accy, accz))
            time.sleep(0.5)
        bma.oversample_rate = oversample_rate
