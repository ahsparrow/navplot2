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

import datetime
import io
import os

import dropbox

from navplot import get_notams, make_briefing

# Map origin and scaling
SOUTH = (50.2, -5.0, 6.5)
NORTH = (53.0, -6.0, 6.0)

TODAY_HOURS = list(range(6, 18))
TOMORROW_HOURS = [16, 17, 18]

def upload_dropbox(name, now, data):
    refresh_token = os.environ['DROPBOX_REFRESH_TOKEN']
    app_key = os.environ['DROPBOX_APP_KEY']
    app_secret = os.environ['DROPBOX_APP_SECRET']

    dbx = dropbox.Dropbox(
            app_key=app_key,
            app_secret=app_secret,
            oauth2_refresh_token=refresh_token)

    dbx.files_upload(
            data, "/" + name + ".pdf", dropbox.files.WriteMode.overwrite)

now = datetime.datetime.utcnow().replace(microsecond=0)

if now.hour in set(TODAY_HOURS + TOMORROW_HOURS):
    notam_soup = get_notams()

    # Today's NOTAMs
    if now.hour in TODAY_HOURS:
        date = now.date()

        buf = io.BytesIO()
        make_briefing(buf, notam_soup, date, SOUTH)
        upload_dropbox("today_south", now, buf.getvalue())

        buf = io.BytesIO()
        make_briefing(buf, notam_soup, date, NORTH)
        upload_dropbox("today_north", now, buf.getvalue())

    # Tomorrow's NOTAMs
    if now.hour in TOMORROW_HOURS:
        date = now.date() + datetime.timedelta(days=1)

        buf = io.BytesIO()
        make_briefing(buf, notam_soup, date, SOUTH)
        upload_dropbox("tomorrow_south", now, buf.getvalue())

        buf = io.BytesIO()
        make_briefing(buf, notam_soup, date, NORTH)
        upload_dropbox("tomorrow_north", now, buf.getvalue())
