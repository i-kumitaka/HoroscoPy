#!/usr/bin/env python
#
# Copyright (c) 2022 Kumitaka Izumi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os


def main():
    with open(os.path.join("res", "sol_days.txt")) as f:
        data = f.read().splitlines()
        num_sol_days = {i: int(x) for i, x in enumerate(data, start=1)}
    assert sum(num_sol_days.values()) == 365

    inton_yoton = []
    with open(os.path.join("res", "inton_yoton.txt")) as f:
        for line in f:
            _, m1, d1, m2, d2 = [int(x) for x in line.rstrip().split(",")]
            inton_yoton.append([m1, d1])
            inton_yoton.append([m2, d2])

    idx = 1
    kanshi = 57
    kyusei = 3
    is_inton = True

    for y in range(1955, 2031):
        os.makedirs(str(y), exist_ok=True)
        for m in range(1, 13):
            f_out = open(os.path.join(str(y), "%02d.txt" % m), mode="w")

            n_days = num_sol_days[m]
            if m == 2 and (y % 400 == 0 or (y % 4 == 0 and y % 100 != 0)):
                n_days += 1
            for d in range(1, n_days + 1):
                kanshi += 1
                if 60 <= kanshi:
                    kanshi = 0
                if m == inton_yoton[idx][0] and d == inton_yoton[idx][1]:
                    idx += 1
                    is_inton = not is_inton
                    assert kanshi == 0 or kanshi == 30, "%d,%d,%d: %d" % (
                        y,
                        m,
                        d,
                        kanshi,
                    )
                    if is_inton and kanshi == 0:
                        assert kyusei == 9
                    elif not is_inton and kanshi == 0:
                        assert kyusei == 1
                    else:
                        assert kyusei == 3 or kyusei == 7, "%d,%d,%d: %d" % (
                            y,
                            m,
                            d,
                            kyusei,
                        )
                else:
                    if is_inton:
                        kyusei -= 1
                        if kyusei == 0:
                            kyusei = 9
                    else:
                        kyusei += 1
                        if kyusei == 10:
                            kyusei = 1
                f_out.write("%d,%d\n" % (kyusei, kanshi))

            f_out.close()


if __name__ == "__main__":
    main()
