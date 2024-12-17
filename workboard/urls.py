from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

from .views import WorkBoardViewSet, TaskListViewSet, TaskViewSet, CommentViewSet
from django.urls import path,include
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'workboards', WorkBoardViewSet)
router.register(r'tasklists', TaskListViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'tasks/(?P<task_id>\d+)/comments', CommentViewSet, basename='comment')  # Đăng ký URL





urlpatterns = [
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)), 
    path('api/tasks/<int:task_id>/attachments/', views.attach_file_to_task, name='add_attachment_to_task'),
    path('api/tasks/<int:task_id>/send-notification/', views.send_task_notification_email, name='send_task_notification_email'),



    
]