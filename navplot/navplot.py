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

from datetime import datetime

from bs4 import BeautifulSoup
import requests
from pkg_resources import resource_filename

from . import notamdoc

NOTAM_URL = "http://pibs.nats.co.uk/operational/pibs/PIB.xml"

#-----------------------------------------------------------------------
# Parse NOTAM soup and return dictionary of notams
def parse_notams(soup):
    notams = {}
    for notam in soup:
        data = {}

        # NOTAM id
        id = "/".join([getattr(notam, a).string
            for a in ["NOF", "Series", "Number", "Year", "Type"]])

        data['qline'] = {
            'qcode': "Q" + notam.QLine.Code23.string + notam.QLine.Code45.string,
            'centre': notam.Coordinates.string,
            'radius': notam.Radius.string
        }

        # Start and end dates
        data['from'] = datetime.strptime(
                notam.StartValidity.string, "%y%m%d%H%M")

        if notam.EndValidity.string != "PERM":
            data['to'] = datetime.strptime(
                    notam.EndValidity.string, "%y%m%d%H%M")

        # Lower and upper limits
        lower = notam.find("ItemF")
        if lower:
            data['lower'] = lower.string
        upper = notam.find("ItemG")
        if upper:
            data['upper'] = upper.string

        schedule = notam.find("ItemD")
        if schedule:
            data['schedule'] = schedule

        # NOTAM text
        data['text'] = notam.ItemE.string

        notams[id] = data

    return notams

#-----------------------------------------------------------------------
# Extract NOTAMS
def extract_notams(soup):
    # Use a dictionary to exclude any duplicate NOTAMs
    notam_dict = {}

    firsections = soup.find_all("FIRSection")
    for firsection in firsections:
        # NAV warnings
        notams = firsection.Warnings.NotamList.find_all("Notam")
        notam_dict.update(parse_notams(notams))

        # En-route
        notams = firsection.find('En-route').NotamList.find_all('Notam')
        notam_dict.update(parse_notams(notams))

    return list(notam_dict.values())

#-----------------------------------------------------------------------
# Filter by date
def date_filter(notam, date):
    if date < notam['from'].date():
        return False
    elif 'to' not in notam:
        return True
    else:
        return date <= notam['to'].date()

#-----------------------------------------------------------------------
# Get XML data from contingency bulletin website
def get_notams():
    r = requests.get(NOTAM_URL)

    soup = BeautifulSoup(r.text, features="lxml-xml")
    return soup

#-----------------------------------------------------------------------
# Create NOTAM briefing
def make_briefing(filename, soup, date, map_extent):
    hdr = "UK AIS - CONTINGENCY BULLETIN\n"
    hdr += "Data source: " + NOTAM_URL + "\n"
    hdr += "Issued: " + soup.AreaPIBHeader.Issued.string

    notams = extract_notams(soup)

    # Filter by date
    notams = [n for n in notams if date_filter(n, date)]

    # Get map data
    with open(resource_filename(__name__, "data/map.dat")) as f:
        mapdata = f.read()

    # Create PDF document
    notamdoc.notamdoc(filename, notams, hdr, date, map_extent, mapdata)

#-----------------------------------------------------------------------
# Get NOTAMS from NATS website & make PDF document
def navplot(filename, date, map_extent):
    notam_soup = get_notams()
    make_briefing(filename, notam_soup, date, map_extent)
