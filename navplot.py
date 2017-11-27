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

# User and password for AIS self-briefing
USER = ''
PASSWORD = ''

# Map origin and scaling
SOUTH = (50.2, -4.5, 6.0)
NORTH = (53.0, -6.0, 6.0)

def navplot_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_filename")
    parser.add_argument("--user", "-u", default=USER,
                        help="NATS AIS user name")
    parser.add_argument("--password", "-p", default=PASSWORD,
                        help="NATS AIS password")
    parser.add_argument("--delta", "-d", type=int, default=0,
                        help="Days offset from today (default today)")
    parser.add_argument("--num_days", "-n", type=int, default=1,
                        help="Number of days (default 1)")
    parser.add_argument("--london", dest='firs',
                        action='append_const', const="EGTT",
                        help="Plot NOTAMs from London FIR (default)")
    parser.add_argument("--scottish", dest='firs',
                        action='append_const', const="EGPX",
                        help="Plot NOTAMs from Scottish FIR")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--south", action="store_true",
                       help="Plot South of country (default)")
    group.add_argument("--north", action="store_true",
                       help="Plot North of country")

    args = parser.parse_args()

    # Get list of FIRs
    firs = args.firs or ["EGTT"]

    # Use with UTC times/dates
    start_date = datetime.datetime.utcnow().date() +\
                 datetime.timedelta(args.delta)

    mapscale = NORTH if args.north else SOUTH

    navplot(args.pdf_filename, firs, start_date, args.num_days,
            args.user, args.password, mapscale)

if __name__ == "__main__":
    navplot_cli()
