import json

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.utils.translation import gettext as _
from django.utils.encoding import force_str
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import MasterCourse, ScheduledCourse, ScheduledCourseGroup
from .sync import full_sync, get_datetime_or_none


@staff_member_required
def full_sync_view(request):
    messages.add_message(request, messages.INFO, full_sync())
    return HttpResponseRedirect(reverse('admin:app_list', args=('programmes',)))


@csrf_exempt  # has to be the first decorator, apparently, or it doesn't work
@require_http_methods(['POST'])
def create_master_course(request):
    """
    create a new master course
    """

    # get the data from the request
    data = json.loads(force_str(request.body))
    vle_course_id = data.get('vle_course_id', '')
    name = data.get('name', '')

    # make sure both fields were given
    if not vle_course_id or not name:
        return _error400(_('Must specify vle_course_id and name'))

    # check MasterCourse doesn't already exist
    if MasterCourse.objects.filter(vle_course_id=vle_course_id).exists():
        return _error400(_('Course with given vle_course_id already exists'))

    # create MasterCourse
    MasterCourse.objects.create(
        vle_course_id=vle_course_id,
        display_name=name,
        compulsory=data.get('compulsory', False),
        credits=data.get('credits', None),
        commitment=data.get('commitment', ''),
        weeks_duration=data.get('weeks_duration', None)
    )

    # return JSON response
    return _success200(_('Course created successfully!'))


@csrf_exempt
@require_http_methods(['POST'])
def update_master_course(request):
    """
    update a MasterCourse (matching its vle_course_id)
    its vle_course_id or name may change, hence old_vle_course_id is needed to identify it
    """

    # get the required data from the request
    data = json.loads(force_str(request.body))
    old_vle_course_id = data.get('old_vle_course_id', '')
    vle_course_id = data.get('vle_course_id', '')
    name = data.get('name', '')

    # make sure all fields were given
    if not old_vle_course_id or not vle_course_id or not name:
        return _error400(_('Must specify old_vle_course_id, vle_course_id, name'))

    # check MasterCourse given by old_vle_course_id actually exists
    if not MasterCourse.objects.filter(vle_course_id=old_vle_course_id).exists():
        return _error400(_('Course with given old_vle_course_id does not exist'))

    # update course
    course = MasterCourse.objects.get(vle_course_id=old_vle_course_id)
    course.vle_course_id = vle_course_id
    course.display_name = name
    course.compulsory = data.get('compulsory', False)
    course.credits = data.get('credits', None)
    course.commitment = data.get('commitment', '')
    course.weeks_duration = data.get('weeks_duration', None)
    course.save()

    # return JSON response
    return _success200(_('Course updated successfully!'))


@csrf_exempt
@require_http_methods(['POST'])
def delete_master_course(request):
    """
    delete an existing MasterCourse (matching its vle_course_id)
    """

    # get the data from the request
    data = json.loads(force_str(request.body))
    vle_course_id = data.get('vle_course_id', '')

    # make sure vle_course_id was given
    if not vle_course_id:
        return _error400(_('Must specify vle_course_id'))

    # check MasterCourse given by vle_course_id actually exists
    if not MasterCourse.objects.filter(vle_course_id=vle_course_id).exists():
        return _error400(_('Course with given vle_course_id does not exist'))

    # delete course
    ScheduledCourse.objects.filter(master_course__vle_course_id=vle_course_id).delete()
    MasterCourse.objects.get(vle_course_id=vle_course_id).delete()

    # return JSON response
    return _success200(_('Course deleted successfully!'))


@csrf_exempt
@require_http_methods(['POST'])
def create_scheduled_course(request):
    """
    create a new scheduled course
    """

    # get the required data from the request
    data = json.loads(force_str(request.body))
    master_vle_course_id = data.get('master_vle_course_id', '')
    vle_course_id = data.get('vle_course_id', '')
    name = data.get('name', '')

    # make sure all fields were given
    if not all([master_vle_course_id, vle_course_id, name]):
        return _error400(_('Must specify master_vle_course_id, vle_course_id and name'))

    # check ScheduledCourse doesn't already exist
    if ScheduledCourse.objects.filter(vle_course_id=vle_course_id).exists():
        return _error400(_('Course with given vle_course_id already exists'))

    # get MasterCourse, catching does not exist exception
    try:
        master = MasterCourse.objects.get(vle_course_id=master_vle_course_id)
    except MasterCourse.DoesNotExist:
        return _error400(_('Course with given master_vle_course_id does not exist'))

    # get the dates from the request
    open_date = data.get('opendate', None)
    start_date = data.get('startdate', None)
    end_date = data.get('enddate', None)
    close_date = data.get('closedate', None)

    # create ScheduledCourse
    ScheduledCourse.objects.create(
        vle_course_id=vle_course_id,
        display_name=name,
        master_course=master,
        open_date=get_datetime_or_none(open_date, '%Y-%m-%d'),
        start_date=get_datetime_or_none(start_date, '%Y-%m-%d'),
        end_date=get_datetime_or_none(end_date, '%Y-%m-%d'),
        close_date=get_datetime_or_none(close_date, '%Y-%m-%d'),
    )

    # return JSON response
    return _success200(_('Course created successfully!'))


@csrf_exempt
@require_http_methods(['POST'])
def update_scheduled_course(request):
    """
    update a ScheduledCourse (matching its vle_course_id and the master course's vle_course_id)
    its vle_course_id or name may change, hence old_vle_course_id is needed to identify it
    """

    # get the data from the request
    data = json.loads(force_str(request.body))
    master_vle_course_id = data.get('master_vle_course_id', '')
    old_vle_course_id = data.get('old_vle_course_id', '')
    vle_course_id = data.get('vle_course_id', '')
    name = data.get('name', '')

    # make sure all fields were given
    if not all([master_vle_course_id, old_vle_course_id, vle_course_id, name]):
        return _error400(_('Must specify master_vle_course_id, old_vle_course_id, vle_course_id and name'))

    # check ScheduledCourse given by old_vle_course_id and master_vle_course_id actually exists
    if not ScheduledCourse.objects.filter(
            vle_course_id=old_vle_course_id, master_course__vle_course_id=master_vle_course_id).exists():
        return _error400(_('Course with given old_vle_course_id and master_vle_course_id does not exist'))

    # get the dates from the request
    open_date = data.get('opendate', None)
    start_date = data.get('startdate', None)
    end_date = data.get('enddate', None)
    close_date = data.get('closedate', None)

    # update course
    course = ScheduledCourse.objects.get(vle_course_id=old_vle_course_id)
    course.vle_course_id = vle_course_id
    course.display_name = name
    course.open_date = get_datetime_or_none(open_date, '%Y-%m-%d')
    course.start_date = get_datetime_or_none(start_date, '%Y-%m-%d')
    course.end_date = get_datetime_or_none(end_date, '%Y-%m-%d')
    course.close_date = get_datetime_or_none(close_date, '%Y-%m-%d')
    course.save()

    # return JSON response
    return _success200(_('Course updated successfully!'))


@csrf_exempt
@require_http_methods(['POST'])
def delete_scheduled_course(request):
    """
    delete an existing ScheduledCourse (matching its vle_course_id)
    """

    # get the data from the request
    data = json.loads(force_str(request.body))
    master_vle_course_id = data.get('master_vle_course_id', '')
    vle_course_id = data.get('vle_course_id', '')

    # make sure vle_course_id and master_vle_course_id were given
    if not vle_course_id or not master_vle_course_id:
        return _error400(_('Must specify master_vle_course_id and vle_course_id'))

    # check ScheduledCourse given by old_vle_course_id and master_vle_course_id actually exists
    if not ScheduledCourse.objects.filter(
            vle_course_id=vle_course_id, master_course__vle_course_id=master_vle_course_id).exists():
        return _error400(_('Course with given old_vle_course_id and master_vle_course_id does not exist'))

    # delete course
    ScheduledCourse.objects.get(vle_course_id=vle_course_id).delete()

    # return JSON response
    return _success200(_('Course deleted successfully!'))


@csrf_exempt
@require_http_methods(['POST'])
def create_group(request):
    # get the data from the request
    data = json.loads(force_str(request.body))
    vle_course_id = data.get('vle_course_id', '')
    vle_group_id = data.get('vle_group_id', '')
    name = data.get('name', '')

    # make sure all fields were given
    if not vle_course_id or not vle_group_id or not name:
        return _error400(_('Must specify vle_course_id, vle_group_id, name'))

    # check ScheduledCourse exists
    try:
        scheduled_course = ScheduledCourse.objects.get(vle_course_id=vle_course_id)
    except ScheduledCourse.DoesNotExist:
        return _error400(_('Course with given vle_course_id does not exist'))

    # check ScheduledCourseGroup doesn't already exist
    if ScheduledCourseGroup.objects.filter(scheduled_course=scheduled_course, vle_group_id=vle_group_id).exists():
        return _error400(_('Group with given vle_course_id and vle_group_id already exists'))

    # create ScheduledCourseGroup
    ScheduledCourseGroup.objects.create(scheduled_course=scheduled_course, vle_group_id=vle_group_id, display_name=name)

    # return JSON response
    return _success200(_('Group created successfully!'))


@csrf_exempt
@require_http_methods(['POST'])
def update_group(request):
    # get the data from the request
    data = json.loads(force_str(request.body))
    vle_course_id = data.get('vle_course_id', '')
    old_vle_group_id = data.get('old_vle_group_id', '')
    vle_group_id = data.get('vle_group_id', '')
    name = data.get('name', '')

    # make sure all fields were given
    if not vle_course_id or not old_vle_group_id or not vle_group_id or not name:
        return _error400(_('Must specify vle_course_id, old_vle_group_id, vle_group_id, name'))

    # check ScheduledCourse exists
    try:
        scheduled_course = ScheduledCourse.objects.get(vle_course_id=vle_course_id)
    except ScheduledCourse.DoesNotExist:
        return _error400(_('Course with given vle_course_id does not exist'))

    # check ScheduledCourseGroup given by vle_course_id and old_vle_group_id actually exists
    if not ScheduledCourseGroup.objects.filter(scheduled_course=scheduled_course, vle_group_id=old_vle_group_id).exists():
        return _error400(_('Group with given vle_course_id and old_vle_group_id does not exist'))

    # update group
    group = ScheduledCourseGroup.objects.get(scheduled_course=scheduled_course, vle_group_id=old_vle_group_id)
    group.vle_group_id = vle_group_id
    group.display_name = name
    group.save()

    # return JSON response
    return _success200(_('Group updated successfully!'))


@csrf_exempt
@require_http_methods(['POST'])
def delete_group(request):
    # get the data from the request
    data = json.loads(force_str(request.body))
    vle_course_id = data.get('vle_course_id', '')
    vle_group_id = data.get('vle_group_id', '')

    # make sure vle_course_id and vle_group_id were given
    if not vle_course_id or not vle_group_id:
        return _error400(_('Must specify vle_course_id and vle_group_id'))

    # check ScheduledCourse exists
    try:
        scheduled_course = ScheduledCourse.objects.get(vle_course_id=vle_course_id)
    except ScheduledCourse.DoesNotExist:
        return _error400(_('Course with given vle_course_id does not exist'))

    # check ScheduledCourseGroup given by vle_course_id and vle_group_id actually exists
    if not ScheduledCourseGroup.objects.filter(scheduled_course=scheduled_course, vle_group_id=vle_group_id).exists():
        return _error400(_('Group with given vle_course_id and vle_group_id does not exist'))

    # delete group
    ScheduledCourseGroup.objects.filter(scheduled_course=scheduled_course, vle_group_id=vle_group_id).delete()

    # return JSON response
    return _success200(_('Group deleted successfully!'))


def _error400(msg):
    """
    return an http 400 with a given message
    """
    return HttpResponse(json.dumps({
        'errorMessage': msg
    }), content_type='application/json', status=400)


def _success200(msg):
    """
    return an http 200 with a given message
    """
    return HttpResponse(json.dumps({
        'successMessage': msg
    }), content_type='application/json', status=200)

