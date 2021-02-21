from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view
from codes.api.serializers import ActivityTypeSerializer
from codes.models import ActivityType


@api_view(['POST', ])
def add_activity_code(request):
    activity_code_serializer = ActivityTypeSerializer(data=request.data)
    if activity_code_serializer.is_valid():
        try:
            activity_code_serializer.save()
        except Exception as e:
            print(e)
            data = {"success": False, "error": {"code": 400, "message": "ِActivity type not created"}}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        data = {"success": True, "data": activity_code_serializer.data}
        return Response(data, status=status.HTTP_201_CREATED)
    else:
        data = {"success": False, "error": {"code": 400, "message": activity_code_serializer.errors}}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

class ActivityListView(ListAPIView):
    serializer_class = ActivityTypeSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = ('code',)
    ordering_fields = ('code',)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return ActivityType.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            data = {"success": True, "count": paginated_response.data["count"], "data": serializer.data, }
            return Response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = {"success": True, "data": serializer.data}
        return Response(data)