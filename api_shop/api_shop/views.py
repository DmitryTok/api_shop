from django.shortcuts import redirect
from django.contrib import messages
from addons.load_data_to_db import FixtureLoader


def run_fixture_loader_fixture_view(request):
    if request.method == "POST" and request.FILES.get("fixture_file"):
        uploaded_file = request.FILES["fixture_file"]
        try:
            if not uploaded_file:
                raise ValueError()
            fixture_loader = FixtureLoader(file=uploaded_file)
            fixture_loader.load_data_to_db()
            messages.success(request, f"Data loaded successfully")
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return redirect(request.META.get("HTTP_REFERER", "admin:index"))
