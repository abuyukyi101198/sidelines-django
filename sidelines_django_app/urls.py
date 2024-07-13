from django.urls import path
from .views import UserRecordView

app_name = 'api'
urlpatterns = [
    path('users/', UserRecordView.as_view(), name='user-list'),
    path('users/<int:user_id>/', UserRecordView.as_view(), name='user-detail'),
]
