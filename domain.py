from functools import partial

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.cache import caches

import requests

from .models import UserProgramme, ProgrammeMasterCourse

course_and_group_memberships_cache_key = 'course_and_group_memberships'


def get_user_enrolled_scheduled_courses_by_programme(user, role='student'):
    # two queries and one http request
    user_programmes = get_user_programmes(user)
    programme_master_courses = get_programme_master_courses(user_programmes.values_list('programme__id', flat=True))
    user_enrolled_scheduled_courses = get_user_enrolled_scheduled_courses(user.username, role)

    # list of programmes
    programmes = [{
        'id': up.programme.id,
        'display_name': up.programme.display_name,
        'courses': list(filter(
            partial(_filter_master_courses, programme_id=up.programme.id, master_course_ids=programme_master_courses),
            user_enrolled_scheduled_courses.get('courses', [])
        )),
    } for up in user_programmes]

    # completion data
    completions = user_enrolled_scheduled_courses.get('module_completions', {})
    if role == 'tutor':
        completions['students'] = _set_user_ids(completions.get('students', []))

    return programmes, completions


def get_user_programmes(user):
    """
    one query to get the user programmes for a given user
    """
    return UserProgramme\
        .objects\
        .select_related('programme')\
        .select_related('user')\
        .filter(user__id=user.id)\
        .order_by('programme__display_name')


def get_programme_master_courses(programme_ids):
    """
    one query to get the programme master courses for given programme ids
    """
    return ProgrammeMasterCourse\
        .objects\
        .select_related('programme')\
        .select_related('master_course')\
        .filter(programme__id__in=programme_ids)


def get_user_enrolled_scheduled_courses(username, role):
    """
    one http request to get all the enrolled courses for a given username
    """
    response = requests.get(
        '{}'.format(settings.ENROLMENTS_URL),
        params={
            'username': username,
            'role': role,
        }
    )
    return response.json() if response.status_code == 200 else {}


def get_scheduled_course_and_group_memberships_from_cache():
    cache = caches['default']
    if cache.get(course_and_group_memberships_cache_key) is None:
        response = requests.get(
            '{}{}'.format(settings.VLEROOT, settings.MEMBERSHIPS_URL)
        )
        if response.status_code == 200:
            cache.set(
                course_and_group_memberships_cache_key,
                response.json(),
                settings.COURSE_AND_GROUP_MEMBERSHIPS_CACHE_TIMEOUT
                if hasattr(settings, 'COURSE_AND_GROUP_MEMBERSHIPS_CACHE_TIMEOUT')
                else 21600
            )
    data = cache.get(course_and_group_memberships_cache_key)
    return {} if data is None else data


def _filter_master_courses(user_enrolled_scheduled_course, programme_id, master_course_ids):
    vle_course_ids = list(map(
        lambda pmc: pmc.master_course.vle_course_id,
        filter(
            lambda pmc: pmc.programme.id == programme_id,
            master_course_ids
        ),
    ))
    return user_enrolled_scheduled_course['masteridnumber'] in vle_course_ids


def _set_user_ids(users):
    ids = get_user_model().objects. \
        filter(username__in=[u['username'] for u in users]). \
        values_list('username', 'id')
    ids = {u[0]: u[1] for u in ids}

    for u in users:
        u['id'] = ids.get(u['username'], None)

    return users
