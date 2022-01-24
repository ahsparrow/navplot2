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
import json
import io
import os

from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload

from navplot import get_notams, make_briefing

# Map origin and scaling
SOUTH_EXTENTS = (50.2, -5.0, 6.5)
NORTH_EXTENTS = (53.0, -6.0, 6.0)

HOURS = list(range(6, 18))

TODAY_SOUTH_ID = "1CChND79djTLhRd5yy3U0UOkyV_VGZmUH"
TODAY_NORTH_ID = "1Zipk8AjVATio21s_yk7OlZaFhuFQd1DK"
TOMORROW_SOUTH_ID = "1sv5SiHiSgFFCDboZnIjHn21WFhvzcdll"
TOMORROW_NORTH_ID = "1-RRiOlcY7z80tvsFQ3Sm1iE5T3-_Wpw-"

# Get Google drive API service
def get_service(api_name, api_version, scopes, account_info):
    credentials = service_account.Credentials.from_service_account_info(
            account_info)
    scoped_credentials = credentials.with_scopes(scopes)

    service = build(api_name, api_version, credentials=scoped_credentials)
    return service

# Upload data to file on Google drive
def upload_google(service, file_id, data):
    media = MediaIoBaseUpload(data, mimetype="application/pdf")
    service.files().update(fileId=file_id, media_body=media).execute()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", "-f", action="store_true")
    args = parser.parse_args()

    now = datetime.datetime.utcnow().replace(microsecond=0)

    if now.hour in HOURS or args.force:
        # Get NOTAM data
        notam_soup = get_notams()

        # Authenticate and construct service.
        account_info = json.loads(os.environ['SERVICE_ACCOUNT_KEY'])
        service = get_service(
            api_name='drive',
            api_version='v3',
            scopes=['https://www.googleapis.com/auth/drive'],
            account_info=account_info)

        # Today's NOTAMs
        date = now.date()

        buf = io.BytesIO()
        make_briefing(buf, notam_soup, date, SOUTH_EXTENTS)
        upload_google(service, TODAY_SOUTH_ID, buf)

        buf = io.BytesIO()
        make_briefing(buf, notam_soup, date, NORTH_EXTENTS)
        upload_google(service, TODAY_NORTH_ID, buf)

        # Tomorrow's NOTAMs
        date += datetime.timedelta(days=1)

        buf = io.BytesIO()
        make_briefing(buf, notam_soup, date, SOUTH_EXTENTS)
        upload_google(service, TOMORROW_SOUTH_ID, buf)

        buf = io.BytesIO()
        make_briefing(buf, notam_soup, date, NORTH_EXTENTS)
        upload_google(service, TOMORROW_NORTH_ID, buf)
