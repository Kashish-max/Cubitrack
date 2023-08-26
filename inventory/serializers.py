from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.serializers import UserSerializer
from .models import Box
from .utils import annotate_area_and_volume


class BoxInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        exclude = ['creator']

    def validate(self, data):
        if(self.context['request'].method != 'POST'):
            return data

        user = self.context['request'].user
        
        all_boxes = Box.objects.filter()
        all_boxes = annotate_area_and_volume(all_boxes)
        all_user_boxes = Box.objects.filter(creator=user)
        all_user_boxes = annotate_area_and_volume(all_user_boxes)

        total_boxes_count = all_boxes.count()
        user_boxes_count = all_user_boxes.count()

        new_area = data['length'] * data['breadth']
        avg_area = all_boxes.aggregate(area__avg=Avg('area'))['area__avg']

        # checking if the average area of all boxes would exceed the limit
        print(f'avg_area: {avg_area}')
        print(f'total_boxes_count: {total_boxes_count}')

        if avg_area is None:
            avg_area = 0

        if (avg_area * total_boxes_count + new_area) / (total_boxes_count + 1) > int(settings.A1):
            raise ValidationError("Average area of all boxes would exceed the limit.")

        new_volume = new_area * data['height']
        avg_volume = all_user_boxes.aggregate(volume__avg=Avg('length') * Avg('breadth') * Avg('height'))['volume__avg']

        if avg_volume is None:
            avg_volume = 0
            
        # checking if the average volume of all boxes added by the current user would exceed the limit
        if (avg_volume * user_boxes_count + new_volume) / (user_boxes_count + 1) > int(settings.V1):
            raise ValidationError("Average volume of all your boxes would exceed the limit.")

        week_ago = timezone.now() - timedelta(weeks=1)

        # checking if the total boxes added in the last week would exceed the limit
        if all_boxes.filter(created_on__gte=week_ago).count() >= int(settings.L1):
            raise ValidationError("Total boxes added in the last week would exceed the limit.")

        # checking if the total boxes added by the current user in the last week would exceed the limit
        if all_user_boxes.filter(created_on__gte=week_ago).count() >= int(settings.L2):
            raise ValidationError("Total boxes added by you in the last week would exceed the limit.")

        return data


class BoxOutputSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    volume = serializers.SerializerMethodField()

    class Meta:
        model = Box
        exclude = ['created_on']

    def get_creator(self, obj):
        creator = obj.creator
        if creator:
            return UserSerializer(creator).data
        return None
    
    def get_area(self, obj):
        return obj.length * obj.breadth
    
    def get_volume(self, obj):
        return obj.length * obj.breadth * obj.height
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not self.context['request'].user.is_staff:
            representation.pop('creator', None)
            representation.pop('updated_on', None)
        return representation
    