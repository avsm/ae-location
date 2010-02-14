# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from google.appengine.api import users

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django import http
from django import shortcuts

import json
import fmi

class Location(db.Model):
  loc = db.GeoPtProperty(required=True)
  date = db.DateTimeProperty(required=True)
  accuracy = db.FloatProperty()
  url = db.URLProperty()

  created = db.DateTimeProperty(auto_now_add=True)
  modified = db.DateTimeProperty(auto_now=True)

def fmi_cron(request):
  resp = fmi.poll()
  if resp:
      loc = db.GeoPt(resp['lat'], resp['long'])
      l = Location(loc=loc, date=resp['date'], accuracy=resp['accuracy'], url='http://me.com')
      l.put()
      return http.HttpResponse("ok", mimetype="text/plain")
  else:
      return http.HttpResponseServerError("error", mimetype="text/plain")