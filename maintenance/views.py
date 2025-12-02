from django.views.generic import ListView, FormView
from django.views.generic.base import TemplateView
from django.db.models import Sum
from django.urls import reverse_lazy
from django.contrib.messages import add_message, SUCCESS
from maintenance.forms import MaintenanceForm, MaintenanceUpdateForm
from .models import Maintenance, Room
from django.utils import timezone
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse
from django.contrib import messages


class MaintenanceCreateView(LoginRequiredMixin, FormView):
    template_name = 'maintenance/maintenance_form.html'
    form_class = MaintenanceForm
    success_url = reverse_lazy('maintenance:create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rooms'] = Room.objects.all().order_by('number')
        return context

    def form_valid(self, form):
        date = form.cleaned_data['date']
        created_count = 0
        
        for room in Room.objects.all().order_by('number'):
            charge = form.cleaned_data.get(f'charge_{room.id}')
            if charge:  # 금액이 입력된 경우에만 생성
                Maintenance.objects.create(
                    room=room,
                    date=date,
                    charge=charge,
                    date_paid=form.cleaned_data.get(f'date_paid_{room.id}'),
                    memo=form.cleaned_data.get(f'memo_{room.id}', '')
                )
                created_count += 1
        
        add_message(
            self.request,
            SUCCESS,
            f'{created_count}개의 관리비가 성공적으로 등록되었습니다.'
        )
        return super().form_valid(form)
    

class MonthlyReportView(LoginRequiredMixin, ListView):
    model = Maintenance
    template_name = 'maintenance/monthly_report.html'
    context_object_name = 'maintenance_list'

    def get_queryset(self):
        year = self.request.GET.get('year', timezone.now().year)
        month = self.request.GET.get('month', timezone.now().month)
        return Maintenance.objects.filter(
            date__year=year,
            date__month=month
        ).order_by('room')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 데이터가 있는 년도만 가져오기
        available_years = [d.year for d in Maintenance.objects
                         .dates('date', 'year', order='DESC')
                         .distinct()]
        
        # 데이터가 있는 경우 가장 최근 년도를, 없으면 현재 년도를 기본값으로
        current_year = available_years[0] if available_years else timezone.now().year
        selected_year = int(self.request.GET.get('year', current_year))
        selected_month = int(self.request.GET.get('month', timezone.now().month))
        
        months = [(i, f"{i}월") for i in range(1, 13)]
        
        queryset = self.get_queryset()
        
        context.update({
            'available_years': available_years,  # year_range 대신 available_years 사용
            'months': months,
            'selected_year': selected_year,
            'selected_month': selected_month,
            'total_charge': queryset.aggregate(Sum('charge'))['charge__sum'] or 0
        })
        return context
    

class YearlyReportView(LoginRequiredMixin, TemplateView):
    template_name = 'maintenance/yearly_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        available_years = [d.year for d in Maintenance.objects
                         .dates('date', 'year', order='DESC')
                         .distinct()]
        
        current_year = available_years[0] if available_years else timezone.now().year
        selected_year = int(self.request.GET.get('year', current_year))
        
        active_rooms = Room.objects.filter(
            maintenance__date__year=selected_year
        ).distinct().order_by('number')

        yearly_data = []
        total_charge = 0
        monthly_totals = [0] * 12

        for room in active_rooms:
            monthly_charges = []
            room_total = 0
            
            for month in range(1, 13):
                charge = Maintenance.objects.filter(
                    room=room,
                    date__year=selected_year,
                    date__month=month
                ).aggregate(Sum('charge'))['charge__sum'] or 0
                
                monthly_charges.append(charge)
                room_total += charge
                monthly_totals[month-1] += charge
            
            yearly_data.append({
                'room': room.number,
                'monthly_charges': monthly_charges,
                'total': room_total
            })
            total_charge += room_total

        # JSON 직렬화를 위한 데이터 준비
        yearly_data_json = json.dumps(yearly_data, cls=DjangoJSONEncoder)

        context.update({
            'year': selected_year,
            'selected_year': selected_year,
            'available_years': available_years,
            'months': range(1, 13),
            'yearly_data': yearly_data,
            'yearly_data_json': yearly_data_json,  # JSON 형식의 데이터 추가
            'monthly_totals': monthly_totals,
            'total_charge': total_charge,
            'grand_total': total_charge
        })
        return context


class MaintenanceUpdateView(LoginRequiredMixin, UpdateView):
    model = Maintenance
    form_class = MaintenanceUpdateForm
    template_name = 'maintenance/maintenance_edit.html'

    def get_success_url(self):
        return reverse('maintenance:monthly_report') + f'?year={self.object.date.year}&month={self.object.date.month}'

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, '관리비 정보가 수정되었습니다.')
        return super().form_valid(form)