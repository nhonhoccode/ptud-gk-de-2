from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('tasks/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('task/new/', views.task_create, name='task_create'),
    path('task/<int:pk>/update/', views.task_update, name='task_update'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('task/<int:pk>/complete/', views.task_complete, name='task_complete'),
    path('profile/', views.profile, name='profile'),
    path('logout/', LogoutView.as_view(next_page='landing', http_method_names=['get', 'post']), name='logout'),
] 