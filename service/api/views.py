from rest_framework import generics
from rest_framework.exceptions import NotFound, ValidationError

from service.models import Services
from .serializers import ServiceSerializer


class ServiceListCreateView(generics.ListCreateAPIView):
    """
    GET  -> list services (paginated, searchable, filterable)
    POST -> create a new service
    """
    queryset = Services.objects.all()
    serializer_class = ServiceSerializer
    filterset_fields = ['status']
    search_fields = ['service_name']
    ordering_fields = ['service_name', 'price', 'duration', 'created_at']


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    -> single service details
    PUT    -> full update
    PATCH  -> partial update
    DELETE -> remove service
    """
    serializer_class = ServiceSerializer

    def get_object(self):
        pk = self.kwargs['pk']

        if not pk.isdigit():
            raise ValidationError({'detail': 'Service ID must be a positive number.'})

        try:
            return Services.objects.get(pk=int(pk))
        except Services.DoesNotExist:
            raise NotFound(f'Service with ID {pk} not found.')
