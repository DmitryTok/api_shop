from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

from custom_admin.load_data_to_db import FixtureLoader


def run_fixture_loader_view(request: HttpRequest, app_name: str, model_name: str) -> HttpResponseRedirect:
    try:
        redirect_url = reverse(f"admin:{app_name}_{model_name}_changelist")
    except Exception:
        redirect_url = request.META.get("HTTP_REFERER", "admin:index")
    if request.method == "POST" and request.FILES.get("fixture_file"):
        uploaded_file = request.FILES["fixture_file"]
        try:
            if not uploaded_file:
                raise ValueError()
            fixture_loader = FixtureLoader(file=uploaded_file)
            fixture_loader.load_data_to_db(app_name=app_name, model_name=model_name)
            redirect_url = reverse(f"admin:{app_name}_{model_name}_changelist")
            messages.success(request, f"Data loaded successfully")
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return redirect(redirect_url)
