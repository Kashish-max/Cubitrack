from django.db.models import F

def annotate_area_and_volume(queryset):
    return queryset.annotate(
        area=F('length') * F('breadth'),
        volume=F('length') * F('breadth') * F('height')
    )
