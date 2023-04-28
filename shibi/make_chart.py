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


class Shika:
    def __init__(self, name, kind):
        assert name is not None and name
        self.name = name
        self.kind = kind


class Hoshi:
    def __init__(self, name, is_shusei):
        assert name is not None and name
        self.name = name
        self.is_shusei = is_shusei
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
    parser.add_argument("--time", required=True, type=str, help="Time, e.g., 21:00")
    parser.add_argument("--place", default=None, type=str, help="Place")
    parser.add_argument("--gender", required=True, type=str, help="Gender, M or F")
    parser.add_argument("--base", default=1, type=int, help="Base index [1, 12]")
    parser.add_argument(
        "--eot", action="store_true", help="If true, use equation of time"
    )
    args = parser.parse_args()

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    sol_year, sol_month, sol_day = [
        int(x) for x in args.date.replace("/", ".").split(".")
    ]

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

    now = datetime.datetime.now()
    print("・鑑定日：%04d.%02d.%02d" % (now.year, now.month, now.day))

    date = datetime.datetime(sol_year, sol_month, sol_day, hour, minute)

    # Take into account 地方時差
    if args.place is not None:
        find = False
        with my_open("longitude.txt") as f:
            for line in f:
                if line.startswith(args.place):
                    longitude = float(line.split(",")[2])
                    find = True
                    break
        if find:
            diff = (longitude - 135) * 4
            date += datetime.timedelta(minutes=diff)
            print("・時差：%+d分" % round(diff))
        else:
            print("・時差：??分")

    # Take into account 均時差
    if args.eot:
        with my_open(os.path.join("equation", "%02d.txt" % sol_month)) as f:
            diff = -int(f.read().splitlines()[int(sol_day) - 1])
            date += datetime.timedelta(minutes=diff)
            print("・均時差：%+d分" % diff)

    # This is the next day.
    if date.hour == 23:
        date += datetime.timedelta(day=1)

    if args.gender.startswith(("m", "M")):
        is_male = True
    elif args.gender.startswith(("f", "F")):
        is_male = False
    else:
        raise ValueError("Unknown gender")

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
        if n >= size:
            n -= size
        elif n <= -1:
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
                    miyas[j].hoshi_list.append(Hoshi(name, True))

    # Set 月系星
    with my_open(os.path.join("positions", "gekkeisei.txt")) as f:
        for line in f:
            ary = line.rstrip().split(",")
            name = ary[0]
            chishi = ary[luna_month - 1 + 1]
            miyas[chishi2miya[chishi]].hoshi_list.append(Hoshi(name, False))

    # Set 時系星
    with my_open(os.path.join("positions", "jikeisei.txt")) as f:
        for line in f:
            ary = line.rstrip().split(",")
            name = ary[0]
            chishi = ary[chishi2num[hour_chishi] + 1]
            miyas[chishi2miya[chishi]].hoshi_list.append(Hoshi(name, False))

    # Set 火星
    with my_open(os.path.join("positions", "kasei.txt")) as f:
        line = f.read().splitlines()[chishi2num[year_chishi]]
        chishi = line.split(",")[chishi2num[hour_chishi]]
        miyas[chishi2miya[chishi]].hoshi_list.append(Hoshi("火星", False))

    # Set 鈴星
    with my_open(os.path.join("positions", "reisei.txt")) as f:
        line = f.read().splitlines()[chishi2num[year_chishi]]
        chishi = line.split(",")[chishi2num[hour_chishi]]
        miyas[chishi2miya[chishi]].hoshi_list.append(Hoshi("鈴星", False))

    # Set 年干系星
    with my_open(os.path.join("positions", "nenkankeisei.txt")) as f:
        for line in f:
            ary = line.rstrip().split(",")
            name = ary[0]
            chishi = ary[tenkan2num[year_tenkan] + 1]
            miyas[chishi2miya[chishi]].hoshi_list.append(Hoshi(name, False))

    # Set 年支系星
    with my_open(os.path.join("positions", "nenshikeisei.txt")) as f:
        for line in f:
            ary = line.rstrip().split(",")
            name = ary[0]
            chishi = ary[chishi2num[year_chishi] + 1]
            miyas[chishi2miya[chishi]].hoshi_list.append(Hoshi(name, False))

    def search(miya, target_name):
        for i, hoshi in enumerate(miya.hoshi_list):
            if hoshi.name == target_name:
                return i
        return -1

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
    is_yokan = tenkan2num[year_tenkan] % 2 == 0
    is_inkan = not is_yokan
    for i in range(len(miyas)):
        if i != 0 and ((is_yokan and not is_male) or (is_inkan and is_male)):
            idx = len(miyas) - i
        else:
            idx = i
        miyas[idx].taigen_begin = bias
        miyas[idx].taigen_end = miyas[idx].taigen_begin + 9
        bias = miyas[idx].taigen_end + 1

    # Compute 子年斗君
    nedoshitokun = add_chishi(hour_chishi, 1 - luna_month)
    print("・子年斗君：" + nedoshitokun)

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
        if miyas[i].hoshi_list:
            for hoshi in miyas[i].hoshi_list:
                if prev_is_shusei is None:
                    print("　", end="")
                elif prev_is_shusei != hoshi.is_shusei:
                    print("\n　", end="")
                prev_is_shusei = hoshi.is_shusei

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
