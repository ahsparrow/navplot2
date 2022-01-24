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

import dropbox

from navplot import get_notams, make_briefing

# Map origin and scaling
SOUTH_EXTENTS = (50.2, -5.0, 6.5)
NORTH_EXTENTS = (53.0, -6.0, 6.0)

HOURS = list(range(6, 18))

def upload_dropbox(name, now, data):
    app_key = os.environ['DROPBOX_APP_KEY']
    app_secret = os.environ['DROPBOX_APP_SECRET']
    refresh_token = os.environ['DROPBOX_REFRESH_TOKEN']

    dbx = dropbox.Dropbox(
            app_key=app_key,
            app_secret=app_secret,
            oauth2_refresh_token=refresh_token)

    dbx.files_upload(
            data, "/" + name + ".pdf", dropbox.files.WriteMode.overwrite)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", "-f", action="store_true")
    args = parser.parse_args()

    now = datetime.datetime.utcnow().replace(microsecond=0)

    if now.hour in HOURS or args.force:
        notam_soup = get_notams()
        date = now.date()

        # Today's NOTAMs
        buf = io.BytesIO()
        make_briefing(buf, notam_soup, date, SOUTH_EXTENTS)
        upload_dropbox("today_south", now, buf.getvalue())

        buf = io.BytesIO()
        make_briefing(buf, notam_soup, date, NORTH_EXTENTS)
        upload_dropbox("today_north", now, buf.getvalue())

        # Tomorrow's NOTAMs
        date += datetime.timedelta(days=1)

        buf = io.BytesIO()
        make_briefing(buf, notam_soup, date, SOUTH_EXTENTS)
        upload_dropbox("tomorrow_south", now, buf.getvalue())

        buf = io.BytesIO()
        make_briefing(buf, notam_soup, date, NORTH_EXTENTS)
        upload_dropbox("tomorrow_north", now, buf.getvalue())
