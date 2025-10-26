from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve

class GlobalLoginRequiredMiddleware:
    """
    全URLに対してログイン必須にするミドルウェア。
    PUBLIC_PATHS に含まれるURLは例外。
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 現在のパスを取得
        path = request.path_info

        # PUBLIC_PATHS に含まれていない場合、未認証ならリダイレクト
        if not request.user.is_authenticated:
            # PUBLIC_PATHS の先頭に '/' がない場合も対応
            public_paths = [p if p.startswith('/') else '/' + p for p in getattr(settings, 'PUBLIC_PATHS', [])]
            if not any(path.startswith(p) for p in public_paths):
                return redirect(settings.LOGIN_URL)

        response = self.get_response(request)
        return response
