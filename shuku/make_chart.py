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
import io
import os
import sys


def my_open(filename):
    return open(os.path.join("res", filename), encoding="utf-8")


def get_basic(basename):
    with my_open(os.path.join("basics", basename + ".txt")) as f:
        names = f.read().splitlines()
        num2name = {str(i): names[i] for i in range(len(names))}
        name2num = {v: int(k) for k, v in num2name.items()}
        return names, num2name, name2num


def main():
    parser = argparse.ArgumentParser(description="Make a chart")
    parser.add_argument(
        "--date", required=True, type=str, help="Birth date, e.g., 2000.01.01"
    )
    parser.add_argument(
        "--check",
        default=None,
        type=str,
        help="Month and year to be checked, e.g., 2010.01",
    )
    args = parser.parse_args()

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    # Get 宿
    split_date = args.date.replace("/", ".").split(".")
    sol_year, sol_month, sol_day = split_date
    sol2luna = os.path.join("sol2luna", sol_year, sol_month + ".txt")
    with my_open(sol2luna) as f:
        data = f.read().splitlines()[int(sol_day) - 1]
        your_shuku = data.rsplit(",", 1)[1]

    _, num2shuku, _ = get_basic("shuku")
    print(num2shuku[your_shuku] + "宿")
    print()

    if args.check is None:
        check_date = datetime.datetime.now().strftime("%Y.%m")
    else:
        check_date = args.check
    check_date = check_date.replace("/", ".").split(".")
    check_year, check_month = check_date

    # Get 六害宿
    rokugaishuku = {}
    with my_open("rokugaishuku.txt") as f:
        for line in f:
            bias, shuku = line.rstrip().split(",")
            idx = (int(your_shuku) + int(bias)) % 27
            rokugaishuku[str(idx)] = shuku + "宿"
    assert len(rokugaishuku) == 6

    # Search 六害宿
    for i in range(1, 13):
        month = "%02d" % i
        sol2luna = os.path.join("sol2luna", check_year, month + ".txt")
        with my_open(sol2luna) as f:
            for day, line in enumerate(f, start=1):
                if line[15] == "1":
                    for k, v in rokugaishuku.items():
                        if line[17:-1] == k:
                            print("%s/%s/%02d %s" % (check_year, month, day, v))
    print()

    # Get 三九の秘宝
    sanku = {}
    with my_open("sanku_hihou.txt") as f:
        for bias, line in enumerate(f):
            idx = (int(your_shuku) + int(bias)) % 27
            sanku[str(idx)] = line.rstrip()
    assert len(sanku) == 27

    # Get 三種日
    _, num2sanshu, _ = get_basic("sanshu")

    # Show the result
    sol2luna = os.path.join("sol2luna", check_year, check_month + ".txt")
    with my_open(sol2luna) as f:
        for day, line in enumerate(f, start=1):
            n = line[17:-1]
            print(
                "%s/%s/%02d %s %s "
                % (check_year, check_month, day, num2shuku[n], sanku[n]),
                end="",
            )
            end = False
            for k, v in num2sanshu.items():
                if line[9 + 2 * int(k)] == "1":
                    print(v)
                    end = True
                    break
            if not end:
                print()


if __name__ == "__main__":
    main()
