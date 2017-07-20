from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

import pytest

from programmes.models import Programme, UserProgramme, MasterCourse, ProgrammeMasterCourse


@pytest.fixture
def students_group():
    return Group.objects.create(name='students')


@pytest.fixture
def tutors_group():
    return Group.objects.create(name='tutors')


@pytest.fixture
def master_courses():
    m1 = MasterCourse.objects.create(
        display_name='Basic Maths',
        vle_course_id='maths001'
    )
    m2 = MasterCourse.objects.create(
        display_name='Intermediate Maths',
        vle_course_id='maths002'
    )
    m3 = MasterCourse.objects.create(
        display_name='Advanced Maths',
        vle_course_id='maths003'
    )
    m4 = MasterCourse.objects.create(
        display_name='Introduction to IT',
        vle_course_id='it001'
    )
    return [m1, m2, m3, m4]


@pytest.fixture
def programmes(master_courses):
    # CATS (no master courses)
    cats = Programme.objects.create(
        display_name='CATS'
    )

    # GMBA (one master course)
    gmba = Programme.objects.create(
        display_name='Global MBA'
    )
    ProgrammeMasterCourse.objects.create(
        programme=gmba,
        master_course=master_courses[3]
    )

    # Maths (3 master courses)
    maths = Programme.objects.create(
        display_name='Maths'
    )
    for i in [0, 1, 2]:
        ProgrammeMasterCourse.objects.create(
            programme=maths,
            master_course=master_courses[i]
        )

    return [cats, gmba, maths]


@pytest.fixture
def three_programmes_student_user(programmes, students_group):
    u = get_user_model().objects.create_user(
        username='student.1',
        email='student1@into.uk.com',
        first_name='Bob',
        last_name='Smith',
        password='topsecret'
    )
    for i in [0, 1, 2]:
        UserProgramme.objects.create(
            programme=programmes[i],
            user=u
        )
    u.groups.add(students_group)
    return u


@pytest.fixture
def three_programmes_tutor_user(programmes, tutors_group):
    u = get_user_model().objects.create_user(
        username='tutor.1',
        email='tutor1@into.uk.com',
        first_name='Erik',
        last_name='Meijer',
        password='topsecret'
    )
    for i in [0, 1, 2]:
        UserProgramme.objects.create(
            programme=programmes[i],
            user=u
        )
    u.groups.add(tutors_group)
    return u


@pytest.fixture
def two_programmes_student_user(programmes, students_group):
    u = get_user_model().objects.create_user(
        username='student.1',
        email='student1@into.uk.com',
        first_name='Bob',
        last_name='Smith',
        password='topsecret'
    )
    for i in [0, 1]:
        UserProgramme.objects.create(
            programme=programmes[i],
            user=u
        )
    u.groups.add(students_group)
    return u


@pytest.fixture
def two_programmes_tutor_user(programmes, tutors_group):
    u = get_user_model().objects.create_user(
        username='tutor.1',
        email='tutor1@into.uk.com',
        first_name='Erik',
        last_name='Meijer',
        password='topsecret'
    )
    for i in [0, 1]:
        UserProgramme.objects.create(
            programme=programmes[i],
            user=u
        )
    u.groups.add(tutors_group)
    return u


@pytest.fixture
def one_programme_student_user(programmes, students_group):
    u = get_user_model().objects.create_user(
        username='student.2',
        email='student2@into.uk.com',
        first_name='Fred',
        last_name='Jones',
        password='topsecret'
    )
    UserProgramme.objects.create(
        programme=programmes[0],
        user=u
    )
    u.groups.add(students_group)
    return u


@pytest.fixture
def no_programmes_student_user(students_group):
    u = get_user_model().objects.create_user(
        username='student.3',
        email='student3@into.uk.com',
        first_name='Bill',
        last_name='Davis',
        password='topsecret'
    )
    u.groups.add(students_group)
    return u


@pytest.fixture
def no_programmes_tutor_user(tutors_group):
    u = get_user_model().objects.create_user(
        username='tutor.1',
        email='tutor1@into.uk.com',
        first_name='Erik',
        last_name='Meijer',
        password='topsecret'
    )
    u.groups.add(tutors_group)
    return u
