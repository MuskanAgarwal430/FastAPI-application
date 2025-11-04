from django.urls import  path
from .views import FirebaseIssueSyncView, import_root_causes, fetch_issue_parts_from_firebase, fetch_parts_from_firebase, \
    get_vendor_data, get_vehicles_data, get_cities_data, get_transfer_history

urlpatterns = [
    path('issue/', FirebaseIssueSyncView.as_view(), name="firebase"),
    path('sync-root-causes/', import_root_causes),
    path('issue_parts/', fetch_issue_parts_from_firebase),
    path('issue_part/', fetch_parts_from_firebase),
    path('vendor/', get_vendor_data),
    path('vehicle/',get_vehicles_data,  name="vehicle"),
    path('city/',get_cities_data, name="city"),
    path('transferhistory/',get_transfer_history)
]