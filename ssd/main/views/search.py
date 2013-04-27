#
# Copyright 2012 - Tom Alessi
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


"""Views for the SSD Project that pertain to search functionality only

"""


import datetime
import pytz
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import timezone as jtz
from ssd.main.models import Report
from ssd.main.models import Service_Issue
from ssd.main.forms import SearchForm


def search(request):
    """Incident Search View

    Allow a user to search through officially created incidents using specific search
    criteria

    """

    # If this is a POST, then check the input params and perform the
    # action, otherwise print the index page
    if request.method == 'POST':
        # Check the form elements
        form = SearchForm(request.POST)

        if form.is_valid():
            # Obtain the cleaned data (only validate the dates)
            s_date = form.cleaned_data['s_date']
            s_time = form.cleaned_data['s_time']
            e_date = form.cleaned_data['e_date']
            e_time = form.cleaned_data['e_time']
            text = form.cleaned_data['text']
            status = form.cleaned_data['status']

            # Give the dates a timezone so search is accurate
            # If the timezone is not set, give the local server timezone
            if request.COOKIES.get('timezone') == None:
                set_timezone = settings.TIME_ZONE
            else:
                set_timezone = request.COOKIES.get('timezone')

            # Combine the dates and times into datetime objects
            start = datetime.datetime.combine(s_date, s_time)
            end = datetime.datetime.combine(e_date, e_time)

            # Set the timezone
            tz = pytz.timezone(set_timezone)
            start = tz.localize(start)
            end = tz.localize(end)

            if status == 'open':
                status = True
            elif status == 'closed':
                status = False

            # Search without regard for open/closed status
            if status == '':
                results = Service_Issue.objects.filter(incident__date__range=[start,end],
                                                       incident__detail__contains=text
                                                      ).values('incident__date',
                                                               'incident_id',
                                                               'incident__closed',
                                                               'incident__detail'
                                                              ).distinct().order_by('-incident__date')
            # Search for open/closed incidents
            else:
                results = Service_Issue.objects.filter(incident__closed__isnull=status,
                                                       incident__date__range=[start,end],
                                                       incident__detail__contains=text
                                                      ).values('incident__date',
                                                               'incident_id',
                                                               'incident__closed',
                                                               'incident__detail'
                                                              ).distinct().order_by('-incident__date')

            # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
            jtz.activate(set_timezone)

            # Print the page
            return render_to_response(
               'search/search_results.html',
               {
                  'title':'SSD Search Results',
                  'results':results,
                  'form':form
               },
               context_instance=RequestContext(request)
            )

    # Ok, its a GET
    else:
        # Create a blank form
        form = SearchForm()

    # Print the page
    # On a POST, the form will give back error values for printing in the template
    return render_to_response(
       'search/search.html',
       {
          'title':'SSD Incident Search',
          'form':form
       },
       context_instance=RequestContext(request)
    )


def rsearch(request):
    """Incident Report Search View

    Allow a user to search through user reported incidents using specific search
    criteria

    """

    # If this is a POST, then check the input params and perform the
    # action, otherwise print the index page
    if request.method == 'POST':
        # Check the form elements
        form = SearchForm(request.POST)

        if form.is_valid():
            # Obtain the cleaned data (only validate the dates)
            s_date = form.cleaned_data['s_date']
            s_time = form.cleaned_data['s_time']
            e_date = form.cleaned_data['e_date']
            e_time = form.cleaned_data['e_time']
            text = form.cleaned_data['text']

            # Give the dates a timezone so search is accurate
            # If the timezone is not set, give the local server timezone
            if request.COOKIES.get('timezone') == None:
                set_timezone = settings.TIME_ZONE
            else:
                set_timezone = request.COOKIES.get('timezone')

            # Combine the dates and times into datetime objects
            start = datetime.datetime.combine(s_date, s_time)
            end = datetime.datetime.combine(e_date, e_time)

            # Set the timezone
            tz = pytz.timezone(set_timezone)
            start = tz.localize(start)
            end = tz.localize(end)

            results = Report.objects.filter(date__range=[start,end],
                                            description__contains=text).values('id',
									                                                             'date',
                                                                               'name',
                                                                               'email',
                                                                               'description',
                                                                               'additional',
                                                                               'screenshot1',
                                                                               'screenshot2'
                                                                              ).order_by('-id')

            # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
            jtz.activate(set_timezone)

            # Print the page
            return render_to_response(
               'search/rsearch_results.html',
               {
                  'title':'SSD Incident Report Results',
                  'results':results,
                  'form':form
               },
               context_instance=RequestContext(request)
            )

    # Ok, its a GET so create a blank form
    else:
        form = SearchForm()

    # Print the page
    # On a POST, the form will give back error values for printing in the template
    return render_to_response(
       'search/rsearch.html',
       {
          'title':'SSD Incident Report Search',
          'form':form
       },
       context_instance=RequestContext(request)
    )


def rsearch_recent(request):
    """Recent Incident Report Search View

    Allow a user to search through the most recent user reported incidents using specific search
    criteria

    """

    # Give the dates a timezone so search is accurate
    # If the timezone is not set, give the local server timezone
    if request.COOKIES.get('timezone') == None:
        set_timezone = settings.TIME_ZONE
    else:
        set_timezone = request.COOKIES.get('timezone')

    # Activate the timezone so the template can use it during rendering
    jtz.activate(set_timezone)

    results = Report.objects.values('id',
                                    'date',
                                    'name',
                                    'email',
                                    'description',
                                    'additional',
                                    'screenshot1',
                                    'screenshot2'
                                   ).order_by('-id')[:5]

    return render_to_response(
       'search/rsearch_results.html',
       {
          'title':'SSD Incident Report Results',
          'results':results
       },
       context_instance=RequestContext(request)
    )
