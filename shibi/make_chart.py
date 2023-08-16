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
import calendar
import datetime
import io
import math
import os
import sys


class Shika:
    def __init__(self, name, kind):
        assert name is not None and name
        self.name = name
        self.kind = kind


class Hoshi:
    def __init__(self, name, level):
        assert name is not None and name
        self.name = name
        self.level = int(level)
        self.shikasei_list = []


class Miya:
    def __init__(self, name):
        assert name is not None and name
        self.name = name
        self.chishi = ""
        self.tenkan = ""
        self.hoshi_list = []
        self.is_shinkyu = False
        self.is_raiinkyu = False
        self.taigen_begin = 0
        self.taigen_end = 0


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
        "--date", required=True, type=str, help="Date, e.g., 2000.01.01"
    )
    parser.add_argument(
        "--time", required=True, type=str, help="Time, e.g., 21:00 or 21"
    )
    parser.add_argument(
        "--gender", required=True, type=str, help="Gender, M(ale) or F(emale)"
    )
    parser.add_argument(
        "--place", default=None, type=str, help="Place or east longitude"
    )
    parser.add_argument(
        "--eot",
        choices=["zero", "smart", "cie", "table"],
        default="smart",
        type=str,
        help="Method to compute equation of time",
    )
    parser.add_argument("--base", default=1, type=int, help="Base index [1, 12]")
    parser.add_argument("--level", default=0, type=int, help="Print level")
    args = parser.parse_args()

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    # Parse Y/m/d
    sol_year, sol_month, sol_day = [
        int(x) for x in args.date.replace("/", ".").split(".")
    ]

    # Parse H:M
    split_time = [int(x) for x in args.time.split(":")]
    if len(split_time) == 1:
        hour = split_time[0]
        minute = 0
    elif len(split_time) == 2:
        hour = split_time[0]
        minute = split_time[1]
    else:
        raise ValueError("Unexpected time")
    assert 0 <= hour <= 23
    assert 0 <= minute <= 59

    date = datetime.datetime(sol_year, sol_month, sol_day, hour, minute)
    now = datetime.datetime.now()
    print("・鑑定日：%04d.%02d.%02d" % (now.year, now.month, now.day))

    if args.gender.startswith(("m", "M")):
        is_male = True
    elif args.gender.startswith(("f", "F")):
        is_male = False
    else:
        raise ValueError("Unknown gender")
    is_female = not is_male

    # Take into account 地方時差
    if args.place is None:
        print("・時差：--分")
    else:
        # Get east longitude
        if args.place.isdigit():
            longitude = float(args.place)
        else:
            with my_open("longitude.txt") as f:
                for line in f:
                    if line.startswith(args.place):
                        ary = line.split(",")
                        longitude = float(ary[2])
                        break
        diff = (longitude - 135) * 4
        date += datetime.timedelta(minutes=diff)
        print("・時差：%+d分（東経：%.3f）" % (round(diff), longitude))

    # Take into account 均時差
    if args.eot is None or args.eot == "zero":
        print("・均時差：--分")
    else:
        if args.eot == "smart":
            # Calculate Julian Date
            def calc_jd(y, m, d):
                if m <= 2:
                    y -= 1
                    m += 12
                jd = (
                    int(365.25 * y)
                    + (y // 400)
                    - (y // 100)
                    + int(30.59 * (m - 2))
                    + d
                    + 1721088.5
                )
                return jd

            # https://www.astrogreg.com/snippets/equationoftime-simple.html
            J1 = calc_jd(sol_year, sol_month, sol_day)
            J2 = calc_jd(1900, 1, 1)
            T1 = (J1 - J2) / 36525
            T2 = T1 * T1
            T3 = T2 * T1
            rad = math.pi / 180
            eps = (
                23.452294 - 0.0130125 * T1 - 0.00000164 * T2 + 0.000000503 * T3
            ) * rad
            y = math.tan(eps / 2) ** 2
            p = 2 * math.pi
            L = (279.69668 + 36000.76892 * T1 + 0.0003025 * T2) * rad % p
            e = 0.01675104 - 0.0000418 * T1 - 0.000000126 * T2
            M = (
                (358.47583 + 35999.04975 * T1 - 0.000150 * T2 - 0.0000033 * T3)
                * rad
                % p
            )
            E = (
                y * math.sin(2 * L)
                - 2 * e * math.sin(M)
                + 4 * e * y * math.sin(M) * math.cos(2 * L)
                - 0.5 * y * y * math.sin(4 * L)
                - 1.25 * e * e * math.sin(2 * M)
            )
            diff = -E / rad / 15 * 60
        elif args.eot == "cie":
            # http://sigbox.web.fc2.com/calc/calc2.html
            D1 = datetime.datetime(sol_year, 1, 1)
            D2 = datetime.datetime(sol_year, sol_month, sol_day)
            N = 366 if calendar.isleap(sol_year) else 365
            w = 2 * math.pi / N
            J = (D2 - D1).days + 0.5
            wJ = w * J
            theta = (
                0.0072 * math.cos(1 * wJ)
                - 0.0528 * math.cos(2 * wJ)
                - 0.0012 * math.cos(3 * wJ)
                - 0.1229 * math.sin(1 * wJ)
                - 0.1565 * math.sin(2 * wJ)
                - 0.0041 * math.sin(3 * wJ)
            )
            diff = -60 * theta
        elif args.eot == "table":
            with my_open(os.path.join("equation", "%02d.txt" % sol_month)) as f:
                diff = -int(f.read().splitlines()[int(sol_day) - 1])
        else:
            raise ValueError("Unknown EOT type")
        date += datetime.timedelta(minutes=diff)
        print("・均時差：%+d分" % round(diff))

    # This is the next day
    if date.hour == 23:
        date += datetime.timedelta(days=1)

    # Convert 新暦 to 旧暦
    sol_year, sol_month, sol_day = date.year, date.month, date.day
    sol2luna = os.path.join("sol2luna", str(sol_year), "%02d.txt" % sol_month)
    with my_open(sol2luna) as f:
        luna_date = f.read().splitlines()[int(sol_day) - 1]
        bias, luna_month, luna_day = [int(x) for x in luna_date.split(",")]
        luna_year = int(sol_year) + bias

    # Compute current old
    old = now.year - luna_year + 1
    print("・数え年：%d歳" % old)

    weekday = date.strftime("%a")
    print("・新暦生年月日：%04d.%02d.%02d (%s)" % (sol_year, sol_month, sol_day, weekday))
    print("・旧暦生年月日：%04d.%02d.%02d" % (luna_year, luna_month, luna_day))
    print("・修正時間：%02d:%02d" % (date.hour, date.minute))

    # Get set of 地支
    chishi_set, num2chishi, chishi2num = get_basic("chishi")

    def add_chishi(chishi, val):
        n = chishi2num[chishi] + int(val)
        size = len(chishi2num)
        n %= size
        if n <= -1:
            n += size
        return num2chishi[str(n)]

    # Convert hour to 地支
    with my_open("hour2chishi.txt") as f:
        hour_chishi = f.read().splitlines()[date.hour]
    print("・生時支：" + hour_chishi)

    # Compute positions of 命宮 and 身宮
    col_diff = luna_month - 1
    chishi = add_chishi("寅", col_diff)
    row_diff = chishi2num[hour_chishi]
    meikyu_chishi = add_chishi(chishi, -row_diff)
    shinkyu_chishi = add_chishi(chishi, row_diff)

    # Make 十二宮 (0 is 命宮, 1 is 父母宮, and so on)
    miya_set, _, _ = get_basic("miya")
    miyas = []
    for miya_name in miya_set:
        miyas.append(Miya(miya_name))

    # Obtain 地支 for each 宮
    bias = chishi2num[meikyu_chishi]
    chishi2miya = {}
    for i, miya_name in enumerate(miya_set):
        chishi = add_chishi(chishi_set[i], bias)
        miyas[i].chishi = chishi
        chishi2miya[chishi] = i
        if chishi == shinkyu_chishi:
            miyas[i].is_shinkyu = True

    # Get set of 天干
    tenkan_set, num2tenkan, tenkan2num = get_basic("tenkan")

    def add_tenkan(tenkan, val):
        n = tenkan2num[tenkan] + int(val)
        size = len(tenkan2num)
        if n >= size:
            n -= size
        elif n <= -1:
            n += size
        return num2tenkan[str(n)]

    # Make 六十干支
    rokuju_kanshi_set = []
    idx = 0
    for _ in range(6):
        for i in tenkan_set:
            j = chishi_set[idx]
            rokuju_kanshi_set.append(i + j)
            idx += 1
            if idx == len(chishi_set):
                idx = 0

    # 甲子 is 六十干支 on 1924
    idx = (luna_year - 1924) % len(rokuju_kanshi_set)
    year_rokuju_kanshi = rokuju_kanshi_set[idx]
    year_tenkan = year_rokuju_kanshi[0]
    year_chishi = year_rokuju_kanshi[1]
    print("・干支：" + year_rokuju_kanshi)

    is_yokan = tenkan2num[year_tenkan] % 2 == 0
    is_inkan = not is_yokan
    clockwise = (is_yokan and is_male) or (is_inkan and is_female)

    with my_open("nenkan2torakan.txt") as f:
        tenkan_at_tora = f.read().splitlines()[tenkan2num[year_tenkan]]

    # Obtain 天干 for each 宮
    idx = chishi2miya["寅"]
    for i in range(len(miyas)):
        miyas[(idx + i) % len(miyas)].tenkan = add_tenkan(tenkan_at_tora, i)

    # Set 来因宮
    for miya in miyas:
        if miya.tenkan == year_tenkan and miya.chishi not in ["子", "丑"]:
            miya.is_raiinkyu = True
            break

    # Compute 五行局
    with my_open("gogyokyoku.txt") as f:
        line = f.read().splitlines()[chishi2num[meikyu_chishi]]
        gogyo = line.split(",")[tenkan2num[miyas[0].tenkan]]

    _, _, gogyo2num = get_basic("gogyo")
    with my_open("gogyo2gogyokyoku.txt") as f:
        suuji = f.read().splitlines()[gogyo2num[gogyo]]
        gogyokyoku = gogyo + suuji + "局"
    print("・五行局：" + gogyokyoku)

    # Compute position of 紫微星
    with my_open(os.path.join("positions", "shibisei.txt")) as f:
        line = f.read().splitlines()[luna_day - 1]
        shibi_pos = line.split(",")[gogyo2num[gogyo]]

    # Set 主星
    with my_open(os.path.join("positions", "shusei.txt")) as f:
        line = f.read().splitlines()[chishi2num[shibi_pos]]
        shusei_set = line.split(",")
        assert len(shusei_set) == len(miyas)

        idx = chishi2miya["子"]
        for i in range(len(shusei_set)):
            if shusei_set[i]:
                j = (idx + i) % len(miyas)
                for name in shusei_set[i].split("+"):
                    miyas[j].hoshi_list.append(Hoshi(name, 1))

    # Set 月系星
    with my_open(os.path.join("positions", "gekkeisei.txt")) as f:
        for line in f:
            ary = line.rstrip().split(",")
            name = ary[0]
            level = ary[1]
            chishi = ary[luna_month - 1 + 2]
            miyas[chishi2miya[chishi]].hoshi_list.append(Hoshi(name, level))

    # Set 時系星
    with my_open(os.path.join("positions", "jikeisei.txt")) as f:
        for line in f:
            ary = line.rstrip().split(",")
            name = ary[0]
            level = ary[1]
            chishi = ary[chishi2num[hour_chishi] + 2]
            miyas[chishi2miya[chishi]].hoshi_list.append(Hoshi(name, level))

    # Set 火星
    with my_open(os.path.join("positions", "kasei.txt")) as f:
        line = f.read().splitlines()[chishi2num[year_chishi]]
        chishi = line.split(",")[chishi2num[hour_chishi]]
        miyas[chishi2miya[chishi]].hoshi_list.append(Hoshi("火星", 0))

    # Set 鈴星
    with my_open(os.path.join("positions", "reisei.txt")) as f:
        line = f.read().splitlines()[chishi2num[year_chishi]]
        chishi = line.split(",")[chishi2num[hour_chishi]]
        miyas[chishi2miya[chishi]].hoshi_list.append(Hoshi("鈴星", 0))

    # Set 年干系星
    with my_open(os.path.join("positions", "nenkankeisei.txt")) as f:
        for line in f:
            ary = line.rstrip().split(",")
            name = ary[0]
            level = ary[1]
            chishi = ary[tenkan2num[year_tenkan] + 2]
            miyas[chishi2miya[chishi]].hoshi_list.append(Hoshi(name, level))

    # Set 年支系星
    with my_open(os.path.join("positions", "nenshikeisei.txt")) as f:
        for line in f:
            ary = line.rstrip().split(",")
            name = ary[0]
            level = ary[1]
            chishi = ary[chishi2num[year_chishi] + 2]
            miyas[chishi2miya[chishi]].hoshi_list.append(Hoshi(name, level))

    # Set 天才星
    miyas[chishi2num[year_chishi]].hoshi_list.append(Hoshi("天才", -1))

    # Set 天寿星
    for i, miya in enumerate(miyas):
        if miyas[i].is_shinkyu:
            idx = (i + chishi2num[year_chishi]) % len(miyas)
            miyas[idx].hoshi_list.append(Hoshi("天寿", -1))
            break

    def search(miya, target_name):
        for i, hoshi in enumerate(miya.hoshi_list):
            if hoshi.name == target_name:
                return i
        return -1

    # Set 日系星
    with my_open(os.path.join("positions", "nikkeisei.txt")) as f:
        for line in f:
            ary = line.rstrip().split(",")
            name = ary[0]
            level = ary[1]
            hoshi = ary[2]
            sign = int(ary[3])
            bias = int(ary[4])
            for i, miya in enumerate(miyas):
                idx = search(miya, hoshi)
                if idx != -1:
                    idx = (i + sign * (luna_day - 1 + bias)) % len(miyas)
                    if idx < 0:
                        idx += len(miyas)
                    miyas[idx].hoshi_list.append(Hoshi(name, level))
                    break
            assert idx != -1

    # Set 天傷星 and 天使星
    miyas[5].hoshi_list.append(Hoshi("天傷", -1))  # 奴僕宮
    miyas[7].hoshi_list.append(Hoshi("天使", -1))  # 疾厄宮

    # Set 長生十二星
    with my_open("gogyo2choseishi.txt") as f:
        chishi_at_chosei = f.read().splitlines()[gogyo2num[gogyo]]
    with my_open(os.path.join("positions", "chosei.txt")) as f:
        for line in f:
            ary = line.rstrip().split(",")
            name = ary[0]
            level = ary[1]
            step = int(ary[2])
            sign = 1 if clockwise else -1
            chishi = add_chishi(chishi_at_chosei, sign * step)
            miyas[chishi2miya[chishi]].hoshi_list.append(Hoshi(name, level))

    # Set 博士十二星
    with my_open(os.path.join("positions", "hakushi.txt")) as f:
        for line in f:
            ary = line.rstrip().split(",")
            name = ary[0]
            level = ary[1]
            hoshi = ary[2]
            step = int(ary[3])
            sign = 1 if clockwise else -1
            for i, miya in enumerate(miyas):
                idx = search(miya, hoshi)
                if idx != -1:
                    idx = (i + sign * step) % len(miyas)
                    if idx < 0:
                        idx += len(miyas)
                    miyas[idx].hoshi_list.append(Hoshi(name, level))
                    break
            assert idx != -1

    # Set 将前十二星
    with my_open(os.path.join("positions", "shozen.txt")) as f:
        for line in f:
            ary = line.rstrip().split(",")
            name = ary[0]
            level = ary[1]
            chishi = ary[chishi2num[year_chishi] + 2]
            miyas[chishi2miya[chishi]].hoshi_list.append(Hoshi(name, level))

    # Set 歳前十二星
    with my_open(os.path.join("positions", "saizen.txt")) as f:
        for line in f:
            ary = line.rstrip().split(",")
            name = ary[0]
            level = ary[1]
            chishi = ary[chishi2num[year_chishi] + 2]
            miyas[chishi2miya[chishi]].hoshi_list.append(Hoshi(name, level))

    # Set 生年四化
    shikasei_names = []
    shikasei_pos = []
    with my_open(os.path.join("positions", "shikasei.txt")) as f:
        for line in f:
            ary = line.rstrip().split(",")
            name = ary[0]
            hoshi = ary[tenkan2num[year_tenkan] + 1]
            shikasei_names.append(name)
            shikasei_pos.append(ary[1:])
            for miya in miyas:
                idx = search(miya, hoshi)
                if idx != -1:
                    miya.hoshi_list[idx].shikasei_list.append(Shika(name, "meikyu"))
                    break
            assert idx != -1

    # Set 流出四化
    for name, pos in zip(shikasei_names, shikasei_pos):
        for i, miya1 in enumerate(miyas):
            hoshi = pos[tenkan2num[miya1.tenkan]]
            miya2 = miyas[(i + len(miyas) // 2) % len(miyas)]
            idx = search(miya2, hoshi)
            if idx != -1:
                miya2.hoshi_list[idx].shikasei_list.append(Shika(name, "ryushutsu"))

    # Set 自化四化
    for name, pos in zip(shikasei_names, shikasei_pos):
        for miya in miyas:
            hoshi = pos[tenkan2num[miya.tenkan]]
            idx = search(miya, hoshi)
            if idx != -1:
                miya.hoshi_list[idx].shikasei_list.append(Shika(name, "jika"))

    # Get 命主
    with my_open(os.path.join("positions", "meishu.txt")) as f:
        meishu = f.read().rstrip().split(",")[chishi2num[miyas[0].chishi]]
        print("・命主：" + meishu)

    # Get 身主
    with my_open(os.path.join("positions", "shinshu.txt")) as f:
        shinshu = f.read().rstrip().split(",")[chishi2num[year_chishi]]
        print("・身主：" + shinshu)

    # Compute 大限
    _, _, suuji2num = get_basic("suuji")
    bias = suuji2num[gogyokyoku[1]]
    for i in range(len(miyas)):
        if i != 0 and not clockwise:
            idx = len(miyas) - i
        else:
            idx = i
        miyas[idx].taigen_begin = bias
        miyas[idx].taigen_end = miyas[idx].taigen_begin + 9
        bias = miyas[idx].taigen_end + 1

    # Compute 子年斗君
    nedoshitokun = add_chishi(hour_chishi, 1 - luna_month)
    print("・子年斗君：" + nedoshitokun)

    # Compute 小限
    with my_open("shogen.txt") as f:
        base_chishi = f.read().splitlines()[chishi2num[year_chishi]]
        diff = old - 1 if is_male else 1 - old
        shogen = add_chishi(base_chishi, diff)
        print("・小限：" + shogen)

    print()
    for i in range(len(miyas)):
        tc = miyas[i].tenkan + miyas[i].chishi
        print("・%02d　%s／" % (i + 1, tc), end="")
        print(miyas[i].name, end="")
        if args.base != 1:
            m = miyas[(i + 13 - args.base) % len(miyas)].name
            print("（%s）" % m, end="")
        if miyas[i].is_shinkyu:
            print("　身宮", end="")
        if miyas[i].is_raiinkyu:
            print("　来因宮", end="")
        print()

        prev_is_shusei = None
        zatsuyo = False
        if miyas[i].hoshi_list:
            for hoshi in miyas[i].hoshi_list:
                if hoshi.level < args.level:
                    continue
                is_shusei = hoshi.level == 1
                if prev_is_shusei is None:
                    print("　", end="")
                elif prev_is_shusei != is_shusei:
                    print("\n　", end="")
                elif hoshi.level <= -2 and not zatsuyo:
                    print("\n　", end="")
                    zatsuyo = True
                prev_is_shusei = is_shusei

                print(hoshi.name, end="")
                for shikasei in hoshi.shikasei_list:
                    if shikasei.kind == "meikyu":
                        print("(" + shikasei.name + ")", end="")
                    elif shikasei.kind == "ryushutsu":
                        print("<" + shikasei.name + ">", end="")
                    elif shikasei.kind == "jika":
                        print("|" + shikasei.name + "|", end="")
                print("　", end="")
            print()

        print("　（大限：%d ～ %d 歳）" % (miyas[i].taigen_begin, miyas[i].taigen_end))
        print()


if __name__ == "__main__":
    main()
