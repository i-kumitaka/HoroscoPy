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

import argparse
import datetime
import os


class Circle:
    def __init__(self, num):
        self.num = num
        self.green_month = None
        self.green_year = None
        self.white_month = None
        self.white_year = None


def to_single(n):
    n = int(n)
    while n >= 10:
        n = sum([int(i) for i in str(n)])
    return n


def my_open(filename):
    return open(os.path.join("res", filename), encoding="utf-8")


def get_basic(basename):
    with my_open(os.path.join("basics", basename + ".txt")) as f:
        names = f.read().splitlines()
        num2name = {i: names[i] for i in range(len(names))}
        name2num = {v: k for k, v in num2name.items()}
        return names, num2name, name2num


def main():
    parser = argparse.ArgumentParser(description="Make a chart")
    parser.add_argument(
        "--date", required=True, type=str, help="Date, e.g., 2000.01.01"
    )
    parser.add_argument(
        "--hour", default=None, type=str, help="Modified hour, e.g., 00:00"
    )
    args = parser.parse_args()

    # Modify date
    year, month, day = [int(x) for x in args.date.replace("/", ".").split(".")]
    if args.hour is None:
        hour, minute = 0, 0
    else:
        hour, minute = [int(x) for x in args.hour.split(":")]
    date = datetime.datetime(year, month, day, hour=hour, minute=minute)
    if date.hour == 23:
        delta = datetime.timedelta(days=1)
        modified_date = date + delta
    else:
        modified_date = date

    # Check ??????
    with my_open("setsuiri.txt") as f:
        lines = f.read().splitlines()
        line = lines[(year - 1955) * 12 + (month - 1)]
        setsuiri = datetime.datetime(*[int(x) for x in line.split(",")])
        before_setsuiri = date < setsuiri

        line = lines[(year - 1955) * 12 + 1]
        risshun = datetime.datetime(*[int(x) for x in line.split(",")])
        before_risshun = date < risshun

    with my_open("ijo_kanshi.txt") as f:
        ijo_kanshi = f.read().splitlines()

    _, num2kanshi, _ = get_basic("kanshi")
    y = year - 1 if before_risshun else year
    year_kanshi = num2kanshi[(y - 1924) % len(num2kanshi)]
    print("????????????" + year_kanshi, end="")
    if year_kanshi in ijo_kanshi:
        print("* ", end="")
    else:
        print("  ", end="")

    _, num2kyusei, _ = get_basic("kyusei")
    year_kyusei = num2kyusei[8 - (y - 1928) % len(num2kyusei)]
    print("????????????" + year_kyusei)

    m = (12 if month == 1 else month - 1) if before_setsuiri else month
    month_kanshi = num2kanshi[((year - 1928) * 12 - 12 + m) % len(num2kanshi)]
    print("????????????" + month_kanshi, end="")
    if month_kanshi in ijo_kanshi:
        print("* ", end="")
    else:
        print("  ", end="")

    month_kyusei = num2kyusei[8 - ((year - 1928) * 12 - 7 + m) % len(num2kyusei)]
    print("????????????" + month_kyusei)

    sol2kanshi = os.path.join(
        "sol2kanshi", str(modified_date.year), "%02d" % modified_date.month + ".txt"
    )
    with my_open(sol2kanshi) as f:
        day_kyusei, day_kanshi = f.read().splitlines()[modified_date.day - 1].split(",")
        day_kanshi = num2kanshi[int(day_kanshi)]
        day_kyusei = num2kyusei[int(day_kyusei) - 1]
    print("????????????" + day_kanshi, end="")
    if day_kanshi in ijo_kanshi:
        print("* ", end="")
    else:
        print("  ", end="")
    print("????????????" + day_kyusei, end="  ")

    with my_open("kubo.txt") as f:
        kubo = None
        for line in f:
            ary = line.rstrip().split(",")
            if day_kanshi in ary[1:]:
                kubo = ary[0]
                break
        assert kubo is not None
    print(kubo + "??????")

    tenkan_set, _, _ = get_basic("tenkan")
    chishi_set, _, _ = get_basic("chishi")

    if args.hour is not None:
        bias1 = tenkan_set.index(day_kanshi[0]) % 5
        bias2 = 0 if hour == 23 else (hour + 1) // 2
        hour_kanshi = num2kanshi[bias1 * 12 + bias2]
        print("????????????" + hour_kanshi, end="")
        if hour_kanshi in ijo_kanshi:
            print("* ", end="")
        else:
            print("  ", end="")
        print()

    circles = [Circle(12 if i == 0 else i) for i in range(12)]
    print(" " * len("Private Month |"), end="")
    for circle in circles:
        print("%5d" % circle.num, end="")
    print()
    print("-" * len("Private Month |"), end="")
    for _ in circles:
        print("-----", end="")
    print()

    n = month
    s = 1
    for i in range(12):
        circles[(s + i) % 12].green_month = (n - 1 + i) % 12 + 1
    print(" Public Month |", end="")
    for circle in circles:
        print("%5d" % circle.green_month, end="")
    print()

    n = to_single(year)
    s = 1
    for i in range(12):
        circles[(s + i) % 12].green_year = to_single(n + i)
    print("  Public Year |", end="")
    for circle in circles:
        print("%5d" % circle.green_year, end="")
    print()

    tenkan = month_kanshi[0]
    is_yokan = tenkan_set.index(tenkan) % 2 == 0

    n = chishi_set.index(kubo[0])
    s = 1 if is_yokan else 0
    for i in range(12):
        circles[(s + i) % 12].white_month = (n + i) % 12 + 1
    print("Private Month |", end="")
    for circle in circles:
        print("%5d" % circle.white_month, end="")
    print()

    tenkan = year_kanshi[0]
    is_yokan = tenkan_set.index(tenkan) % 2 == 0

    n = chishi_set.index(kubo[0])
    s = 1 if is_yokan else 0
    for i in range(12):
        circles[(s + i) % 12].white_year = chishi_set[(n + i) % 12]
    print(" Private Year |", end="")
    for circle in circles:
        print("%4s" % circle.white_year, end="")
    print()


if __name__ == "__main__":
    main()
