import pytest

from programmes.domain import get_user_programmes
from programmes.serializers import UserProgrammeSerializer

from .fixtures import *


@pytest.mark.django_db
def test_user_programme_serializer(two_programmes_student_user, programmes):
    user_programmes = get_user_programmes(two_programmes_student_user)
    user_programmes_serializer = UserProgrammeSerializer(user_programmes, many=True)
    data = user_programmes_serializer.data
    assert len(data) == 2
    assert data[0]['programme']['display_name'] == programmes[0].display_name
    assert data[1]['programme']['display_name'] == programmes[1].display_name
