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


def is_yokan(tenkan):
    with open(os.path.join("res", "tenkan.txt"), encoding="utf-8") as f:
        tenkan_set = f.read().splitlines()
        index = tenkan_set.index(tenkan)
        return index % 2 == 0


def main():
    parser = argparse.ArgumentParser(description="Make a chart")
    parser.add_argument(
        "--nenkanshi", required=False, default=None, type=str, help="年干支, e.g., 甲子"
    )
    parser.add_argument(
        "--gekkanshi", required=False, default=None, type=str, help="月干支, e.g., 甲子"
    )
    parser.add_argument(
        "--nikkanshi", required=False, default=None, type=str, help="日干支, e.g., 甲子"
    )
    parser.add_argument(
        "--year", required=False, default=None, type=int, help="Birth year, e.g., 2000"
    )
    parser.add_argument(
        "--month", required=False, default=None, type=int, help="Birth month, e.g., 11"
    )
    args = parser.parse_args()

    circles = [Circle(12 if i == 0 else i) for i in range(12)]
    print("    ", end="")
    for circle in circles:
        print("%5d" % circle.num, end="")
    print()
    print("----", end="")
    for _ in circles:
        print("-----", end="")
    print()

    if args.month is not None:
        assert 1 <= args.month <= 12

        n = args.month
        s = 1
        for i in range(12):
            circles[(s + i) % 12].green_month = (n - 1 + i) % 12 + 1

        print("GM |", end="")
        for circle in circles:
            print("%5d" % circle.green_month, end="")
        print()

    if args.year is not None:
        n = to_single(args.year)
        s = 1
        for i in range(12):
            circles[(s + i) % 12].green_year = to_single(n + i)

        print("GY |", end="")
        for circle in circles:
            print("%5d" % circle.green_year, end="")
        print()

    # Get 空亡
    kubo = None
    if args.gekkanshi is not None or args.nenkanshi is not None:
        assert args.nikkanshi is not None
        with open(os.path.join("res", "kubo.txt"), encoding="utf-8") as f:
            for line in f:
                ary = line.rstrip().split(",")
                if args.nikkanshi in ary[1:]:
                    kubo = ary[0]
                    break
        assert kubo is not None, "%s is wrong" % args.nikkanshi

    if args.gekkanshi is not None:
        assert len(args.gekkanshi) == 2

        tenkan, _ = list(args.gekkanshi)
        with open(os.path.join("res", "chishi.txt"), encoding="utf-8") as f:
            chishi_set = f.read().splitlines()
            n = chishi_set.index(kubo[0]) + 1
        s = 1 if is_yokan(tenkan) else 0
        for i in range(12):
            circles[(s + i) % 12].white_month = (n - 1 + i) % 12 + 1

        print("WM |", end="")
        for circle in circles:
            print("%5d" % circle.white_month, end="")
        print()

    if args.nenkanshi is not None:
        assert len(args.nenkanshi) == 2

        tenkan, _ = list(args.nenkanshi)
        with open(os.path.join("res", "chishi.txt"), encoding="utf-8") as f:
            chishi_set = f.read().splitlines()
            n = chishi_set.index(kubo[0])
        s = 1 if is_yokan(tenkan) else 0
        for i in range(12):
            circles[(s + i) % 12].white_year = chishi_set[(n + i) % 12]

        print("WY |", end="")
        for circle in circles:
            print("%4s" % circle.white_year, end="")
        print()


if __name__ == "__main__":
    main()
