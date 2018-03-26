#!/bin/sh
$1/bin/python navplot.py -d1 -uahsparrow -p$2 $3/tomorrow_south.pdf
$1/bin/python navplot.py -d1 -uahsparrow -p$2 --north --london --scottish $3/tomorrow_north.pdf
