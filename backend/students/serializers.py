from rest_framework import serializers

from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    """Converts Student objects to/from JSON and validates incoming data.

    Server-side validation runs here regardless of what the browser checked,
    so the API stays safe even if it is called directly from Postman.
    """

    department_display = serializers.CharField(
        source="get_department_display", read_only=True
    )

    class Meta:
        model = Student
        fields = [
            "id",
            "roll_number",
            "full_name",
            "email",
            "phone",
            "department",
            "department_display",
            "year_of_study",
            "cgpa",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "roll_number": {
                "error_messages": {
                    "unique": "A student with this roll number already exists."
                }
            },
            "email": {
                "error_messages": {
                    "unique": "A student with this email already exists."
                }
            },
        }

    def validate_full_name(self, value):
        name = value.strip()
        if len(name) < 3:
            raise serializers.ValidationError(
                "Full name must be at least 3 characters long."
            )
        if not all(ch.isalpha() or ch in " .'-" for ch in name):
            raise serializers.ValidationError(
                "Full name may contain letters, spaces, apostrophes, dots and hyphens only."
            )
        return name

    def validate_roll_number(self, value):
        return value.strip().upper()

    def validate_email(self, value):
        return value.strip().lower()

    def validate_cgpa(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError("CGPA must be between 0 and 10.")
        return value

    def validate(self, attrs):
        # Cross-field rule: a first-year student cannot already have a
        # perfect CGPA recorded before any results are published.
        year = attrs.get("year_of_study", getattr(self.instance, "year_of_study", None))
        cgpa = attrs.get("cgpa", getattr(self.instance, "cgpa", None))
        if year == 1 and cgpa is not None and cgpa > 10:
            raise serializers.ValidationError(
                {"cgpa": "CGPA cannot exceed 10 for a first-year student."}
            )
        return attrs
