#!/bin/sh
$1/bin/python navplot.py $2/today_south.pdf
$1/bin/python navplot.py --north $2/today_north.pdf
