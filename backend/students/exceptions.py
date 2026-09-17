"""Uniform error responses for the whole API.

Without this, DRF returns several different error shapes. The frontend
only has to understand one format:

    {"success": false, "message": "...", "errors": {...}}
"""

from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        # Anything DRF did not recognise — most often a database problem.
        if isinstance(exc, IntegrityError):
            return Response(
                {
                    "success": False,
                    "message": "That value conflicts with an existing record.",
                    "errors": {"detail": str(exc)},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None

    detail = response.data
    if isinstance(detail, dict) and "detail" in detail:
        message = str(detail["detail"])
        errors = {}
    else:
        message = "The request could not be processed. Check the fields below."
        errors = detail

    response.data = {
        "success": False,
        "message": message,
        "errors": errors,
    }
    return response
