# Codecs overview

## libavif (AOM)

### qmax-qmin

Compression is always done with q = (qmax + qmin)/2.
So q=10-34 is euivalent of q=22-22.

### Speed 0

Always 3x compression time compared to s=1, always +0.2-1.5% to size,
a reasonable dssim drop from time to time.

### Speed 10

Identical to s=9.

### Speed 1, 2, 3

No trend in size, zero or insignificant DSSIM drop, measurable performance gain up to 2x.

### Speed 4 comparing to 3

Usually size grow about 1%, very moderate DSSIM drop.

### Speed 5 comparing to 1

DSSIM is quite stable, almost to cases with drop more than 0.01.
Size difference from 2% to -0.5%. Also noticed significant inconsistency
in coding performance for different q settings. For example,
giving s=5, the performance better 2.36 times for compression with q=44,
than for q=10. For s=1, the same ratio is 3.4x.

Speed 5 is recommended for offline compression. All levels below that don't make sense.


### Speed 7 vs 6

This and next levels have problems with picture quality: missing parts
on high q on artworks, pixilation in gradients on photos. As a result,
can be even more compact.

### Speed 8 vs 7

Has significant drop in quality and compression level. Not recommended.

### Speed 9 vs 8

Dramatically larger file size for artworks even with worse DSSIM.
Not recommended at all.
