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

from email.message import EmailMessage
from os import environ
from smtplib import SMTP_SSL
from subprocess import run, PIPE, STDOUT

from dotenv import load_dotenv

result = run("systemctl status navplot.service".split(), stdout=PIPE, stderr=STDOUT)
txt = result.stdout.decode("ascii", "ignore")

msg = EmailMessage()
msg.set_content(txt)
msg["From"] = "alan@freeflight.org.uk"
msg["To"] = "alan@freeflight.org.uk"
msg["Subject"] = "Navplot Fail"

load_dotenv()

server = SMTP_SSL("smtppro.zoho.com")
server.login(environ["ZOHO_USER"], environ["ZOHO_PASSWORD"])
server.send_message(msg)
