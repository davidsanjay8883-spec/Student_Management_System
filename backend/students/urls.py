from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StudentViewSet, student_stats

router = DefaultRouter()
router.register(r"students", StudentViewSet, basename="student")

urlpatterns = [
    path("", include(router.urls)),
    path("stats/", student_stats, name="student-stats"),
]
