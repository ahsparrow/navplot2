# Copyright 2023 Alan Sparrow
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
# along with Navplot.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import datetime
import io
import os
import sys

from dotenv import load_dotenv

from navplot import get_notams, make_briefing

# Map origin and scaling
SOUTH_EXTENTS = (50.2, -5.0, 6.5)
NORTH_EXTENTS = (53.0, -6.0, 6.0)


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="output directory")
    parser.add_argument(
        "--user", "-u", help="NATS AIP username", default=os.environ.get("NATS_USER")
    )
    parser.add_argument(
        "--password",
        "-p",
        help="NATS AIP password",
        default=os.environ.get("NATS_PASSWORD"),
    )
    args = parser.parse_args()

    today = datetime.datetime.utcnow().date()
    tomorrow = today + datetime.timedelta(days=1)

    notams, hdr = get_notams(args.user, args.password, today, tomorrow)

    # Temporary file name (make file updates atomic)
    tmpfile = os.path.join(args.directory, "tmp.pdf")

    # Today's NOTAMs
    buf = io.BytesIO()
    make_briefing(buf, notams, hdr, today, SOUTH_EXTENTS)
    with open(tmpfile, "wb") as f:
        f.write(buf.getbuffer())
    os.rename(tmpfile, os.path.join(args.directory, "today_south.pdf"))

    buf = io.BytesIO()
    make_briefing(buf, notams, hdr, today, NORTH_EXTENTS)
    with open(tmpfile, "wb") as f:
        f.write(buf.getbuffer())
    os.rename(tmpfile, os.path.join(args.directory, "today_north.pdf"))

    # Tomorrow's NOTAMs
    buf = io.BytesIO()
    make_briefing(buf, notams, hdr, tomorrow, SOUTH_EXTENTS)
    with open(tmpfile, "wb") as f:
        f.write(buf.getbuffer())
    os.rename(tmpfile, os.path.join(args.directory, "tomorrow_south.pdf"))

    buf = io.BytesIO()
    make_briefing(buf, notams, hdr, tomorrow, NORTH_EXTENTS)
    with open(tmpfile, "wb") as f:
        f.write(buf.getbuffer())
    os.rename(tmpfile, os.path.join(args.directory, "tomorrow_north.pdf"))
