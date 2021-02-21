from rest_framework import serializers
from codes.models import ActivityType


class ActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityType
        fields = "__all__"
        read_only_fields = ('id',)


