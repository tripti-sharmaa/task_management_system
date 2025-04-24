from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.inspectors import CoreAPICompatInspector
from drf_yasg.utils import swagger_auto_schema

class CustomFilterInspector(CoreAPICompatInspector):
    def get_filter_parameters(self, filter_backend):
        """
        Add custom filter parameters for Swagger documentation.
        """
        if hasattr(filter_backend, 'get_schema_fields'):
            return filter_backend.get_schema_fields(self.view)
        return super().get_filter_parameters(filter_backend)

@swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'search', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'manager', openapi.IN_QUERY, description="Filter by manager ID", type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'members', openapi.IN_QUERY, description="Filter by member ID", type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'status', openapi.IN_QUERY, description="Filter by task status", type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'priority', openapi.IN_QUERY, description="Filter by task priority", type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'project', openapi.IN_QUERY, description="Filter by project ID", type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'assigned_to', openapi.IN_QUERY, description="Filter by assigned user ID", type=openapi.TYPE_INTEGER
        ),
    ]
)
def custom_swagger_view():
    """
    Custom Swagger view to include filter parameters.
    """
    pass

schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@myapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
