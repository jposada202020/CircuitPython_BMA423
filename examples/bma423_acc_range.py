# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
import board
import bma423

i2c = board.I2C()
bma = bma423.BMA423(i2c)

bma.acc_range = bma423.ACC_RANGE_8

while True:
    for acc_range in bma423.acc_range_values:
        print("Current Acc range setting: ", bma.acc_range)
        for _ in range(10):
            accx, accy, accz = bma.acceleration
            print("x:{:.2f}m/s2, y:{:.2f}m/s2, z:{:.2f}m/s2".format(accx, accy, accz))
            time.sleep(0.5)
        bma.acc_range = acc_range
