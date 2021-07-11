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

from pymongo import MongoClient

from navplot import get_notams, make_briefing

# Map origin and scaling
SOUTH = (50.2, -5.0, 6.5)
NORTH = (53.0, -6.0, 6.0)

TODAY_HOURS = list(range(6, 18))
TOMORROW_HOURS = [16, 17, 18]

def update_db(name, now, next, data):
    client = MongoClient(
        "mongodb+srv://navplot@cluster0.ywtwj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
        password="pRX5jOrjas0H7UBD")

    db = client['notam']
    collection = db['notams']

    collection.update_one(
        {'name': name},
        {'$set': {'name': name, 'current': now, 'next': next, 'pdf': data}},
        upsert=True)

def get_next(now, hours):
    if now.hour == hours[-1]:
        offset = 24 + hours[0] - hours[-1]
    else:
        offset = 1

    return now + datetime.timedelta(hours=offset)

now = datetime.datetime.utcnow().replace(microsecond=0)

if now.hour in set(TODAY_HOURS + TOMORROW_HOURS):
    notam_soup = get_notams()

    # Today's NOTAMs
    if now.hour in TODAY_HOURS:
        next = get_next(now, TODAY_HOURS)
        date = now.date()

        buf = io.BytesIO()
        make_briefing(buf, notam_soup, date, SOUTH)
        update_db("today-south", now, next, buf.getvalue())

        buf = io.BytesIO()
        make_briefing(buf, notam_soup, date, NORTH)
        update_db("today-north", now, next, buf.getvalue())

    # Tomorrow's NOTAMs
    if now.hour in TOMORROW_HOURS:
        next = get_next(now, TOMORROW_HOURS)
        date = now.date() + datetime.timedelta(hour=1)

        buf = io.BytesIO()
        make_briefing(buf, notam_soup, date, SOUTH)
        update_db("tomorrow-south", now, next, buf.getvalue())

        buf = io.BytesIO()
        make_briefing(buf, notam_soup, date, NORTH)
        update_db("tomorrow-north", now, next, buf.getvalue())
