import base64
import json

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.encoding import force_str

import pytest

from programmes.models import MasterCourse, ScheduledCourse, ScheduledCourseGroup


@pytest.fixture
def auth_headers():
    return {}


@pytest.fixture
def master_course():
    return MasterCourse.objects.create(
        vle_course_id='001',
        display_name='Zero Zero One'
    )


@pytest.fixture
def scheduled_course(master_course):
    return ScheduledCourse.objects.create(
        master_course=master_course,
        vle_course_id='001/01',
        display_name='Zero Zero One / Zero One'
    )


@pytest.fixture
def scheduled_course_group(scheduled_course):
    return ScheduledCourseGroup.objects.create(
        scheduled_course=scheduled_course,
        vle_group_id='001/01/A',
        display_name='Group A'
    )


@pytest.fixture
def scheduled_course_group_b(scheduled_course):
    return ScheduledCourseGroup.objects.create(
        scheduled_course=scheduled_course,
        vle_group_id='001/01/B',
        display_name='Group B'
    )


@pytest.mark.django_db
def test_create_master_course_no_vle_course_id(auth_headers, client):
    # make a request
    post_data = {
        'name': 'Zero Zero One',
    }
    response = client.post(reverse('programmes_api:create_master_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Must specify vle_course_id and name')


@pytest.mark.django_db
def test_create_master_course_no_name(auth_headers, client):
    # make a request
    post_data = {
        'vle_course_id': '001',
    }
    response = client.post(reverse('programmes_api:create_master_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Must specify vle_course_id and name')


@pytest.mark.django_db
def test_create_master_course_already_exists(auth_headers, client):
    MasterCourse.objects.create(vle_course_id='001', display_name='foobar')

    # make a request
    post_data = {
        'vle_course_id': '001',
        'name': 'wibble',
    }
    response = client.post(reverse('programmes_api:create_master_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Course with given vle_course_id already exists')


@pytest.mark.django_db
def test_create_master_course_successfully(auth_headers, client):
    # make a request
    post_data = {
        'vle_course_id': '001',
        'name': 'Zero Zero One',
    }
    response = client.post(reverse('programmes_api:create_master_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it was successful
    assert response.status_code == 200

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('successMessage') == _('Course created successfully!')

    # check the instance
    course = MasterCourse.objects.get(vle_course_id='001')
    assert course.display_name == 'Zero Zero One'


@pytest.mark.django_db
def test_create_master_course_successfully_all_attributes(auth_headers, client):
    # make a request
    post_data = {
        'vle_course_id': '001',
        'name': 'Zero Zero One',
        'weeks_duration': 30,
        'compulsory': True,
        'commitment': '4 days per year',
        'credits': 20,
    }
    response = client.post(reverse('programmes_api:create_master_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it was successful
    assert response.status_code == 200

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('successMessage') == _('Course created successfully!')

    # check the instance
    course = MasterCourse.objects.get(vle_course_id='001')
    assert course.display_name == 'Zero Zero One'
    assert course.weeks_duration == 30
    assert course.compulsory
    assert course.credits == 20
    assert course.commitment == '4 days per year'


@pytest.mark.django_db
def test_update_master_course_missing_fields(auth_headers, client):
    # make a request
    post_data = {}
    response = client.post(reverse('programmes_api:update_master_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Must specify old_vle_course_id, vle_course_id, name')


@pytest.mark.django_db
def test_update_master_course_does_not_exist(auth_headers, client):
    # make a request
    post_data = {
        'old_vle_course_id': '001',
        'vle_course_id': '002',
        'name': 'wibble',
    }
    response = client.post(reverse('programmes_api:update_master_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Course with given old_vle_course_id does not exist')


@pytest.mark.django_db
def test_update_master_course_successfully(auth_headers, client):
    MasterCourse.objects.create(
        vle_course_id='001',
        display_name='Zero Zero One',
        weeks_duration=30,
        compulsory=False,
        credits=20,
        commitment='4 days per year'
    )

    # make a request
    post_data = {
        'old_vle_course_id': '001',
        'vle_course_id': '002',
        'name': 'Zero Zero Two',
        'weeks_duration': 60,
        'compulsory': False,
        'commitment': '4 days per hour',
        'credits': 1,
    }
    response = client.post(reverse('programmes_api:update_master_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it was successful
    assert response.status_code == 200

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('successMessage') == _('Course updated successfully!')

    # check the instance
    course = MasterCourse.objects.get(vle_course_id='002')
    assert course.display_name == 'Zero Zero Two'
    assert course.weeks_duration == 60
    assert not course.compulsory
    assert course.credits == 1
    assert course.commitment == '4 days per hour'

    # check there's only one MasterCourse
    assert MasterCourse.objects.count() == 1


@pytest.mark.django_db
def test_delete_master_course_missing_field(auth_headers, client):
    # make a request
    post_data = {}
    response = client.post(reverse('programmes_api:delete_master_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Must specify vle_course_id')


@pytest.mark.django_db
def test_delete_master_course_does_not_exist(auth_headers, client):
    # make a request
    post_data = {
        'vle_course_id': '001',
    }
    response = client.post(reverse('programmes_api:delete_master_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Course with given vle_course_id does not exist')


@pytest.mark.django_db
def test_delete_master_course_successfully(auth_headers, client):
    # 001
    master_1 = MasterCourse.objects.create(vle_course_id='001', display_name='master_1')
    ScheduledCourse.objects.create(vle_course_id='001/01', display_name='scheduled_1_1', master_course=master_1)
    ScheduledCourse.objects.create(vle_course_id='001/02', display_name='scheduled_1_2', master_course=master_1)

    # 002
    master_2 = MasterCourse.objects.create(vle_course_id='002', display_name='master_2')
    ScheduledCourse.objects.create(vle_course_id='002/01', display_name='master_2_1', master_course=master_2)
    ScheduledCourse.objects.create(vle_course_id='002/02', display_name='master_2_2', master_course=master_2)

    # make a request
    post_data = {
        'vle_course_id': '001',
    }
    response = client.post(reverse('programmes_api:delete_master_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it was successful
    assert response.status_code == 200

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('successMessage') == _('Course deleted successfully!')

    # check there's no MasterCourse
    assert MasterCourse.objects.filter(vle_course_id='001').count() == 0

    # check the related models were also deleted
    assert ScheduledCourse.objects.filter(vle_course_id='001').count() == 0

    # check the '002' course hasn't been deleted
    assert MasterCourse.objects.filter(vle_course_id='002').count() == 1
    assert ScheduledCourse.objects.filter(master_course__vle_course_id='002').count() == 2


@pytest.mark.django_db
def test_create_scheduled_course_no_master_vle_course_id(auth_headers, client):
    # make a request
    post_data = {
        'vle_course_id': '001',
        'name': 'Zero Zero One',
    }
    response = client.post(reverse('programmes_api:create_scheduled_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Must specify master_vle_course_id, vle_course_id and name')


@pytest.mark.django_db
def test_create_scheduled_course_no_vle_course_id(auth_headers, client):
    # make a request
    post_data = {
        'master_vle_course_id': '001',
        'name': 'Zero Zero One',
    }
    response = client.post(reverse('programmes_api:create_scheduled_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Must specify master_vle_course_id, vle_course_id and name')


@pytest.mark.django_db
def test_create_scheduled_course_no_name(auth_headers, client):
    # make a request
    post_data = {
        'master_vle_course_id': '001',
        'vle_course_id': '002',
    }
    response = client.post(reverse('programmes_api:create_scheduled_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Must specify master_vle_course_id, vle_course_id and name')


@pytest.mark.django_db
def test_create_scheduled_course_already_exists(auth_headers, client):
    # create a master and a scheduled course
    master = MasterCourse.objects.create(vle_course_id='001', display_name='master_1')
    ScheduledCourse.objects.create(vle_course_id='002', display_name='foobar', master_course=master)

    # make a request
    post_data = {
        'master_vle_course_id': '001',
        'vle_course_id': '002',
        'name': 'wibble',
    }
    response = client.post(reverse('programmes_api:create_scheduled_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Course with given vle_course_id already exists')


@pytest.mark.django_db
def test_create_scheduled_course_master_does_not_exist(auth_headers, client):
    # make a request
    post_data = {
        'master_vle_course_id': 'DOES_NOT_EXIST',
        'vle_course_id': '002',
        'name': 'wibble',
    }
    response = client.post(reverse('programmes_api:create_scheduled_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Course with given master_vle_course_id does not exist')


@pytest.mark.django_db
def test_create_scheduled_course_successfully(auth_headers, client):
    # create a master course
    MasterCourse.objects.create(vle_course_id='001', display_name='master_1')

    # make a request
    post_data = {
        'master_vle_course_id': '001',
        'vle_course_id': '002',
        'name': 'Zero Zero One',
    }
    response = client.post(reverse('programmes_api:create_scheduled_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it was successful
    assert response.status_code == 200

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('successMessage') == _('Course created successfully!')

    # check the instance
    course = ScheduledCourse.objects.get(vle_course_id='002')
    assert course.display_name == 'Zero Zero One'
    assert course.master_course.vle_course_id == '001'


@pytest.mark.django_db
def test_create_scheduled_course_successfully_all_attributes(auth_headers, client):
    # create a master course
    MasterCourse.objects.create(vle_course_id='001', display_name='master_1')

    # make a request
    post_data = {
        'master_vle_course_id': '001',
        'vle_course_id': '002',
        'name': 'Zero Zero One',
        'opendate': '2015-01-01',
        'startdate': '2015-02-01',
        'enddate': '2015-03-01',
        'closedate': '2015-04-01',
    }
    response = client.post(reverse('programmes_api:create_scheduled_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it was successful
    assert response.status_code == 200

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('successMessage') == _('Course created successfully!')

    # check the instance
    course = ScheduledCourse.objects.get(vle_course_id='002')
    assert course.display_name == 'Zero Zero One'
    assert str(course.open_date) == '2015-01-01'
    assert str(course.start_date) == '2015-02-01'
    assert str(course.end_date) == '2015-03-01'
    assert str(course.close_date) == '2015-04-01'


@pytest.mark.django_db
def test_update_scheduled_course_missing_fields(auth_headers, client):
    # make a request
    post_data = {}
    response = client.post(reverse('programmes_api:update_scheduled_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Must specify master_vle_course_id, old_vle_course_id, vle_course_id and name')


@pytest.mark.django_db
def test_update_scheduled_course_does_not_exist(auth_headers, client):
    # make a request
    post_data = {
        'master_vle_course_id': '001',
        'old_vle_course_id': '002',
        'vle_course_id': '003',
        'name': 'wibble',
    }
    response = client.post(reverse('programmes_api:update_scheduled_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Course with given old_vle_course_id and master_vle_course_id does not exist')


@pytest.mark.django_db
def test_update_scheduled_course_master_does_not_exist(auth_headers, client):
    # create a master and a scheduled course
    master = MasterCourse.objects.create(vle_course_id='001', display_name='master_1')
    ScheduledCourse.objects.create(vle_course_id='002', display_name='foobar', master_course=master)

    # make a request
    post_data = {
        'master_vle_course_id': 'DOES_NOT_EXIST',
        'old_vle_course_id': '002',
        'vle_course_id': '003',
        'name': 'wibble',
    }
    response = client.post(reverse('programmes_api:update_scheduled_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Course with given old_vle_course_id and master_vle_course_id does not exist')


@pytest.mark.django_db
def test_update_scheduled_course_successfully(auth_headers, client):
    # create a master and a scheduled course
    master = MasterCourse.objects.create(vle_course_id='001', display_name='master_1')
    ScheduledCourse.objects.create(vle_course_id='002', display_name='Zero Zero One', master_course=master)

    # make a request
    post_data = {
        'master_vle_course_id': '001',
        'old_vle_course_id': '002',
        'vle_course_id': '003',
        'name': 'Zero Zero Two',
    }
    response = client.post(reverse('programmes_api:update_scheduled_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it was successful
    assert response.status_code == 200

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('successMessage') == _('Course updated successfully!')

    # check the instance
    course = ScheduledCourse.objects.get(vle_course_id='003')
    assert course.display_name == 'Zero Zero Two'
    assert course.master_course.vle_course_id == '001'

    # check there's only one ScheduledCourse
    assert ScheduledCourse.objects.count() == 1


@pytest.mark.django_db
def test_update_scheduled_course_successfully_all_attributes(auth_headers, client):
    # create a master and a scheduled course
    master = MasterCourse.objects.create(vle_course_id='001', display_name='master_1')
    ScheduledCourse.objects.create(
        vle_course_id='002',
        display_name='Zero Zero One',
        master_course=master,
        open_date='2015-01-01',
        start_date='2015-02-01',
        end_date='2015-03-01',
        close_date='2015-04-01'
    )

    # make a request
    post_data = {
        'master_vle_course_id': '001',
        'old_vle_course_id': '002',
        'vle_course_id': '003',
        'name': 'Zero Zero Two',
        'opendate': '2015-01-31',
        'startdate': '2015-02-28',
        'enddate': '2015-03-31',
        'closedate': '2015-04-30',
    }
    response = client.post(reverse('programmes_api:update_scheduled_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it was successful
    assert response.status_code == 200

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('successMessage') == _('Course updated successfully!')

    # check the instance
    course = ScheduledCourse.objects.get(vle_course_id='003', master_course__vle_course_id='001')
    assert course.display_name == 'Zero Zero Two'
    assert str(course.open_date) == '2015-01-31'
    assert str(course.start_date) == '2015-02-28'
    assert str(course.end_date) == '2015-03-31'
    assert str(course.close_date) == '2015-04-30'


@pytest.mark.django_db
def test_delete_scheduled_course_missing_field(auth_headers, client):
    # make a request
    post_data = {}
    response = client.post(reverse('programmes_api:delete_scheduled_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Must specify master_vle_course_id and vle_course_id')


@pytest.mark.django_db
def test_delete_scheduled_course_does_not_exist(auth_headers, client):
    # make a request
    post_data = {
        'master_vle_course_id': '001',
        'vle_course_id': '002',
    }
    response = client.post(reverse('programmes_api:delete_scheduled_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Course with given old_vle_course_id and master_vle_course_id does not exist')


@pytest.mark.django_db
def test_delete_scheduled_course_master_does_not_exist(auth_headers, client):
    # create a master and a scheduled course
    master = MasterCourse.objects.create(vle_course_id='001', display_name='master_1')
    ScheduledCourse.objects.create(vle_course_id='002', display_name='Zero Zero One', master_course=master)

    # make a request
    post_data = {
        'master_vle_course_id': 'DOES_NOT_EXIST',
        'vle_course_id': '002',
    }
    response = client.post(reverse('programmes_api:delete_scheduled_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Course with given old_vle_course_id and master_vle_course_id does not exist')


@pytest.mark.django_db
def test_delete_scheduled_course_successfully(auth_headers, client):
    # master
    master = MasterCourse.objects.create(vle_course_id='master', display_name='scheduled_1')

    # 001
    ScheduledCourse.objects.create(vle_course_id='001', display_name='scheduled_1_1', master_course=master)

    # 002
    ScheduledCourse.objects.create(vle_course_id='002', display_name='scheduled_1_2', master_course=master)

    # make a request
    post_data = {
        'master_vle_course_id': 'master',
        'vle_course_id': '001',
    }
    response = client.post(reverse('programmes_api:delete_scheduled_course'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it was successful
    assert response.status_code == 200

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('successMessage') == _('Course deleted successfully!')

    # check there's no ScheduledCourse
    assert ScheduledCourse.objects.filter(vle_course_id='001').count() == 0

    # check the '002' course hasn't been deleted
    assert ScheduledCourse.objects.filter(vle_course_id='002').count() == 1


@pytest.mark.django_db
def test_create_group_no_vle_course_id(auth_headers, client):
    # make a request
    post_data = {
        'vle_group_id': '001a',
        'name': 'Zero Zero One',
    }
    response = client.post(reverse('programmes_api:create_group'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Must specify vle_course_id, vle_group_id, name')


@pytest.mark.django_db
def test_create_group_no_vle_group_id(auth_headers, client):
    # make a request
    post_data = {
        'vle_course_id': '001',
        'name': 'Zero Zero One',
    }
    response = client.post(reverse('programmes_api:create_group'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Must specify vle_course_id, vle_group_id, name')


@pytest.mark.django_db
def test_create_group_no_name(auth_headers, client):
    # make a request
    post_data = {
        'vle_course_id': '001',
        'vle_group_id': '001a',
    }
    response = client.post(reverse('programmes_api:create_group'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Must specify vle_course_id, vle_group_id, name')


@pytest.mark.django_db
def test_create_group_already_exists(auth_headers, scheduled_course_group, client):
    # make a request
    post_data = {
        'vle_course_id': '001/01',
        'vle_group_id': '001/01/A',
        'name': 'irrelevant',
    }
    response = client.post(reverse('programmes_api:create_group'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Group with given vle_course_id and vle_group_id already exists')


@pytest.mark.django_db
def test_create_group_without_existing_course(auth_headers, client):
    # make a request
    post_data = {
        'vle_course_id': '001/01',
        'vle_group_id': '001/01/A',
        'name': 'irrelevant',
    }
    response = client.post(reverse('programmes_api:create_group'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Course with given vle_course_id does not exist')


@pytest.mark.django_db
def test_create_group_successfully(auth_headers, scheduled_course, client):
    # make a request
    post_data = {
        'vle_course_id': '001/01',
        'vle_group_id': '001/01/A',
        'name': 'Group A',
    }
    response = client.post(reverse('programmes_api:create_group'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it was successful
    assert response.status_code == 200

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('successMessage') == _('Group created successfully!')

    # check the instance
    group = ScheduledCourseGroup.objects.get(scheduled_course=scheduled_course, vle_group_id='001/01/A')
    assert group.display_name == 'Group A'


@pytest.mark.django_db
def test_update_group_missing_fields(auth_headers, client):
    # make a request
    post_data = {}
    response = client.post(reverse('programmes_api:update_group'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Must specify vle_course_id, old_vle_group_id, vle_group_id, name')


@pytest.mark.django_db
def test_update_group_missing_vle_group_id(auth_headers, client):
    # make a request
    post_data = {
        'vle_course_id': 'irrelevant',
        'old_vle_group_id': 'irrelevant',
        'name': 'irrelevant',
    }
    response = client.post(reverse('programmes_api:update_group'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Must specify vle_course_id, old_vle_group_id, vle_group_id, name')


@pytest.mark.django_db
def test_update_group_does_not_exist(auth_headers, client, scheduled_course):
    # make a request
    post_data = {
        'vle_course_id': '001/01',
        'old_vle_group_id': '001/01/Y',
        'vle_group_id': '001/01/Z',
        'name': 'Group Z',
    }
    response = client.post(reverse('programmes_api:update_group'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Group with given vle_course_id and old_vle_group_id does not exist')


@pytest.mark.django_db
def test_update_group_successfully(auth_headers, client, scheduled_course_group):
    # make a request
    post_data = {
        'vle_course_id': '001/01',
        'old_vle_group_id': '001/01/A',
        'vle_group_id': '001/01/B',
        'name': 'Group B',
    }
    response = client.post(reverse('programmes_api:update_group'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it was successful
    assert response.status_code == 200

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('successMessage') == _('Group updated successfully!')

    # check the instance
    group = ScheduledCourseGroup.objects.get(vle_group_id='001/01/B')
    assert group.display_name == 'Group B'

    # check there's only one ScheduledCourseGroup
    assert ScheduledCourseGroup.objects.count() == 1


@pytest.mark.django_db
def test_delete_group_missing_field(auth_headers, client):
    # make a request
    post_data = {}
    response = client.post(reverse('programmes_api:delete_group'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Must specify vle_course_id and vle_group_id')


@pytest.mark.django_db
def test_delete_group_does_not_exist(auth_headers, client, scheduled_course):
    # make a request
    post_data = {
        'vle_course_id': '001/01',
        'vle_group_id': '001/01/Z',
    }
    response = client.post(reverse('programmes_api:delete_group'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it wasn't successful
    assert response.status_code == 400

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('errorMessage') == _('Group with given vle_course_id and vle_group_id does not exist')


@pytest.mark.django_db
def test_delete_group_successfully(auth_headers, client, scheduled_course, scheduled_course_group, scheduled_course_group_b):
    # make a request
    post_data = {
        'vle_course_id': '001/01',
        'vle_group_id': '001/01/A',
    }
    response = client.post(reverse('programmes_api:delete_group'), content_type='application/json', data=json.dumps(post_data), **auth_headers)

    # check it was successful
    assert response.status_code == 200

    # check the JSON
    data = json.loads(force_str(response.content))
    assert data.get('successMessage') == _('Group deleted successfully!')

    # check there's no ScheduledCourseGroup
    # self.assertEqual(0, ScheduledCourseGroup.objects.filter(vle_course_id='001', vle_group_id='001a').count())
    assert ScheduledCourseGroup.objects.filter(scheduled_course=scheduled_course, vle_group_id='001/01/A').count() == 0

    # check the other ScheduledCourseGroup hasn't been deleted
    assert ScheduledCourseGroup.objects.filter(scheduled_course=scheduled_course, vle_group_id='001/01/B').count() == 1
