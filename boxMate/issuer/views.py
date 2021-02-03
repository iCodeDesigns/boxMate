from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view

from issuer.models import Issuer
from issuer.serializers import IssuerSerializer


# Create your views here.
@api_view(['POST', ])
def add_issuer(request):
    issuer_serializer = IssuerSerializer(data=request.data)
    if issuer_serializer.is_valid():
        try:
            issuer_serializer.save()
        except Exception as e:
            print(e)
            data = {"success": False, "error": {"code": 400, "message": "Issuer not created"}}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        data = {"success": True, "data": issuer_serializer.data}
        return Response(data, status=status.HTTP_201_CREATED)
    else:
        data = {"success": False, "error": {"code": 400, "message": issuer_serializer.errors}}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class IssuerListView(ListAPIView):
    serializer_class = IssuerSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = ('id', 'reg_num',)
    ordering_fields = ('id',)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Issuer.objects.all()

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
