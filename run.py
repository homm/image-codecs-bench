#!/usr/bin/env python

import csv
import os.path
import subprocess
import time
from collections import namedtuple
from glob import glob
from tempfile import NamedTemporaryFile

from PIL import Image

from tools.bisect import bisect_function


INPUT = "./input"
OUTPUT = "./output"
PassResult = namedtuple('PassResult', 'fname codec outname size enc_time perf dssim')


def encode_libavif(infile, outfile, *, speed=None, quality=None):
    cmd = ["avifenc", infile, outfile]
    if speed is not None:
        assert 0 <= speed <= 10
        cmd.extend(['--speed', str(speed)])
        if speed >= 7 and quality is not None:
            quality -= 2

    if quality is not None:
        assert 0 <= quality <= 63
        cmd.extend(['--min', str(quality)])
        cmd.extend(['--max', str(quality)])
        cmd.extend(['--minalpha', str(quality // 2)])
        cmd.extend(['--maxalpha', str(quality // 2)])
    # print('$', " ".join(cmd))
    start = time.time()
    avifenc = subprocess.check_output(cmd).decode()
    return time.time() - start, os.stat(outfile).st_size


def decode_libavif(infile, outfile):
    cmd = ["avifdec", infile, outfile]
    avifdec = subprocess.check_output(cmd).decode()


def encode_webp(infile, outfile, *, quality=None):
    cmd = ["cwebp", infile, '-o', outfile]

    if quality is not None:
        assert 0 <= quality <= 100
        cmd.extend(['-q', str(quality)])
    # print('$', " ".join(cmd))
    start = time.time()
    cwebp = subprocess.check_output(cmd, stderr=subprocess.PIPE).decode()
    return time.time() - start, os.stat(outfile).st_size


def decode_webp(infile, outfile):
    cmd = ["dwebp", infile, '-o', outfile]
    dwebp = subprocess.check_output(cmd, stderr=subprocess.PIPE).decode()


def calc_dssim(infile, outfile):
    cmd = ["dssim", infile, outfile]
    dssim = subprocess.check_output(cmd, env={'RAYON_NUM_THREADS': '1'})
    return float(dssim.partition(b'\t')[0]) * 100


def test_libavif(infile, speed, quality):
    res = Image.open(infile).size
    fname, _ = os.path.splitext(os.path.basename(infile))
    outname = f'{fname}.s{speed}.q{quality}'
    outfile = f'{OUTPUT}/{outname}.avif'

    enc_time, size = encode_libavif(
        infile, outfile, speed=speed, quality=quality)
    with NamedTemporaryFile(suffix='.png') as temp_png:
        decode_libavif(outfile, temp_png.name)
        dssim = calc_dssim(infile, temp_png.name)

    perf = res[0] * res[1] / enc_time / 1000 / 1000
    return PassResult(fname, 'libavif', outname, size, enc_time, perf, dssim)


test_webp_func_cache = {}

def test_webp_func(infile):
    res = Image.open(infile).size
    fname, _ = os.path.splitext(os.path.basename(infile))
    cache = test_webp_func_cache

    def webp_test(quality):
        if quality.is_integer():
            quality = round(quality)
        key = (infile, quality)
        if key not in cache:
            outname = f'{fname}.q{quality}'
            outfile = f'{OUTPUT}/{outname}.webp'
            enc_time, size = encode_webp(infile, outfile, quality=quality)
            with NamedTemporaryFile(suffix='.png') as temp_png:
                decode_webp(outfile, temp_png.name)
                dssim = calc_dssim(infile, temp_png.name)
            perf = res[0] * res[1] / enc_time / 1000 / 1000
            cache[key] = PassResult(fname, 'webp', outname, size, enc_time, perf, dssim)
        return cache[key]
    return webp_test


src_files = glob(f"{INPUT}/*.png")
# src_files = [f"{INPUT}/mars.png"]


with open('libavif.csv', 'w', newline='') as csvfp:
    csvwriter = csv.writer(csvfp)
    csvwriter.writerow("fname codec effort quality outname size enc_time perf dssim".split())
    for infile in src_files:
        for quality in range(10, 45, 2):
            for speed in (5, 7):
                res = test_libavif(infile, speed, quality)
                csvwriter.writerow(res[0:2] + (speed, quality) + res[2:])
                print('>>> {outname:18} {size:7} {enc_time:6.3f}s {perf:5.2f}Mps {dssim:7.3f}'.format(**res._asdict()))

                res, q = bisect_function(
                    test_webp_func(infile), 0, 100, res.dssim, step=0.5,
                    invert=True, key=lambda x: x.dssim)
                csvwriter.writerow(res[0:2] + (speed, quality) + res[2:])
                print('>>> {outname:18} {size:7} {enc_time:6.3f}s {perf:5.2f}Mps {dssim:7.3f}'.format(**res._asdict()))
                csvfp.flush()
            print()

