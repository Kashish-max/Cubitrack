from django_filters import rest_framework as django_filters
from rest_framework import viewsets, status, filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Box
from .serializers import BoxInputSerializer, BoxOutputSerializer
from .utils import annotate_area_and_volume


class BoxFilter(django_filters.FilterSet):
    created_after = django_filters.DateFilter(field_name='created_on', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_on', lookup_expr='lte')

    fields_with_lookups = ['length', 'breadth', 'height', 'area', 'volume']

    for field_name in fields_with_lookups:
        field_lte = field_name + '__lt'
        field_gte = field_name + '__gt'
        
        filters = {
            field_name: django_filters.NumberFilter(field_name=field_name),
            field_lte: django_filters.NumberFilter(field_name=field_name, lookup_expr='lte'),
            field_gte: django_filters.NumberFilter(field_name=field_name, lookup_expr='gte')
        }
        
        locals().update(filters)
        
    class Meta:
        model = Box
        fields = [
            *['length', 'breadth', 'height', 'area', 'volume'],
            *[f'{field}__lt' for field in ['length', 'breadth', 'height', 'area', 'volume']],
            *[f'{field}__gt' for field in ['length', 'breadth', 'height', 'area', 'volume']],
            'creator__username', 'created_after', 'created_before'
        ]


class BoxViewSet(viewsets.ModelViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxInputSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    filter_backends = [django_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = BoxFilter

    ordering_fields = ['created_on', 'updated_on']

    def get_permissions(self):
        if self.action in ['create', 'partial_update', 'myboxes']:
            permission_classes = [IsAdminUser]
        elif self.action in ['retrieve', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.update_and_filter_queryset(self.get_queryset())
            serialize_value = BoxOutputSerializer(queryset, many=True, context={"request": request}).data
            return Response(serialize_value, status=status.HTTP_200_OK)
        except Exception as E:
            return Response({'error': str(E)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update_and_filter_queryset(self, queryset):
        queryset = annotate_area_and_volume(queryset)
        queryset = super().filter_queryset(queryset)
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        restricted_fields = ['creator', 'created_on']
        for field in restricted_fields:
            if field in request.data:
                raise PermissionDenied(f"You are not allowed to update the '{field}' field.")
        return super().partial_update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        if self.request.user != instance.creator:
            raise PermissionDenied("You are not allowed to remove this Box.")
        instance.delete()

    @action(detail=False, methods=["GET"])
    def myboxes(self, request):
        boxes = Box.objects.filter(creator=request.user)
        queryset = self.update_and_filter_queryset(boxes)
        serializer = BoxOutputSerializer(queryset, many=True, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

