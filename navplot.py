#!/usr/bin/env python3
# Copyright 2017 Alan Sparrow
#
# This file is part of Navplot
#
# Navplot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Navplot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with YAIXM.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import datetime

from navplot import navplot

# Map origin and scaling
SOUTH = (50.2, -5.0, 6.5)
NORTH = (53.0, -6.0, 6.0)

def navplot_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_filename")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--today", action="store_true",
                       help="Today's NOTAMs (default)")
    group.add_argument("--tomorrow", action="store_true",
                       help="Tomorrow's NOTAMs")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--south", action="store_true",
                       help="Plot South of country (default)")
    group.add_argument("--north", action="store_true",
                       help="Plot North of country")

    args = parser.parse_args()

    # Use with UTC times/dates
    date = datetime.datetime.utcnow().date()
    if args.tomorrow:
        date += datetime.timedelta(1)

    mapscale = NORTH if args.north else SOUTH

    navplot(args.pdf_filename, date, mapscale)

if __name__ == "__main__":
    navplot_cli()
