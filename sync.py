from datetime import datetime

from django.conf import settings
from django.utils.translation import gettext as _

import requests

from .models import MasterCourse, ScheduledCourse, ScheduledCourseGroup


def full_sync():
    # request all courses requiring synchronization from Moodle
    response = requests.get(
        ''.join([settings.VLEROOT, settings.SYNC_URL])
    )

    # return error message
    if response.status_code != 200:
        e = response.json()
        return e['errorMessage']

    _sync_all_courses(response.json())
    return _('Full course synchronization completed successfully')


def _sync_all_courses(courses):
    # orphaned ids to delete
    to_delete = list(MasterCourse.objects.all().values_list('vle_course_id', flat=True))

    # create or update each item
    for item in courses:
        obj, created = MasterCourse.objects.get_or_create(vle_course_id=item['vle_course_id'])
        obj.display_name = item['fullname']
        obj.compulsory = bool(item['compulsory'])
        obj.credits = item['credits']
        obj.commitment = item['commitment'] or ''
        obj.weeks_duration = item['weeks_duration']
        obj.save()
        if item['vle_course_id'] in to_delete:
            to_delete.remove(item['vle_course_id'])
        _sync_scheduled_courses(obj, item['scheduled'])

    # delete orphans
    if to_delete:
        MasterCourse.objects.filter(vle_course_id__in=to_delete).delete()


def _sync_scheduled_courses(master, scheduled):
    # orphaned ids to delete
    to_delete = list(ScheduledCourse.objects.filter(master_course=master).values_list('vle_course_id', flat=True))

    # create or update each item
    for item in scheduled:
        ScheduledCourse.objects.filter(vle_course_id=item['vle_course_id']).exclude(master_course=master).delete()
        obj, created = master.scheduledcourse_set.get_or_create(vle_course_id=item['vle_course_id'])
        obj.display_name = item['fullname']
        obj.open_date = get_datetime_or_none(item['opendate'], '%Y-%m-%d')
        obj.start_date = get_datetime_or_none(item['startdate'], '%Y-%m-%d')
        obj.end_date = get_datetime_or_none(item['enddate'], '%Y-%m-%d')
        obj.close_date = get_datetime_or_none(item['closedate'], '%Y-%m-%d')
        obj.save()
        if item['vle_course_id'] in to_delete:
            to_delete.remove(item['vle_course_id'])
        if 'groups' in item:
            _sync_scheduled_course_groups(obj, item['groups'])

    # delete orphans
    if to_delete:
        ScheduledCourse.objects.filter(master_course=master, vle_course_id__in=to_delete).delete()


def _sync_scheduled_course_groups(scheduled_course, groups):
    # orphaned ids to delete
    to_delete = list(ScheduledCourseGroup.objects.filter(scheduled_course=scheduled_course).values_list('vle_group_id', flat=True))

    # create or update each item
    for item in groups:
        obj, created = scheduled_course.scheduledcoursegroup_set.get_or_create(vle_group_id=item['vle_group_id'])
        obj.display_name = item['name']
        obj.save()
        if item['vle_group_id'] in to_delete:
            to_delete.remove(item['vle_group_id'])

    # delete orphans
    if to_delete:
        ScheduledCourseGroup.objects.filter(scheduled_course=scheduled_course, vle_group_id__in=to_delete).delete()


def get_datetime_or_none(date, fmt):
    try:
        date = datetime.strptime(date, fmt)
    except (TypeError, ValueError):
        date = None
    return date
