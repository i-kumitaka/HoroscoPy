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


def to_single(n):
    n = int(n)
    while n >= 10:
        n = sum([int(i) for i in str(n)])
    return n


def main():
    parser = argparse.ArgumentParser(description="Calculate numbers")
    parser.add_argument(
        "--date", required=True, type=str, help="Date, e.g., 2000.01.01"
    )
    parser.add_argument(
        "--name", required=True, type=str, help="Full name, e.g., Your Name"
    )
    args = parser.parse_args()

    processed_date = args.date.replace(".", "")
    processed_date = processed_date.replace("/", "")

    table = {}
    with open(os.path.join("res", "pythagorean.txt")) as f:
        for line in f:
            k, v = line.rstrip().split(",")
            table[k] = v

    with open(os.path.join("res", "vowels.txt")) as f:
        vowels = f.read().splitlines()

    processed_name = args.name.replace(" ", "")
    processed_name = processed_name.upper()

    vowels_in_name = ""
    consonants_in_name = ""
    for c in processed_name:
        if c in vowels:
            vowels_in_name += c
        else:
            consonants_in_name += c

    assert len(vowels_in_name) > 0
    assert len(consonants_in_name) > 0

    # Calculate birth number.
    n_b = to_single(processed_date)
    print("B: %d" % n_b)

    # Calculate destiny number.
    n_d = to_single("".join([table[i] for i in processed_name]))
    print("D: %d" % n_d)

    # Calculate soul number.
    n_s = to_single("".join([table[i] for i in vowels_in_name]))
    print("S: %d" % n_s)

    # Calculate personality number.
    n_p = to_single("".join([table[i] for i in consonants_in_name]))
    print("P: %d" % n_p)

    # Calculate realization number.
    n_r = to_single(n_b + n_d)
    print("R: %d" % n_r)


if __name__ == "__main__":
    main()
