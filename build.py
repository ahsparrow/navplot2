# Copyright 2026 Alan Sparrow
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
import os

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
    parser.add_argument(
        "--archive", help="Number of old NOTAMS to archive", type=int, default=0
    )
    args = parser.parse_args()

    today = datetime.datetime.now(datetime.UTC).date()
    tomorrow = today + datetime.timedelta(days=1)

    notams, hdr = get_notams(args.user, args.password, today, tomorrow)

    # Today's NOTAMs
    make_briefing(
        os.path.join(args.directory, "today_south.pdf"),
        notams,
        hdr,
        today,
        SOUTH_EXTENTS,
    )

    make_briefing(
        os.path.join(args.directory, "today_north.pdf"),
        notams,
        hdr,
        today,
        NORTH_EXTENTS,
    )

    # Tomorrow's NOTAMs
    make_briefing(
        os.path.join(args.directory, "tomorrow_south.pdf"),
        notams,
        hdr,
        tomorrow,
        SOUTH_EXTENTS,
    )

    make_briefing(
        os.path.join(args.directory, "tomorrow_north.pdf"),
        notams,
        hdr,
        tomorrow,
        NORTH_EXTENTS,
    )
