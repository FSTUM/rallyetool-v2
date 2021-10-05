from typing import List

from django.http import JsonResponse
from rest_framework import serializers, status, viewsets
from rest_framework.parsers import JSONParser

from .models import Group

# Only enabled if settings.API is True


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields: List[str] = ("group_name", "group_number")


class TeamsViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    queryset = Group.objects.all()
    serializer_class = TeamSerializer

    def get(self, request, format=None):  # pylint: disable=redefined-builtin,unused-argument
        queryset = Group.objects.all().order_by("number")
        serializer_class = TeamSerializer(data=queryset)
        return JsonResponse(serializer_class.data, safe=False)

    def post(self, request, format=None):  # pylint: disable=redefined-builtin,unused-argument
        data = JSONParser().parse(request)
        serializer = TeamSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):  # pylint: disable=redefined-builtin,invalid-name,unused-argument
        pass
