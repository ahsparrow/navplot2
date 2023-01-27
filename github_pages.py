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
import io
import os
import sys

from navplot import get_notams, make_briefing

# Map origin and scaling
SOUTH_EXTENTS = (50.2, -5.0, 6.5)
NORTH_EXTENTS = (53.0, -6.0, 6.0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="output directory")
    parser.add_argument("--user", "-u", help="NATS AIP username")
    parser.add_argument("--password", "-p", help="NATS AIP password")
    args = parser.parse_args()

    today = datetime.datetime.utcnow().date()
    tomorrow = today + datetime.timedelta(days=1)

    notams, hdr = get_notams(args.user, args.password, today, tomorrow)

    # Today's NOTAMs
    buf = io.BytesIO()
    make_briefing(buf, notams, hdr, today, SOUTH_EXTENTS)
    with open(os.path.join(args.directory, "today_south.pdf"), "wb") as f:
        f.write(buf.getbuffer())

    buf = io.BytesIO()
    make_briefing(buf, notams, hdr, today, NORTH_EXTENTS)
    with open(os.path.join(args.directory, "today_north.pdf"), "wb") as f:
        f.write(buf.getbuffer())

    # Tomorrow's NOTAMs
    buf = io.BytesIO()
    make_briefing(buf, notams, hdr, tomorrow, SOUTH_EXTENTS)
    with open(os.path.join(args.directory, "tomorrow_south.pdf"), "wb") as f:
        f.write(buf.getbuffer())

    buf = io.BytesIO()
    make_briefing(buf, notams, hdr, tomorrow, NORTH_EXTENTS)
    with open(os.path.join(args.directory, "tomorrow_north.pdf"), "wb") as f:
        f.write(buf.getbuffer())
