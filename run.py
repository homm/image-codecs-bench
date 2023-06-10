#!/usr/bin/env python

import csv
import os.path
import subprocess
import time
from collections import namedtuple
from glob import glob

from PIL import Image


INPUT = "./input"
OUTPUT = "./output"
PassResult = namedtuple('PassResult', 'infile fname size enc_time perf dssim')


def encode_libavif(infile, outfile, *, speed=None, quality=None):
    cmd = ["avifenc", infile, outfile]
    if speed is not None:
        assert 0 <= speed <= 10
        cmd.extend(['--speed', str(speed)])
    if quality is not None:
        assert 0 <= quality <= 63
        cmd.extend(['--min', str(quality)])
        cmd.extend(['--max', str(quality)])
    # print('$', " ".join(cmd))
    start = time.time()
    avifenc = subprocess.check_output(cmd).decode()
    return time.time() - start, os.stat(outfile).st_size


def decode_libavif(infile, outfile):
    cmd = ["avifdec", infile, outfile]
    # print('$', " ".join(cmd))
    avifdec = subprocess.check_output(cmd).decode()
    # print(avifdec)


def calc_dssim(infile, outfile):
    dssim = subprocess.check_output(["dssim", infile, outfile])
    return float(dssim.partition(b'\t')[0]) * 100


def test_libavif(infile, speed, quality):
    res = Image.open(infile).size
    fname, _ = os.path.splitext(os.path.basename(infile))
    fname = f'{fname}.s{speed}.q{quality}'
    outfile = f'{OUTPUT}/{fname}'

    enc_time, size = encode_libavif(
        infile, f'{outfile}.avif', speed=speed, quality=quality)
    decode_libavif(f'{outfile}.avif', f'{outfile}.png')
    dssim = calc_dssim(infile, f'{outfile}.png')
    os.unlink(f'{outfile}.png')

    perf = res[0] * res[1] / enc_time / 1000 / 1000
    return PassResult(infile, fname, size, enc_time, perf, dssim)


src_files = glob(f"{INPUT}/parrots.png")


with open('libavif.csv', 'w', newline='') as csvfp:
    csvwriter = csv.writer(csvfp)
    csvwriter.writerow("fname speed quality size enc_time perf dssim".split())
    for infile in src_files:
        for quality in range(10, 45, 2):
            speed = 4
            for speed in range(1, 10):
                res = test_libavif(infile, speed, quality)
                csvwriter.writerow(res[1:2] + (speed, quality) + res[2:])
                csvfp.flush()
                print('>>> {fname:18} {size:7} {enc_time:6.3f}s {perf:5.2f}Mps {dssim:7.3f}'.format(**res._asdict()))
            print()

