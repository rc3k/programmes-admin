from django.conf import settings

import pytest
from mock import patch

from programmes.models import MasterCourse
from programmes.domain import get_user_programmes, get_programme_master_courses
from programmes.domain import get_user_enrolled_scheduled_courses_by_programme

from .fixtures import *

slug = 'some-module-overview-page'


@pytest.fixture
def master_course():
    vle_course_id = 'foobar'
    return MasterCourse.objects.create(
        display_name='Foobar',
        vle_course_id=vle_course_id
    )


@pytest.fixture
def module_overview_page():
    home = create_page(
        'Home',
        'public_new/home.html',
        'en',
        published=True
    )
    home.save()
    page = create_page(
        'Some module overview page',
        'public_new/module_outline_page.html',
        'en',
        slug=slug,
        published=True
    )
    page.save()
    return page


@pytest.mark.django_db
def test_get_user_programmes_for_two_programmes_student_user(two_programmes_student_user, one_programme_student_user, programmes):
    user_programmes = get_user_programmes(two_programmes_student_user)
    cats = user_programmes.get(programme__display_name=programmes[0].display_name)
    gmba = user_programmes.get(programme__display_name=programmes[1].display_name)
    assert len(user_programmes) == 2
    assert cats.programme == programmes[0]
    assert gmba.programme == programmes[1]


@pytest.mark.django_db
def test_get_user_programmes_for_one_programme_student_user(two_programmes_student_user, one_programme_student_user, programmes):
    user_programmes = get_user_programmes(one_programme_student_user)
    cats = user_programmes.get(programme__display_name=programmes[0].display_name)
    assert len(user_programmes) == 1
    assert cats.programme == programmes[0]


@pytest.mark.django_db
def test_get_user_programmes_for_no_programmes_student_user(no_programmes_student_user, programmes):
    user_programmes = get_user_programmes(no_programmes_student_user)
    assert len(user_programmes) == 0


@pytest.mark.django_db
def test_get_programme_master_courses_for_cats(programmes):
    gmba_programme = programmes[0]
    assert gmba_programme.display_name == 'CATS'
    programme_master_courses = get_programme_master_courses([gmba_programme.id])
    assert len(programme_master_courses) == 0


@pytest.mark.django_db
def test_get_programme_master_courses_for_gmba(programmes):
    gmba_programme = programmes[1]
    assert gmba_programme.display_name == 'Global MBA'
    programme_master_courses = get_programme_master_courses([gmba_programme.id])
    assert len(programme_master_courses) == 1
    assert programme_master_courses[0].master_course.vle_course_id == 'it001'


@pytest.mark.django_db
def test_get_programme_master_courses_for_maths(programmes):
    maths_programme = programmes[2]
    assert maths_programme.display_name == 'Maths'
    programme_master_courses = get_programme_master_courses([maths_programme.id])
    ordered_programme_master_courses = programme_master_courses.order_by('master_course__vle_course_id')
    assert len(ordered_programme_master_courses) == 3
    assert list(map(lambda pmc: pmc.master_course.vle_course_id, ordered_programme_master_courses)) == [
        'maths001',
        'maths002',
        'maths003',
    ]


@patch('programmes.domain.requests')
@pytest.mark.django_db
def test_get_user_enrolled_scheduled_courses_by_programme_requests_lms_service(mock_requests, three_programmes_student_user):
    mock_requests.get.return_value.status_code = 200
    get_user_enrolled_scheduled_courses_by_programme(three_programmes_student_user)
    assert mock_requests.get.call_count == 1
    assert mock_requests.get.call_args[0][0] == '{}{}'.format(settings.VLEROOT, settings.ENROLMENTS_URL)
    assert mock_requests.get.call_args[1]['params'] == {
        'username': three_programmes_student_user.username,
        'role': 'student',
    }


@patch('programmes.domain.requests')
@pytest.mark.django_db
def test_get_user_enrolled_scheduled_courses_by_programme_requests_lms_service_for_tutors(mock_requests, three_programmes_tutor_user):
    mock_requests.get.return_value.status_code = 200
    get_user_enrolled_scheduled_courses_by_programme(three_programmes_tutor_user, 'tutor')
    assert mock_requests.get.call_count == 1
    assert mock_requests.get.call_args[0][0] == '{}{}'.format(settings.VLEROOT, settings.ENROLMENTS_URL)
    assert mock_requests.get.call_args[1]['params'] == {
        'username': three_programmes_tutor_user.username,
        'role': 'tutor',
    }


@patch('programmes.domain.requests')
@pytest.mark.django_db
def test_get_user_enrolled_scheduled_courses_by_programme_returns_programmes_as_list_of_dicts(mock_requests, two_programmes_student_user, programmes):
    mock_requests.get.return_value.status_code = 200
    l, d = get_user_enrolled_scheduled_courses_by_programme(two_programmes_student_user)
    assert type(l).__name__ == 'list'
    assert len(l) == 2
    assert l[0]['id'] == programmes[0].id
    assert l[1]['id'] == programmes[1].id


@patch('programmes.domain.requests')
@pytest.mark.django_db
def test_get_user_enrolled_scheduled_courses_by_programme_returns_courses(mock_requests, three_programmes_student_user, programmes):
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = {
        'courses': [
            {'masteridnumber': 'maths001'},  # from the 'Maths' programme
            {'masteridnumber': 'maths002'},  # from the 'Maths' programme
            {'masteridnumber': 'it001'},  # from the 'Global MBA' programme
        ]
    }
    d, m = get_user_enrolled_scheduled_courses_by_programme(three_programmes_student_user)
    assert d == [
        {
            'id': programmes[0].id,
            'display_name': 'CATS',
            'courses': [],
        },
        {
            'id': programmes[1].id,
            'display_name': 'Global MBA',
            'courses': [
                {'masteridnumber': 'it001'},
            ]
        },
        {
            'id': programmes[2].id,
            'display_name': 'Maths',
            'courses': [
                {'masteridnumber': 'maths001'},
                {'masteridnumber': 'maths002'},
            ]
        }
    ]


@patch('programmes.domain.requests')
@pytest.mark.django_db
def test_get_user_enrolled_scheduled_courses_by_programme_returns_completions(mock_requests, three_programmes_tutor_user):
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = {
        'courses': [],
        'module_completions': {
            'foo': 'bar',
            'students': []
        }
    }
    d, m = get_user_enrolled_scheduled_courses_by_programme(three_programmes_tutor_user)
    assert m == {'foo': 'bar', 'students': []}


@patch('programmes.domain.requests')
@pytest.mark.django_db
def test_get_user_enrolled_scheduled_courses_by_programme_retrieves_user_ids(mock_requests, three_programmes_tutor_user):
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = {
        'courses': [],
        'module_completions': {
            'students': [
                {'username': three_programmes_tutor_user.username},
                {'username': 'robologo'}
            ]
        }
    }
    d, m = get_user_enrolled_scheduled_courses_by_programme(three_programmes_tutor_user, 'tutor')
    assert m == {
        'students': [
            {
                'id': three_programmes_tutor_user.id,
                'username': three_programmes_tutor_user.username
            },
            {
                'id': None,
                'username': 'robologo'
            }
        ]
    }

