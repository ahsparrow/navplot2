#!/bin/sh
$1/bin/python navplot.py --tomorrow $2/tomorrow_south.pdf
$1/bin/python navplot.py --tomorrow --north $2/tomorrow_north.pdf
