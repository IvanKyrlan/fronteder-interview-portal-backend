# core/middleware.py (створіть новий файл)

class PermissionsPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Додаємо заголовок Permissions-Policy
        response['Permissions-Policy'] = 'browsing-topics=(), join-ad-interest-group=(), run-ad-auction=()'

        return response