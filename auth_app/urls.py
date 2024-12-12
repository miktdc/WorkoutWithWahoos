from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('guest/', views.anonymous_user, name='anonymous_user'),
    path('logout/', views.logout_view, name='logout_view'),
    path('pma_admin_dashboard/', views.pma_admin_dashboard, name='pma_admin_dashboard'),
    path('common_user_dashboard/', views.common_user_dashboard, name='common_user_dashboard'),
    path('common_user_dashboard/create/', views.create_session, name='create_session'),
    path('common_user_dashboard/available/', views.available_sessions, name='available_sessions'),
    path('profile', views.profile, name='profile'),
    path('profile/update', views.update_profile, name='update_profile'),
    path('delete-session/<int:session_id>/', views.delete_session, name='delete_session'),
    path('edit-session/<int:session_id>/', views.edit_session, name='edit_session'),
    path('drop_session/<int:session_id>/', views.drop_session, name='drop_session'),
    path('file-upload/<int:session_id>/', views.file_upload, name = 'file_upload'),
    path('workout-detail/<int:session_id>/', views.workout_detail, name='workout_detail'),
    path('request-enrollment/', views.request_enrollment, name='request_enrollment'),
    path('manage-requests/<int:session_id>/', views.manage_requests, name='manage_requests'),
    path('creator-delete-session/<int:session_id>/', views.creator_delete_session, name='creator_delete_session'),
    path('delete-file/<int:file_id>/', views.delete_file, name='delete_file'),
]