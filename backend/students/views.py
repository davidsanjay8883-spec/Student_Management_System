from django.db.models import Avg, Q
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Student
from .serializers import StudentSerializer


class StudentViewSet(viewsets.ModelViewSet):
    """All five CRUD endpoints for Student.

    POST   /api/students/       create
    GET    /api/students/       read all (supports ?search= and ?department=)
    GET    /api/students/{id}/  read one
    PUT    /api/students/{id}/  full update
    PATCH  /api/students/{id}/  partial update
    DELETE /api/students/{id}/  delete
    """

    serializer_class = StudentSerializer

    def get_queryset(self):
        queryset = Student.objects.all()
        params = self.request.query_params

        search = params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search)
                | Q(roll_number__icontains=search)
                | Q(email__icontains=search)
            )

        department = params.get("department", "").strip()
        if department:
            queryset = queryset.filter(department__iexact=department)

        year = params.get("year", "").strip()
        if year.isdigit():
            queryset = queryset.filter(year_of_study=int(year))

        ordering = params.get("ordering", "").strip()
        allowed = {
            "roll_number",
            "-roll_number",
            "full_name",
            "-full_name",
            "cgpa",
            "-cgpa",
            "created_at",
            "-created_at",
        }
        if ordering in allowed:
            queryset = queryset.order_by(ordering)

        return queryset

    def destroy(self, request, *args, **kwargs):
        student = self.get_object()
        roll_number = student.roll_number
        student.delete()
        return Response(
            {"detail": f"Student {roll_number} deleted."},
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])
def student_stats(request):
    """Small summary used by the dashboard header."""
    total = Student.objects.count()
    average = Student.objects.aggregate(value=Avg("cgpa"))["value"]
    by_department = {}
    for row in Student.objects.values("department").distinct():
        code = row["department"]
        by_department[code] = Student.objects.filter(department=code).count()

    return Response(
        {
            "total_students": total,
            "average_cgpa": round(float(average), 2) if average is not None else None,
            "by_department": by_department,
        }
    )
