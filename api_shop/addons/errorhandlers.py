from django.http import JsonResponse


def handler_404(request, exception):
    return JsonResponse(
        {
            'error': 'Invalid URL format',
            'message': 'The requested URL was not found on the server. Please check the URL and try again.',
        },
        status=404,
    )


handler404 = 'my_app.views.error_404_view'
