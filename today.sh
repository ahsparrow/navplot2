#!/bin/sh
$1/bin/python navplot.py -uahsparrow -p$2 $3/today_south.pdf
$1/bin/python navplot.py -uahsparrow -p$2 --north --london --scottish $3/today_north.pdf
