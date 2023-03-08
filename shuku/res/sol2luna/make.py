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

    luna2shuku = {i: {} for i in range(1, 13)}
    with open(os.path.join("res", "sluna2shuku.txt")) as f:
        for line in f:
            month, day, shuku = [int(x) for x in line.rstrip().split(",")]
            luna2shuku[month][day] = shuku

    ryohan_kikan = {i: {} for i in range(1, 13)}
    with open(os.path.join("res", "ryohan_kikan.txt")) as f:
        for i, line in enumerate(f):
            dow1, b1, e1, dow2, b2, e2 = [int(x) for x in line.rstrip().split(",")]
            month = i + 1
            ryohan_kikan[month][dow1] = (b1, e1)
            ryohan_kikan[month][dow2] = (b2, e2)

    sanshubi = []
    with open(os.path.join("res", "sanshubi.txt")) as f:
        for i, line in enumerate(f):
            sanshubi.append(
                {i: int(x) for i, x in enumerate(line.rstrip().split(","), start=1)}
            )

    with open(os.path.join("res", "lunar_calender.txt")) as f_in:
        # 1955/01/01 on lunar calender
        sol_year = 1955
        sol_month = 1
        sol_day = 24
        dow = 1  # Monday

        first = True
        extend = False
        ryohan_begin, ryohan_end = 0, 0

        os.makedirs(str(sol_year), exist_ok=True)

        for line in f_in:
            luna_year, _, luna_month, is_thirty = [
                int(x) for x in line.rstrip().split(",")
            ]

            num_luna_days = 30 if is_thirty else 29
            for luna_day in range(1, num_luna_days + 1):
                y = -1 if sol_year > luna_year else 0
                m = luna_month
                d = luna_day
                s = luna2shuku[m][d]

                is_sanshu = []
                for i in range(len(sanshubi)):
                    is_sanshu.append("1" if sanshubi[i][dow] == s else "0")
                is_sanshu = ",".join(is_sanshu)

                if d == 1:
                    if dow in ryohan_kikan[m]:
                        ryohan_begin, ryohan_end = ryohan_kikan[m][dow]
                    else:
                        ryohan_begin, ryohan_end = 0, 0

                if ryohan_begin <= d <= ryohan_end:
                    is_ryohan = 1
                else:
                    is_ryohan = 0

                if not first:
                    f_out.write(
                        "%+d,%02d,%02d,%s,%1d,%1d\n"
                        % (y, m, d, is_sanshu, is_ryohan, s)
                    )

                dow += 1
                if 7 < dow:
                    dow = 1

                sol_day += 1
                if num_sol_days[sol_month] < sol_day:
                    if sol_month == 2 and not extend:
                        if sol_year % 400 == 0 or (
                            sol_year % 4 == 0 and sol_year % 100 != 0
                        ):
                            extend = True
                            continue

                    sol_month += 1
                    sol_day = 1
                    if 12 < sol_month:
                        sol_year += 1
                        sol_month = 1
                        extend = False
                        os.makedirs(str(sol_year), exist_ok=True)

                    if first:
                        first = False
                    else:
                        f_out.close()

                    f_out = open(
                        os.path.join(str(sol_year), "%02d.txt" % sol_month), mode="w"
                    )

        f_out.close()


if __name__ == "__main__":
    main()
