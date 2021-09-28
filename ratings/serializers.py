from rest_framework import serializers

from .models import Group


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ("group_name", "group_number")
