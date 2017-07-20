from rest_framework import serializers

from .models import UserProgramme


class UserProgrammeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgramme
        fields = (
            'programme',
        )
        depth = 2
