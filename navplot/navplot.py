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


from . import notamdoc

import datetime
import json
import re
import warnings

import mechanicalsoup
import bs4
from pkg_resources import resource_filename

warnings.filterwarnings(action="ignore", category=bs4.XMLParsedAsHTMLWarning)

LOGIN_URL = "https://nats-uk.ead-it.com/fwf-nats/mobile/public/login.faces"
AREA_BRIEF_URL = "https://nats-uk.ead-it.com/fwf-nats/mobile/restricted/pib/mobile-briefing-new-area.faces"

# Regex for the Q-line
QGroupRe = re.compile(
    r"^Q\)"
    r"(?P<fir>[A-Z]+)/"
    r"(?P<qcode>Q[A-Z]+)/"
    r"(?P<traffic>[IV]+)/"
    r"(?P<purpose>[NBOM]+)/"
    r"(?P<scope>[AEW]+)/"
    r"(?P<lower>\d+)/"
    r"(?P<upper>\d+)/"
    r"(?P<centre>\d{4}[NS]\d{5}[EW])(?P<radius>\d{3})[ ]*"
)

FROM_RE = re.compile(r"\bB\)(\d{10})\b")
TO_RE = re.compile(r"\bC\)(\d{10}|PERM)\b")
SCHEDULE_RE = re.compile(r"^D\)(.+)$")
DESCRIPTION_RE = re.compile(r"^E\)(.+)", re.MULTILINE)
LEVELS_RE = re.compile(r"F\)(.+?) G\)(.+)")


# -----------------------------------------------------------------------
# Extract NOTAM data from the HTML soup
def parse_soup(soup):
    notam_dict = {}
    for notam in soup.findAll("table", class_="notamTable"):
        id = notam.parent.parent.td.string

        # Get Q-Line
        qline = notam.find(text=QGroupRe)
        n_dict = {"qline": QGroupRe.match(qline.string).groupdict()}

        # Get "From" time
        from_element = notam.find(text=FROM_RE)
        from_str = FROM_RE.search(from_element.string).group(1)
        n_dict["from"] = datetime.datetime.strptime(from_str, "%y%m%d%H%M")

        # Get "To" time
        to_element = notam.find(text=TO_RE)
        to_str = TO_RE.search(to_element.string).group(1)
        if to_str != "PERM":
            n_dict["to"] = datetime.datetime.strptime(to_str, "%y%m%d%H%M")

        # Get schedule
        schedule_element = notam.find(text=SCHEDULE_RE)
        if schedule_element:
            n_dict["schedule"] = SCHEDULE_RE.match(schedule_element.string).group(1)

        # Get levels
        levels_element = notam.find(text=LEVELS_RE)
        if levels_element:
            levels = LEVELS_RE.match(levels_element.string)
            n_dict["lower"] = levels.group(1)
            n_dict["upper"] = levels.group(2)

        # Get description text
        description_element = notam.find(text=DESCRIPTION_RE)
        n_dict["text"] = description_element.string[2:]

        notam_dict[id] = n_dict

    return list(notam_dict.values())


# -----------------------------------------------------------------------
# Get NOTAM data from NATS briefing website
def get_notams(username, password, date_from, date_to):
    browser = mechanicalsoup.StatefulBrowser()

    # Log in
    browser.open(LOGIN_URL)
    browser.select_form()
    browser["login:mainForm:j_username_input"] = username
    browser["login:mainForm:j_password"] = password
    browser.submit_selected()

    # Area briefing page
    browser.open(AREA_BRIEF_URL)

    # Add EGTT
    browser.select_form('form[id="mainPage:mainForm"]')
    browser["mainPage:mainForm:fir:fir:fir_input_input"] = "EGTT"
    browser.submit_selected("mainPage:mainForm:fir:fir:fir_uibsm-ad1")

    # Add EGPX
    browser.select_form('form[id="mainPage:mainForm"]')
    browser["mainPage:mainForm:fir:fir:fir_input_input"] = "EGPX"
    browser.submit_selected("mainPage:mainForm:fir:fir:fir_uibsm-ad1")

    # Set start/end times
    browser.select_form('form[id="mainPage:mainForm"]')
    browser["mainPage:mainForm:startDateSelected:startDateSelected_date_input"] = (
        f"{date_from:%Y-%m-%d}"
    )
    browser["mainPage:mainForm:startDateSelected:startDateSelected_time_input"] = (
        "00:00"
    )
    browser["mainPage:mainForm:endDateSelected:endDateSelected_date_input"] = (
        f"{date_to:%Y-%m-%d}"
    )
    browser["mainPage:mainForm:endDateSelected:endDateSelected_time_input"] = "23:59"
    response = browser.submit_selected("mainPage:mainForm:pibgenerate")

    notams = parse_soup(response.soup)

    # Get header text
    hdr = response.soup.find("div", class_="uibs-pib-result-header").get_text()

    return notams, hdr


# -----------------------------------------------------------------------
# Filter by date
def date_filter(notam, date):
    if date < notam["from"].date():
        return False
    elif "to" not in notam:
        return True
    else:
        return date <= notam["to"].date()


# -----------------------------------------------------------------------
# Create NOTAM briefing
def make_briefing(filename, notams, hdr, date, map_extent, debug=False):
    # filter by date
    notams = [n for n in notams if date_filter(n, date)]

    # Get map data
    with open(resource_filename(__name__, "data/yaixm.geojson")) as f:
        airspace_json = json.load(f)

    with open(resource_filename(__name__, "data/coast.geojson")) as f:
        coast_json = json.load(f)

    # Create PDF document
    notamdoc.notamdoc(
        filename, notams, hdr, date, map_extent, airspace_json, coast_json, debug
    )


# -----------------------------------------------------------------------
# Get NOTAMS from NATS website and make PDF document
def navplot(username, password, filename, date, map_extent, debug=False):
    notams, hdr = get_notams(username, password, date, date)
    make_briefing(filename, notams, hdr, date, map_extent, debug)
