from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # 로그인된 사용자는 대시보드를 보여줌
            self.template_name = 'dashboard.html'
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # 로그인된 사용자를 위한 추가 컨텍스트
            # 필요한 경우 여기에 데이터 추가
            pass
        return context