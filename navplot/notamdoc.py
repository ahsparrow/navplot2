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

import math
import datetime

import pkg_resources
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import darkgray, gray, blue, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, XPreformatted, Paragraph
from reportlab.platypus import PageBreak, KeepTogether

# For plotting on the map
GLIDING_SITES = {
    'ABO': (57.0753, -2.8429),
    'GRL': (52.1863, -0.1112),
    'HUS': (52.4407, -1.0470),
    'LAS': (51.1893, -1.0317),
    'MYN': (52.5187, -2.8810),
    'NHL': (50.8510, -3.2785),
    'NYM': (51.7152, -2.2814),
    'PAR': (50.9229, -0.4739),
    'POR': (56.1888, -3.3219),
    'SUT': (54.2288, -1.2097),
    'TIB': (52.4575,  1.1616)}

# Page margins
LEFT_MARGIN = 15 * mm
RIGHT_MARGIN = 15 * mm
TOP_MARGIN = 15 * mm
BOTTOM_MARGIN = 10 * mm

# XPreformatted with added hyperlink
class LinkedXPreformatted(XPreformatted):
    def __init__(self, link, *args, **kwargs):
        self.link = str(link)
        super().__init__(*args, **kwargs)

    def drawOn(self, canvas, x, y, _sW=0):
        super().drawOn(canvas, x, y, _sW)
        top = y + self.height + (5 * mm)
        canvas.bookmarkPage(self.link, fit="XYZ", left=x, top=top)

#------------------------------------------------------------------------------
# Reportlab Platypus template

class DocTemplate(SimpleDocTemplate):
    def __init__(self, filename, dateStr, notams, mapinfo, mapdata, **kw):
        SimpleDocTemplate.__init__(self, filename, **kw)
        self.lat0 = mapinfo[0]
        self.lon0 = mapinfo[1]
        self.notams = notams
        self.dateStr = dateStr
        self.bottomOffset = 5*mm
        self.map_data = mapdata

        self.mapwidth = self.pagesize[0]-self.rightMargin-self.leftMargin
        self.mapheight = self.pagesize[1]-self.bottomMargin-self.topMargin-\
            self.bottomOffset-20*mm
        self.scale =\
            self.mapwidth/(mapinfo[2]*math.cos(math.radians(self.lat0)))

    # Convert lat/lon coordinates to page coordinates
    def latlon2xy(self, lat, lon):
        x = self.leftMargin+\
            (lon-self.lon0)*self.scale*math.cos(math.radians(lat))
        y = self.bottomMargin+self.bottomOffset+(lat-self.lat0)*self.scale
        # Reducing precision reduces output file size
        return int(x*10)/10, int(y*10)/10

#------------------------------------------------------------------------------
# Draw front page (and map)

def drawFirstPage(canvas, doc):
    canvas.saveState()

    # Title text
    tobj = canvas.beginText()
    tobj.setTextOrigin(doc.leftMargin, doc.pagesize[1]-doc.topMargin-24)
    tobj.setFont('Helvetica-Bold', 32)
    tobj.setLeading(22)
    tobj.textLine('NavPlot')
    tobj.setFont('Helvetica', 16)
    tobj.textLine('Navigation warnings for: %s' % doc.dateStr)
    canvas.drawText(tobj)

    # Small print
    canvas.setFont('Helvetica', 10)
    canvas.drawString(doc.leftMargin, doc.bottomMargin,
                      "THIS IS AN UNOFFICAL BRIEFING. Use at your own risk.")
    #canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, doc.bottomMargin,
    #                       "Data \N{COPYRIGHT SIGN} NATS Ltd.")

    # Clipping rectangle for the map
    path = canvas.beginPath()
    path.rect(doc.leftMargin, doc.bottomMargin+doc.bottomOffset, doc.mapwidth,
              doc.mapheight)
    canvas.clipPath(path)

    # Drawing style for the map
    canvas.setLineWidth(0.5)
    canvas.setFillColor(gray)

    # Draw the other map stuff. Coordinate file must be in mapinfo format.
    # Coast line from http://rimmer.ngdc.noaa.gov/mgg/coast/getcoast.html
    moveFlag = True
    path = canvas.beginPath()

    map_data = doc.map_data
    for lin in map_data.splitlines():
        try:
            lon, lat = map(float, lin.split())
        except:
            moveFlag = True
            continue

        x, y = doc.latlon2xy(lat, lon)
        if moveFlag:
            path.moveTo(x, y)
            moveFlag = False
        else:
            path.lineTo(x, y)

    canvas.setStrokeColor(darkgray)
    canvas.drawPath(path)

    # Draw some gliding sites
    canvas.setStrokeColor(gray)
    delta = 2.5*mm
    for gs in GLIDING_SITES:
        x, y = doc.latlon2xy(*GLIDING_SITES[gs])
        canvas.lines(((x, y+delta, x, y-delta), (x-delta, y, x+delta, y)))
        canvas.drawString(x+mm, y+mm, gs)

    # Draw NOTAM areas
    canvas.setStrokeColor(blue)
    canvas.setFillColor(black)
    canvas.setLineWidth(0.5)
    for n, notam in enumerate(doc.notams):
        x, y = doc.latlon2xy(notam[0], notam[1])
        radius = notam[2]/60.0*doc.scale
        canvas.circle(x, y, radius)
        if radius/mm < 3:
            x1 = x + radius/1.41 + mm/2
            y1 = y + radius/1.41 + mm/2
            canvas.line(x, y, x1, y1)
            canvas.drawString(x1, y1, str(n+1))
        else:
            canvas.drawCentredString(x, y-3, str(n+1))

        # Add hyperlink
        canvas.linkAbsolute("", str(n),
                (x - (4 * mm), y - (4 * mm), x + (4 * mm), y + (4 * mm)),
                Border='[0 0 0]')

    canvas.restoreState()

#------------------------------------------------------------------------------
# Produce NOTAM document
def format_doc(filename, local_notams, area_notams, boring_notams,
               local_coords, header, date, mapinfo, mapdata):

    date_str = date.strftime('%a, %d %b %y')

    # Define Platypus template and paragraph styles
    doc = DocTemplate(filename, date_str, local_coords, mapinfo,
                      mapdata,
                      leftMargin=LEFT_MARGIN,
                      rightMargin=RIGHT_MARGIN,
                      bottomMargin=BOTTOM_MARGIN,
                      topMargin=TOP_MARGIN,
                      title='NOTAM', author='Freeflight')

    subStyle = ParagraphStyle('Sub',
                              fontName='Helvetica-Oblique', fontSize=16,
                              spaceBefore=2*mm, spaceAfter=5*mm)

    notamStyle = ParagraphStyle('Notam',
                                fontName='Helvetica', fontSize=9,
                                bulletFontName='Helvetica-Bold',
                                bulletFontSize=10,
                                leftIndent=8*mm, spaceAfter=3*mm)

    otherStyle = ParagraphStyle('Other',
                                fontName='Helvetica', fontSize=9,
                                bulletFontName='Symbol',
                                bulletFontSize=10,
                                leftIndent=8*mm, spaceAfter=3*mm)

    # Generate the NOTAM document.
    story=[]
    story.append(PageBreak())

    story.append(Paragraph('<b>NOTAM Header</b>', subStyle))
    h = '\n'.join([hl for hl in header.splitlines() if hl])
    story.append(XPreformatted(h, otherStyle))
    story.append(Paragraph('<b>Plotted Navigation Warnings</b>', subStyle))
    story.append(Paragraph(
        'Plotted Navigation Warnings are Restrictions of all types '\
        'and Warnings of type: <i>Air Display</i>, <i>Aerobatics</i>, '\
        '<i>Glider Flying</i>, <i>Missile, Gun or Rocket Firing</i>, '\
        '<i>Parachute Dropping Area</i> and <i>Radioactive '\
        'Materials and Toxic Chemicals</i>. Also plotted are activation or '\
        'installation of Airspace types <i>CTZ</i>, <i>CTA</i>, <i>ATS '\
        'route</i>, <i>TMA</i> and <i>ATZ</i>', otherStyle))
    for n, notam in enumerate(local_notams):
        story.append(
            KeepTogether(LinkedXPreformatted(n, notam, notamStyle, bulletText=str(n+1))))

    if area_notams:
        paras = [XPreformatted(n, otherStyle, bulletText="\N{BULLET}")
                 for n in area_notams]

        head = '<b>Non-Plotted Navigation Warnings</b> (Radius > 30nm)'
        story.append(KeepTogether([Paragraph(head, subStyle), paras[0]]))
        for p in paras[1:]:
            story.append(KeepTogether(p))

    if boring_notams:
        paras = [XPreformatted(n, otherStyle, bulletText="\N{BULLET}")
                 for n in boring_notams]

        head = '<b>All Other Navigation Warnings</b> (Sorted South to North)'
        story.append(KeepTogether([Paragraph(head, subStyle), paras[0]]))
        for p in paras[1:]:
            story.append(KeepTogether(p))

    doc.build(story, onFirstPage=drawFirstPage)

#------------------------------------------------------------------------------
def notamdoc(filename, notams, header, date, mapinfo, mapdata):
    # Sort by latitude of area centre
    notams.sort(key=lambda x: int(x['qline']['centre'][:4]))

    # NOTAMS are split into three categories - localNotams have an
    # "interesting" subject with a radius <=30nm. These are the ones that are
    # plotted on the map.
    # areaNotams are also "interesting" but have radius >30nm.
    # boringNotams have an "uninteresting" subject (e.g. kite flying)
    interesting_notams = []
    area_notams = []
    boring_notams = []
    interesting_coords = []
    for n in notams:
        # NOTAM description text
        notam_text = "FROM: %s" % n['from'].strftime("%y/%m/%d %H:%M")
        to = "PERM" if 'to' not in n else n['to'].strftime("%y/%m/%d %H:%M")
        notam_text += " TO: %s\n" % to

        notam_text += n['text']
        if 'lower' in n:
            notam_text += "\nLOWER: %s" % n['lower']

        if 'upper' in n:
            notam_text += "\nUPPER: %s" % n['upper']

        if 'schedule' in n:
            notam_text += "\nSCHEDULE: %s" % n['schedule']

        # Sort into interesting, area & boring categories
        qc = n['qline']['qcode']
        if ((qc[1]=='R') or
            (qc[1]=='W' and qc[2] in 'ABGMPR') or
            (qc[1]=='A' and qc[2] in 'CERTZ' and qc[3:5] in ['CA', 'CS'])):

            if int(n['qline']['radius']) > 30:
                area_notams.append(notam_text)
            else:
                interesting_notams.append(notam_text)

                # Coordinates for map
                ctext = n['qline']['centre']
                lat = int(ctext[:2]) + int(ctext[2:4])/60.0
                lon = int(ctext[5:8]) + int(ctext[8:10])/60.0
                if ctext[10] == 'W':
                    lon = -lon
                rad = int(n['qline']['radius'])
                interesting_coords.append((lat, lon, rad))
        elif qc[1]=='W':
            boring_notams.append(notam_text)

    format_doc(filename, interesting_notams, area_notams, boring_notams,
               interesting_coords, header, date, mapinfo, mapdata)
