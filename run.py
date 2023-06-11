#!/usr/bin/env python

import csv
import os.path
import subprocess
import time
from collections import namedtuple
from glob import glob
from tempfile import NamedTemporaryFile

from PIL import Image


INPUT = "./input"
OUTPUT = "./output"
PassResult = namedtuple('PassResult', 'fname outname size enc_time perf dssim')


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
    outfile = f'{OUTPUT}/{outname}'

    enc_time, size = encode_libavif(
        infile, f'{outfile}.avif', speed=speed, quality=quality)
    decode_libavif(f'{outfile}.avif', f'{outfile}.png')
    dssim = calc_dssim(infile, f'{outfile}.png')
    os.unlink(f'{outfile}.png')

    perf = res[0] * res[1] / enc_time / 1000 / 1000
    return PassResult(fname, outname, size, enc_time, perf, dssim)


src_files = glob(f"{INPUT}/*.png")
src_files = [f"{INPUT}/mars.png"]


from tools.bisect import bisect_function


def webp_size(quality):
    outfile = f'./parrots.q{quality}.webp'
    enc_time, size = encode_webp(f"{INPUT}/parrots.png", outfile, quality=quality)
    return size


def webp_dssim(quality):
    if quality.is_integer():
        quality = round(quality)
    infile = f"{INPUT}/parrots.png"
    outfile = f'./parrots.q{quality}.webp'
    enc_time, size = encode_webp(infile, outfile, quality=quality)
    with NamedTemporaryFile(suffix='.png') as temp_png:
        decode_webp(outfile, temp_png.name)
        dssim = calc_dssim(infile, temp_png.name)
    return dssim


error = 0
for target in [0.048, 0.059, 0.071, 0.084, 0.097, 0.112, 0.126, 0.144, 0.177, 0.210, 0.246, 0.306, 0.360, 0.434, 0.517, 0.605, 0.712, 0.832]:
    val, q = bisect_function(webp_dssim, 0, 100, target, step=0.5, delta=0, invert=True)
    error += abs(target - val) / target
    print('>>>', val, q, abs(target - val) / target)

raise ValueError(f'{error=}')


with open('libavif.csv', 'w', newline='') as csvfp:
    csvwriter = csv.writer(csvfp)
    csvwriter.writerow("fname speed quality outname size enc_time perf dssim".split())
    for infile in src_files:
        for quality in range(10, 45, 2):
            speed = 4
            for speed in range(5, 10):
                res = test_libavif(infile, speed, quality)
                csvwriter.writerow(res[0:1] + (speed, quality) + res[1:])
                csvfp.flush()
                print('>>> {outname:18} {size:7} {enc_time:6.3f}s {perf:5.2f}Mps {dssim:7.3f}'.format(**res._asdict()))
            print()

