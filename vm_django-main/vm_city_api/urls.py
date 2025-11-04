from django.urls import  path
from .views import IssueCreateAPIView, SyncIssuePartsView


urlpatterns = [
    path('issue/', IssueCreateAPIView.as_view(), name="firebase"),
    path('sync-issue-parts/', SyncIssuePartsView.as_view(), name='sync-issue-parts'),
]