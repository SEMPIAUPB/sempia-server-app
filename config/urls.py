from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from .views import DKTProxyView, TutoringProxyView, InitDBView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/exercises/', include('exercises.urls')),
    path('api/v1/submissions/', include('submissions.urls')),
    path('api/v1/gamification/', include('gamification.urls')),
    path('api/v1/skills/', include('skills.urls')),
    path('api/v1/ai/dkt/estimate', DKTProxyView.as_view(), name='ai_dkt_proxy'),
    path('api/v1/ai/tutoring/hint', TutoringProxyView.as_view(), name='ai_tutoring_proxy'),
    path('api/v1/initdb/', InitDBView.as_view()),
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
