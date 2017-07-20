from datetime import datetime

import pytest
from mock import patch

from programmes.models import MasterCourse


@patch('programmes.models.datetime')
@pytest.mark.django_db
def test_next_start_date(mock_datetime):
    course = MasterCourse.objects.create(
        vle_course_id='123',
        display_name='Master Course 001'
    )
    course.scheduledcourse_set.create(
        vle_course_id='123/01',
        display_name='Scheduled Course 001',
        start_date=datetime.strptime('2015-01-01', '%Y-%m-%d'),
    )
    course.scheduledcourse_set.create(
        vle_course_id='123/02',
        display_name='Scheduled Course 002',
        start_date=datetime.strptime('2015-01-02', '%Y-%m-%d'),
    )
    course.scheduledcourse_set.create(
        vle_course_id='123/03',
        display_name='Scheduled Course 003',
        start_date=datetime.strptime('2015-01-03', '%Y-%m-%d'),
    )
    course.scheduledcourse_set.create(
        vle_course_id='123/04',
        display_name='Scheduled Course 004',
        start_date=None,
    )
    today = datetime.strptime('2015-01-02', '%Y-%m-%d').date()
    mock_datetime.today.return_value.date.return_value = today
    assert str(course.next_start_date) == '2015-01-02'
