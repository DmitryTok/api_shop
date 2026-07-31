import json

from django.contrib import messages
from django.contrib.admin import AdminSite
from django.shortcuts import redirect
from django.urls import path

from .load_data_to_db import load_data_to_db


class CustomAdminSite(AdminSite):
    index_template = "admin/index.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "run_parser/",
                self.admin_view(self.run_parser),
                name="run_parser",
            )
        ]
        return custom_urls + urls

    def run_parser(self, request):
        try:
            file = request.FILES.get("parser_file")
            if not file:
                messages.warning(request, "Select a file")
                return redirect("admin:index")
            data = json.load(file)
            load_data_to_db(data)
            messages.success(request, "Data loaded successfully")
            return redirect("admin:index")
        except Exception as error:
            messages.error(request, f"An error: {error}, occurred during loading data")
            return redirect("admin:index")
