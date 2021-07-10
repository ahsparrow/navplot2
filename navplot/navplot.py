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
import re

from bs4 import BeautifulSoup
import requests
from pkg_resources import resource_filename

from . import notamdoc

# Regex for the Q-line
QGroupRe = re.compile(
    r'(?P<fir>[A-Z]+)/'
    r'(?P<qcode>Q[A-Z]+)/'
    r'(?P<traffic>[IV]+)/'
    r'(?P<purpose>[NBOM]+)/'
    r'(?P<scope>[AEW]+)/'
    r'(?P<lower>\d+)/'
    r'(?P<upper>\d+)/'
    r'(?P<centre>\d{4}[NS]\d{5}[EW])(?P<radius>\d{3})')

ToRe = re.compile(r"^TO:\s*$")
FromRe = re.compile(r"^FROM:\s*$")
LowerRe = re.compile(r"^LOWER:\s*$")
UpperRe = re.compile(r"^UPPER:\s*$")
ScheduleRe = re.compile(r"^SCHEDULE:\s*$")

#-----------------------------------------------------------------------
# Extract NOTAM data from the HTML soup
def parse_notam_soup(soup):
    # Find all the Q-codes
    notam_dict = {}
    for notam in soup.findAll(class_="notam"):
        try:
            data = {}

            qline = notam.find(string=QGroupRe)
            data['qline'] = QGroupRe.match(qline).groupdict()

            data['text'] = notam.find("pre").text.strip()

            frm = str(notam.find("b", string=FromRe).next_sibling).strip()
            data['from'] = datetime.strptime(frm, "%d %b %Y %H:%M")

            to = str(notam.find("b", string=ToRe).next_sibling).strip()
            if to != "PERM":
                data['to'] = datetime.strptime(
                        to.removesuffix("EST").strip(), "%d %b %Y %H:%M")

            lower = notam.find("b", string=LowerRe)
            if lower:
                data['lower'] = str(lower.next_sibling).strip()

            upper = notam.find("b", string=UpperRe)
            if upper:
                data['upper'] = str(upper.next_sibling).strip()

            schedule = notam.find("b", string=ScheduleRe)
            if schedule:
                data['schedule'] = str(schedule.next_sibling).strip()

            id = notam.find(class_="notamid").text.strip()
            notam_dict[id] = data
        except Exception as e:
            print(e, notam.text)

    return notam_dict

#-----------------------------------------------------------------------
# Get NOTAMS from NATS website & make PDF document
def navplot(filename, date, mapinfo):
    # Navigation warning contingency breif
    r = requests.get("http://pibs.nats.co.uk/operational/pibs/pib3.shtml")
    soup = BeautifulSoup(r.text, features="lxml")

    notam_dict = parse_notam_soup(soup)
    notams = list(notam_dict.values())

    # Get header text
    hdr = "UK AIS - CONTINGENCY BULLETIN\n"

    validity = soup.find(id="body")\
            .find(class_="header").find(string="VALIDITY (UTC):").parent
    hdr += "".join(validity.text.splitlines())

    # Filter by date
    notams = [n for n in notams if date_filter(n, date)]

    # Get map data
    with open(resource_filename(__name__, "data/map.dat")) as f:
        mapdata = f.read()

    # Create PDF document
    notamdoc.notamdoc(notams, hdr, date, filename, mapinfo, mapdata)

#-----------------------------------------------------------------------
# Filter by date
def date_filter(notam, date):
    if date < notam['from'].date():
        return False
    elif 'to' not in notam:
        return True
    else:
        return date <= notam['to'].date()
