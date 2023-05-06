# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
import board
import bma423

i2c = board.I2C()  # uses board.SCL and board.SDA
bma = bma423.BMA423(i2c)

for i in range(10):
    print(bma.acceleration)
    print(bma.temperature)
    time.sleep(2)
