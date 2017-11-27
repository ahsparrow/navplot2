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
import re

import mechanicalsoup
from pkg_resources import resource_filename

from . import notamdoc

LOGIN_URL = "http://www.nats-uk.ead-it.com/fwf-natsuk/public/user/account/login.faces"
AREA_BRIEF_URL = "http://www.nats-uk.ead-it.com/fwf-natsuk/restricted/user/ino/brief_area.faces"
COPYRIGHT_HOLDER = 'NATS Ltd'

# Regex for the Q-line
QGroupRe = re.compile(r'^Q\) '
    r'(?P<fir>[A-Z]+)/'
    r'(?P<qcode>Q[A-Z]+)/'
    r'(?P<traffic>[IV]+)/'
    r'(?P<purpose>[NBOM]+)/'
    r'(?P<scope>[AEW]+)/'
    r'(?P<lower>\d+)/'
    r'(?P<upper>\d+)/'
    r'(?P<centre>\d{4}[NS]\d{5}[EW])(?P<radius>\d{3})[ ]*')

#-----------------------------------------------------------------------
# Extract NOTAM data from the HTML soup
def parse_notam_soup(soup):
    # Find all the Q-codes
    notam_dict = {}
    for q in soup.findAll(text=QGroupRe):
        # Q code is in tr->td->div
        notam_row = q.parent.parent.parent

        # Get NOTAM id from adjancent cell to the NOTAM
        id = notam_row.find('td', {"class": "right"}).string

        # Get Q-line
        n_dict = QGroupRe.match(q.string).groupdict()
        notam = q.parent.parent

        # Get NOTAM text remove Q-line and blank lines
        notam_text = notam.get_text()
        clean_text = "\n".join([n for n in notam_text.splitlines()
                                if n.strip() and not n.startswith("Q)")])
        n_dict["text"] = clean_text

        notam_dict[id] = n_dict

    return list(notam_dict.values())

#-----------------------------------------------------------------------
# Get NOTAMS from NATS website & make PDF document
def navplot(filename, firs, start_date, num_days, username, password,
             mapinfo):
    # Calculate dates
    if start_date == datetime.date.today():
        utc = datetime.datetime.utcnow()
        start_hour = utc.hour
        start_min = utc.minute
    else:
        start_hour = 0
        start_min = 0
    end_date = start_date + datetime.timedelta(days=num_days-1)

    browser = mechanicalsoup.StatefulBrowser()

    # Log in
    browser.open(LOGIN_URL)
    browser.select_form()
    browser['j_username'] = username
    browser['j_password'] = password
    browser.submit_selected()

    # Area Briefing page
    browser.open(AREA_BRIEF_URL)

    browser.select_form("#mainForm")
    browser["mainForm:startValidityDay"] = str(start_date.day)
    browser["mainForm:startValidityMonth"] = str(start_date.month-1)
    browser["mainForm:startValidityYear"] = str(start_date.year)
    browser["mainForm:startValidityHour"] = str(start_hour)
    browser["mainForm:startValidityMinute"] = str(start_min)
    browser["mainForm:endValidityDay"] = str(end_date.day)
    browser["mainForm:endValidityMonth"] = str(end_date.month-1)
    browser["mainForm:endValidityYear"] = str(end_date.year)
    browser["mainForm:endValidityHour"] = "23"
    browser["mainForm:endValidityMinute"] = "59"
    browser["mainForm:traffic"] = "V"
    browser["mainForm:lowerFL"] = "000"
    browser["mainForm:upperFL"] = "100"
    for i, fir in enumerate(firs):
        browser["mainForm:fir_%d" % i] = fir
    response = browser.submit_selected("mainForm:generate")

    notams = parse_notam_soup(response.soup)

    # Get the header text (discarding non-ASCII characters)
    hdr = response.soup.find("div", {"id": "mainColContent"}).get_text()
    hdr_text = "\n".join([h.strip() for h in hdr.splitlines() if h.strip()])

    # Create PDF document
    with open(resource_filename(__name__, "data/map.dat")) as f:
        mapdata = f.read()

    notamdoc.notamdoc(notams, hdr_text, firs, start_date, num_days, filename,
                      mapinfo, mapdata)
