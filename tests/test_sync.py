from django.core.exceptions import ObjectDoesNotExist

import pytest

from programmes.models import MasterCourse, ScheduledCourse, ScheduledCourseGroup
from programmes.sync import _sync_all_courses


@pytest.mark.django_db
def test_sync_all_courses_master_created():
    courses = [
        {
            'vle_course_id': '001',
            'fullname': 'How to make a lantern',
            'weeks_duration': 30,
            'compulsory': True,
            'commitment': '4 days per year',
            'credits': 20,
            'scheduled': [],
        },
    ]
    _sync_all_courses(courses)
    try:
        course = MasterCourse.objects.get(vle_course_id='001')
        assert course.display_name == courses[0]['fullname']
        assert course.weeks_duration == courses[0]['weeks_duration']
        assert course.compulsory == courses[0]['compulsory']
        assert course.commitment == courses[0]['commitment']
        assert course.credits == courses[0]['credits']
    except ObjectDoesNotExist:
        pytest.fail('Master course not created')


@pytest.mark.django_db
def test_sync_all_courses_master_created_none_types():
    courses = [
        {
            'vle_course_id': '001',
            'fullname': 'How to make a lantern',
            'weeks_duration': None,
            'compulsory': None,
            'commitment': None,
            'credits': None,
            'scheduled': [],
        },
    ]
    _sync_all_courses(courses)
    try:
        course = MasterCourse.objects.get(vle_course_id='001')
        assert course.display_name == courses[0]['fullname']
        assert course.weeks_duration == courses[0]['weeks_duration']
        assert course.compulsory is False
        assert course.commitment == ''
        assert course.credits == courses[0]['credits']
    except ObjectDoesNotExist:
        pytest.fail('Master course not created')


@pytest.mark.django_db
def test_sync_all_courses_master_updated():
    MasterCourse.objects.create(
        vle_course_id='001',
        display_name='How to make a lantern',
        weeks_duration=30,
        compulsory=False,
        credits=20,
        commitment='4 days per year'
    )
    courses = [
        {
            'vle_course_id': '001',
            'fullname': 'How to light a bonfire',
            'weeks_duration': 30,
            'compulsory': True,
            'credits': 20,
            'commitment': '4 days per year',
            'scheduled': [],
        },
    ]
    _sync_all_courses(courses)
    try:
        course = MasterCourse.objects.get(vle_course_id='001')
        assert course.display_name == courses[0]['fullname']
        assert course.weeks_duration == courses[0]['weeks_duration']
        assert course.compulsory == courses[0]['compulsory']
        assert course.commitment == courses[0]['commitment']
        assert course.credits == courses[0]['credits']
    except ObjectDoesNotExist:
        pytest.fail('Master course not created')


@pytest.mark.django_db
def test_sync_all_courses_master_removed():
    MasterCourse.objects.create(vle_course_id='001', display_name='How to make a lantern')
    MasterCourse.objects.create(vle_course_id='002', display_name='How to fix your broadband connection')
    courses = [
        {
            'vle_course_id': '001',
            'fullname': 'How to light a bonfire',
            'weeks_duration': 30,
            'compulsory': True,
            'credits': 20,
            'commitment': '4 days per year',
            'scheduled': [],
        },
    ]
    _sync_all_courses(courses)
    MasterCourse.objects.filter(vle_course_id='001', display_name='How to light a bonfire').count() == 1
    MasterCourse.objects.filter(vle_course_id='002').count() == 0


@pytest.mark.django_db
def test_sync_all_courses_scheduled_created():
    master = MasterCourse.objects.create(vle_course_id='001', display_name='How to make a lantern')
    courses = [
        {
            'vle_course_id': '001',
            'fullname': 'How to light a bonfire',
            'weeks_duration': 30,
            'compulsory': True,
            'credits': 20,
            'commitment': '4 days per year',
            'scheduled': [
                {
                    'vle_course_id': '001/01',
                    'fullname': 'How to gather wood',
                    'opendate': '2015-01-01',
                    'startdate': '2015-02-01',
                    'enddate': '2015-03-01',
                    'closedate': '2015-04-01',
                }
            ],
        },
    ]
    _sync_all_courses(courses)
    try:
        course = ScheduledCourse.objects.get(master_course=master, vle_course_id='001/01')
        course_dict = vars(course)
        assert course_dict['display_name'] == courses[0]['scheduled'][0]['fullname']
        assert str(course_dict['open_date']) == courses[0]['scheduled'][0]['opendate']
        assert str(course_dict['start_date']) == courses[0]['scheduled'][0]['startdate']
        assert str(course_dict['end_date']) == courses[0]['scheduled'][0]['enddate']
        assert str(course_dict['close_date']) == courses[0]['scheduled'][0]['closedate']
    except ObjectDoesNotExist:
        pytest.fail('Scheduled course not created')


@pytest.mark.django_db
def test_sync_all_courses_scheduled_created_none_types():
    master = MasterCourse.objects.create(vle_course_id='001', display_name='How to make a lantern')
    courses = [
        {
            'vle_course_id': '001',
            'fullname': 'How to light a bonfire',
            'weeks_duration': 30,
            'compulsory': True,
            'credits': 20,
            'commitment': '4 days per year',
            'scheduled': [
                {
                    'vle_course_id': '001/01',
                    'fullname': 'How to gather wood',
                    'opendate': None,
                    'startdate': None,
                    'enddate': None,
                    'closedate': None,
                }
            ],
        },
    ]
    _sync_all_courses(courses)
    try:
        course = ScheduledCourse.objects.get(master_course=master, vle_course_id='001/01')
        course_dict = vars(course)
        assert course_dict['display_name'] == courses[0]['scheduled'][0]['fullname']
        assert course_dict['open_date'] == courses[0]['scheduled'][0]['opendate']
        assert course_dict['start_date'] == courses[0]['scheduled'][0]['startdate']
        assert course_dict['end_date'] == courses[0]['scheduled'][0]['enddate']
        assert course_dict['close_date'] == courses[0]['scheduled'][0]['closedate']
    except ObjectDoesNotExist:
        pytest.fail('Scheduled course not created')


@pytest.mark.django_db
def test_sync_all_courses_scheduled_updated():
    master = MasterCourse.objects.create(vle_course_id='001', display_name='How to make a lantern')
    master.scheduledcourse_set.create(
        vle_course_id='001/01',
        display_name='How to gather wood',
        open_date='2015-01-01',
        start_date='2015-02-01',
        end_date='2015-03-01',
        close_date='2015-04-01'
    )
    courses = [
        {
            'vle_course_id': '001',
            'fullname': 'How to light a bonfire',
            'weeks_duration': 30,
            'compulsory': True,
            'credits': 20,
            'commitment': '4 days per year',
            'scheduled': [
                {
                    'vle_course_id': '001/01',
                    'fullname': 'How to light a firework',
                    'opendate': '2015-01-31',
                    'startdate': '2015-02-28',
                    'enddate': '2015-03-31',
                    'closedate': '2015-04-30',
                }
            ],
        },
    ]
    _sync_all_courses(courses)
    try:
        course = ScheduledCourse.objects.get(master_course=master, vle_course_id='001/01')
        course_dict = vars(course)
        assert course_dict['display_name'] == courses[0]['scheduled'][0]['fullname']
        assert str(course_dict['open_date']) == courses[0]['scheduled'][0]['opendate']
        assert str(course_dict['start_date']) == courses[0]['scheduled'][0]['startdate']
        assert str(course_dict['end_date']) == courses[0]['scheduled'][0]['enddate']
        assert str(course_dict['close_date']) == courses[0]['scheduled'][0]['closedate']
        assert ScheduledCourse.objects.all().count() == 1
    except ObjectDoesNotExist:
        pytest.fail('Scheduled course not created')


@pytest.mark.django_db
def test_sync_all_courses_scheduled_removed():
    master = MasterCourse.objects.create(vle_course_id='001', display_name='How to make a lantern')
    master.scheduledcourse_set.create(vle_course_id='001/01', display_name='How to gather wood')
    master.scheduledcourse_set.create(vle_course_id='001/02', display_name='How to light a firework')
    courses = [
        {
            'vle_course_id': '001',
            'fullname': 'How to light a bonfire',
            'weeks_duration': 30,
            'compulsory': True,
            'credits': 20,
            'commitment': '4 days per year',
            'scheduled': [
                {
                    'vle_course_id': '001/01',
                    'fullname': '',
                    'opendate': None,
                    'startdate': None,
                    'enddate': None,
                    'closedate': None,
                }
            ],
        },
    ]
    _sync_all_courses(courses)
    ScheduledCourse.objects.filter(master_course=master, vle_course_id='001/02').count() == 0
    ScheduledCourse.objects.filter(master_course=master, vle_course_id='001/01').count() == 1


@pytest.mark.django_db
def test_sync_all_courses_scheduled_group_created():
    master = MasterCourse.objects.create(vle_course_id='001', display_name='How to make a lantern')
    master.scheduledcourse_set.create(vle_course_id='001/01', display_name='How to gather wood')
    courses = [
        {
            'vle_course_id': '001',
            'fullname': 'How to light a bonfire',
            'weeks_duration': 30,
            'compulsory': True,
            'credits': 20,
            'commitment': '4 days per year',
            'scheduled': [
                {
                    'vle_course_id': '001/01',
                    'fullname': 'How to gather wood',
                    'opendate': '2015-01-01',
                    'startdate': '2015-02-01',
                    'enddate': '2015-03-01',
                    'closedate': '2015-04-01',
                    'groups': [
                        {
                            'vle_group_id': '001/01/A',
                            'name': 'Group A',
                        },
                        {
                            'vle_group_id': '001/01/B',
                            'name': 'Group B',
                        }
                    ]
                }
            ],
        },
    ]
    _sync_all_courses(courses)
    try:
        assert master.scheduledcourse_set.get(vle_course_id='001/01').scheduledcoursegroup_set.count() == len(courses[0]['scheduled'][0]['groups'])

        group = ScheduledCourseGroup.objects.get(vle_group_id='001/01/A')
        group_dict = vars(group)
        assert group_dict['display_name'] == courses[0]['scheduled'][0]['groups'][0]['name']

        group = ScheduledCourseGroup.objects.get(vle_group_id='001/01/B')
        group_dict = vars(group)
        assert group_dict['display_name'] == courses[0]['scheduled'][0]['groups'][1]['name']
    except ObjectDoesNotExist:
        pytest.fail('Scheduled course group not created')


@pytest.mark.django_db
def test_sync_all_courses_scheduled_group_updated():
    master = MasterCourse.objects.create(vle_course_id='001', display_name='How to make a lantern')
    master.scheduledcourse_set.create(vle_course_id='001/01', display_name='How to gather wood')
    master.scheduledcourse_set.get(vle_course_id='001/01').scheduledcoursegroup_set.create(vle_group_id='001/01/A', display_name='Group A (old)')
    courses = [
        {
            'vle_course_id': '001',
            'fullname': 'How to light a bonfire',
            'weeks_duration': 30,
            'compulsory': True,
            'credits': 20,
            'commitment': '4 days per year',
            'scheduled': [
                {
                    'vle_course_id': '001/01',
                    'fullname': 'How to light a firework',
                    'opendate': '2015-01-31',
                    'startdate': '2015-02-28',
                    'enddate': '2015-03-31',
                    'closedate': '2015-04-30',
                    'groups': [
                        {
                            'vle_group_id': '001/01/A',
                            'name': 'Group A (new)',
                        }
                    ]
                }
            ],
        },
    ]
    _sync_all_courses(courses)
    try:
        assert master.scheduledcourse_set.get(vle_course_id='001/01').scheduledcoursegroup_set.count() == len(courses[0]['scheduled'][0]['groups'])

        group = ScheduledCourseGroup.objects.get(vle_group_id='001/01/A')
        group_dict = vars(group)
        assert group_dict['display_name'] == courses[0]['scheduled'][0]['groups'][0]['name']
    except ObjectDoesNotExist:
        pytest.fail('Scheduled course group not created')


@pytest.mark.django_db
def test_sync_all_courses_scheduled_group_removed():
    master = MasterCourse.objects.create(vle_course_id='001', display_name='How to light a bonfire')
    master.scheduledcourse_set.create(vle_course_id='001/01', display_name='How to light a bonfire')
    master.scheduledcourse_set.create(vle_course_id='001/02', display_name='How to light a bonfire')
    master.scheduledcourse_set.get(vle_course_id='001/01').scheduledcoursegroup_set.create(vle_group_id='A', display_name='Group A')
    master.scheduledcourse_set.get(vle_course_id='001/01').scheduledcoursegroup_set.create(vle_group_id='B', display_name='Group B')
    master.scheduledcourse_set.get(vle_course_id='001/02').scheduledcoursegroup_set.create(vle_group_id='A', display_name='Group A')
    courses = [
        {
            'vle_course_id': '001',
            'fullname': 'How to light a bonfire',
            'weeks_duration': 30,
            'compulsory': True,
            'credits': 20,
            'commitment': '4 days per year',
            'scheduled': [
                {
                    'vle_course_id': '001/01',
                    'fullname': 'How to light a bonfire',
                    'opendate': '2015-01-31',
                    'startdate': '2015-02-28',
                    'enddate': '2015-03-31',
                    'closedate': '2015-04-30',
                    'groups': [
                        {
                            'vle_group_id': 'B',
                            'name': 'Group B',
                        }
                    ]
                },
                {
                    'vle_course_id': '001/02',
                    'fullname': 'How to light a bonfire',
                    'opendate': '2016-01-31',
                    'startdate': '2016-02-28',
                    'enddate': '2016-03-31',
                    'closedate': '2016-04-30',
                    'groups': [
                        {
                            'vle_group_id': 'A',
                            'name': 'Group A',
                        }
                    ]
                }
            ],
        },
    ]
    assert master.scheduledcourse_set.get(vle_course_id='001/01').scheduledcoursegroup_set.count() == 2
    assert master.scheduledcourse_set.get(vle_course_id='001/02').scheduledcoursegroup_set.count() == 1
    group_ids_before = list(ScheduledCourseGroup.objects.exclude(scheduled_course__vle_course_id='001/01', vle_group_id='A').values_list('id', flat=True))
    _sync_all_courses(courses)
    assert master.scheduledcourse_set.get(vle_course_id='001/01').scheduledcoursegroup_set.count() == 1
    assert master.scheduledcourse_set.get(vle_course_id='001/02').scheduledcoursegroup_set.count() == 1
    ScheduledCourseGroup.objects.filter(scheduled_course__vle_course_id='001/01', vle_group_id='A').count() == 0
    ScheduledCourseGroup.objects.filter(scheduled_course__vle_course_id='001/01', vle_group_id='B').count() == 1
    ScheduledCourseGroup.objects.filter(scheduled_course__vle_course_id='001/02', vle_group_id='A').count() == 1
    group_ids_after = list(ScheduledCourseGroup.objects.values_list('id', flat=True))
    assert group_ids_after == group_ids_before


@pytest.mark.django_db
def test_sync_master_vle_course_id_changed():
    master = MasterCourse.objects.create(vle_course_id='001', display_name='How to light a bonfire')
    master.scheduledcourse_set.create(vle_course_id='001/01', display_name='How to light a bonfire')
    courses = [
        {
            'vle_course_id': 'NEW_VLE_COURSE_ID',
            'fullname': 'How to light a bonfire',
            'weeks_duration': 30,
            'compulsory': True,
            'credits': 20,
            'commitment': '4 days per year',
            'scheduled': [
                {
                    'vle_course_id': '001/01',
                    'fullname': 'How to light a bonfire',
                    'opendate': '2015-01-31',
                    'startdate': '2015-02-28',
                    'enddate': '2015-03-31',
                    'closedate': '2015-04-30',
                },
            ],
        },
    ]
    _sync_all_courses(courses)
    master = MasterCourse.objects.get(vle_course_id='NEW_VLE_COURSE_ID')
    assert ScheduledCourse.objects.filter(master_course=master, vle_course_id='001/01').exists()
    assert not MasterCourse.objects.filter(vle_course_id='001').exists()
