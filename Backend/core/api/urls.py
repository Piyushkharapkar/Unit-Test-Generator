# api/urls.py
from django.urls import path, re_path
from . import views

urlpatterns = [
    # GitHub OAuth endpoints
    path('github/login/', views.github_login, name='github-login'),
    path('github/token/', views.get_access_token, name='get-access-token'),

    # GitHub API endpoints
    path('repos/', views.list_repos, name='list-repos'),
    path('files/<str:owner>/<str:repo>/', views.list_files, name='list-files'),
    re_path(r'^files/(?P<owner>[^/]+)/(?P<repo>[^/]+)/(?P<file_path>.*)$', views.get_file_content, name='get-file-content'),

    # Gemini AI endpoints
    path('generate/summaries/', views.generate_summaries, name='generate-summaries'),
    path('generate/code/', views.generate_code, name='generate-code'),
]