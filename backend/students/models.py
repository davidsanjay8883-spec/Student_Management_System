from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models


class Student(models.Model):
    """A single student record — the entity this application manages."""

    DEPARTMENT_CHOICES = [
        ("CSE", "Computer Science and Engineering"),
        ("IT", "Information Technology"),
        ("ECE", "Electronics and Communication"),
        ("EEE", "Electrical and Electronics"),
        ("MECH", "Mechanical Engineering"),
        ("CIVIL", "Civil Engineering"),
    ]

    roll_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z0-9/-]+$",
                message="Roll number may contain letters, digits, - and / only.",
            )
        ],
        help_text="Unique roll number, e.g. 21CSE045",
    )
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=10,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\d{10}$",
                message="Phone number must be exactly 10 digits.",
            )
        ],
    )
    department = models.CharField(max_length=10, choices=DEPARTMENT_CHOICES)
    year_of_study = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="1 to 4",
    )
    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="0.00 to 10.00",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["roll_number"]
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.roll_number} — {self.full_name}"

    def save(self, *args, **kwargs):
        # Keep stored values tidy and case-consistent.
        self.roll_number = self.roll_number.strip().upper()
        self.email = self.email.strip().lower()
        self.full_name = self.full_name.strip()
        super().save(*args, **kwargs)
