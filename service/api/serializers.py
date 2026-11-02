from rest_framework import serializers

from service.models import Services


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Services
        fields = [
            'id', 'service_name', 'description', 'price',
            'duration', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_service_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError('Service name must have at least 3 characters.')

        # same name with different case should also be treated as duplicate
        qs = Services.objects.filter(service_name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('A service with this name already exists.')
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price must be greater than 0.')
        return value

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError('Duration must be at least 1 minute.')
        if value > 1440:
            raise serializers.ValidationError('Duration cannot be more than 1440 minutes (24 hours).')
        return value
