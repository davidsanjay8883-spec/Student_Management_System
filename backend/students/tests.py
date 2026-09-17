from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Student

VALID_PAYLOAD = {
    "roll_number": "21CSE045",
    "full_name": "Anitha Ramesh",
    "email": "anitha.r@example.edu",
    "phone": "9876543210",
    "department": "CSE",
    "year_of_study": 3,
    "cgpa": "8.75",
}


class StudentCrudTests(APITestCase):
    def setUp(self):
        self.list_url = reverse("student-list")

    def detail_url(self, pk):
        return reverse("student-detail", args=[pk])

    # --- Create -----------------------------------------------------------
    def test_create_with_valid_data(self):
        response = self.client.post(self.list_url, VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(), 1)

    def test_create_rejects_missing_required_field(self):
        payload = {**VALID_PAYLOAD}
        payload.pop("full_name")
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("full_name", response.data["errors"])

    def test_create_rejects_invalid_email(self):
        payload = {**VALID_PAYLOAD, "email": "not-an-email"}
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data["errors"])

    def test_create_rejects_duplicate_roll_number(self):
        self.client.post(self.list_url, VALID_PAYLOAD, format="json")
        duplicate = {**VALID_PAYLOAD, "email": "someone.else@example.edu"}
        response = self.client.post(self.list_url, duplicate, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("roll_number", response.data["errors"])

    def test_create_rejects_cgpa_above_ten(self):
        payload = {**VALID_PAYLOAD, "cgpa": "11.50"}
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rejects_year_out_of_range(self):
        payload = {**VALID_PAYLOAD, "year_of_study": 7}
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Read -------------------------------------------------------------
    def test_read_all_on_empty_database(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_read_all_returns_records(self):
        self.client.post(self.list_url, VALID_PAYLOAD, format="json")
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 1)

    def test_read_one(self):
        created = self.client.post(self.list_url, VALID_PAYLOAD, format="json")
        response = self.client.get(self.detail_url(created.data["id"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["roll_number"], "21CSE045")

    def test_read_one_with_invalid_id_returns_404(self):
        response = self.client.get(self.detail_url(9999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_filters_results(self):
        self.client.post(self.list_url, VALID_PAYLOAD, format="json")
        self.client.post(
            self.list_url,
            {
                **VALID_PAYLOAD,
                "roll_number": "21IT012",
                "email": "bala.k@example.edu",
                "full_name": "Bala Krishnan",
                "department": "IT",
            },
            format="json",
        )
        response = self.client.get(self.list_url, {"search": "Bala"})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["full_name"], "Bala Krishnan")

    # --- Update -----------------------------------------------------------
    def test_update_existing_record(self):
        created = self.client.post(self.list_url, VALID_PAYLOAD, format="json")
        payload = {**VALID_PAYLOAD, "cgpa": "9.10"}
        response = self.client.put(
            self.detail_url(created.data["id"]), payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data["cgpa"]), "9.10")

    def test_partial_update(self):
        created = self.client.post(self.list_url, VALID_PAYLOAD, format="json")
        response = self.client.patch(
            self.detail_url(created.data["id"]),
            {"year_of_study": 4},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["year_of_study"], 4)

    def test_update_with_invalid_id_returns_404(self):
        response = self.client.put(self.detail_url(9999), VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Delete -----------------------------------------------------------
    def test_delete_existing_record(self):
        created = self.client.post(self.list_url, VALID_PAYLOAD, format="json")
        response = self.client.delete(self.detail_url(created.data["id"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Student.objects.count(), 0)

    def test_delete_with_invalid_id_returns_404(self):
        response = self.client.delete(self.detail_url(9999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Stats ------------------------------------------------------------
    def test_stats_endpoint(self):
        self.client.post(self.list_url, VALID_PAYLOAD, format="json")
        response = self.client.get(reverse("student-stats"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_students"], 1)
        self.assertEqual(response.data["average_cgpa"], 8.75)
