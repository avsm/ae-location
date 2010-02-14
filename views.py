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

class Gift(db.Model):
  name = db.StringProperty(required=True)
  giver = db.UserProperty()
  recipient = db.StringProperty(required=True)

  description = db.TextProperty()
  url = db.URLProperty()
  created = db.DateTimeProperty(auto_now_add=True)
  modified = db.DateTimeProperty(auto_now=True)

class GiftForm(djangoforms.ModelForm):
  class Meta:
    model = Gift
    exclude = ['giver', 'created', 'modified']

def respond(request, user, template, params=None):
  """Helper to render a response, passing standard stuff to the response.

  Args:
    request: The request object.
    user: The User object representing the current user; or None if nobody
      is logged in.
    template: The template name; '.html' is appended automatically.
    params: A dict giving the template parameters; modified in-place.

  Returns:
    Whatever render_to_response(template, params) returns.

  Raises:
    Whatever render_to_response(template, params) raises.
  """
  if params is None:
    params = {}
  if user:
    params['user'] = user
    params['sign_out'] = users.CreateLogoutURL('/')
    params['is_admin'] = (users.IsCurrentUserAdmin() and
                          'Dev' in os.getenv('SERVER_SOFTWARE'))
  else:
    params['sign_in'] = users.CreateLoginURL(request.path)
  if not template.endswith('.html'):
    template += '.html'
  return shortcuts.render_to_response(template, params)


def index(request):
  """Request / -- show all gifts."""
  user = users.GetCurrentUser()
  gifts = db.GqlQuery('SELECT * FROM Gift ORDER BY created DESC')
  return respond(request, user, 'list', {'gifts': gifts})

def edit(request, gift_id):
  """Create or edit a gift.  GET shows a blank form, POST processes it."""
  user = users.GetCurrentUser()
  if user is None:
    return http.HttpResponseForbidden('You must be signed in to add or edit a gift')

  gift = None
  if gift_id:
    gift = Gift.get(db.Key.from_path(Gift.kind(), int(gift_id)))
    if gift is None:
      return http.HttpResponseNotFound('No gift exists with that key (%r)' %
                                       gift_id)

  form = GiftForm(data=request.POST or None, instance=gift)

  if not request.POST:
    return respond(request, user, 'gift', {'form': form, 'gift': gift})

  errors = form.errors
  if not errors:
    try:
      gift = form.save(commit=False)
    except ValueError, err:
      errors['__all__'] = unicode(err)
  if errors:
    return respond(request, user, 'gift', {'form': form, 'gift': gift})

  if not gift.giver:
    gift.giver = user
  gift.put()

  return http.HttpResponseRedirect('/')

def new(request):
  """Create a gift.  GET shows a blank form, POST processes it."""
  return edit(request, None)
