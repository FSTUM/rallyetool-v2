from django.http import JsonResponse
from rest_framework import serializers, status, viewsets
from rest_framework.parsers import JSONParser

from .models import Group

# Only enabled if settings.API is True


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields: list[str] = ["group_name", "group_number"]


# pylint: disable=redefined-builtin,unused-argument,no-self-use
class TeamsViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = TeamSerializer

    def get(self, request, format=None):
        queryset = Group.objects.all().order_by("number")
        serializer_class = TeamSerializer(data=queryset)
        return JsonResponse(serializer_class.data, safe=False)

    def post(self, request, format=None):
        data = JSONParser().parse(request)
        serializer = TeamSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # pylint: disable-next=invalid-name
    def delete(self, request, id, format=None):
        pass


# pylint: enable=redefined-builtin,unused-argument,no-self-use
