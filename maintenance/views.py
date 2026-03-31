from django.views.generic import ListView, FormView, CreateView
from django.views.generic.base import TemplateView, View
from django.db.models import Sum, Q
from django.urls import reverse_lazy
from django.contrib.messages import add_message, SUCCESS
from maintenance.forms import MaintenanceForm, MaintenanceUpdateForm, RoomForm
from .models import Maintenance, Room
from django.utils import timezone
import json
import datetime
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect


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

        # 선택된 부과년월에 계약이 유효한 호실만 처리
        valid_rooms = Room.objects.filter(
            contract_start_date__lte=date
        ).filter(
            Q(contract_end_date__isnull=True) | Q(contract_end_date__gte=date)
        ).order_by('number')

        for room in valid_rooms:
            charge = form.cleaned_data.get(f'charge_{room.id}')
            rent = form.cleaned_data.get(f'rent_{room.id}')
            if charge or rent:  # 관리비 또는 임차료가 입력된 경우에만 생성
                Maintenance.objects.create(
                    room=room,
                    date=date,
                    charge=charge or 0,
                    rent=rent or 0,
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
        
        totals = queryset.aggregate(
            total_charge=Sum('charge'),
            total_rent=Sum('rent')
        )
        context.update({
            'available_years': available_years,
            'months': months,
            'selected_year': selected_year,
            'selected_month': selected_month,
            'total_charge': totals['total_charge'] or 0,
            'total_rent': totals['total_rent'] or 0,
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
        total_rent = 0
        monthly_totals = [0] * 12
        monthly_rent_totals = [0] * 12

        for room in active_rooms:
            monthly_charges = []
            monthly_rents = []
            room_charge_total = 0
            room_rent_total = 0

            for month in range(1, 13):
                agg = Maintenance.objects.filter(
                    room=room,
                    date__year=selected_year,
                    date__month=month
                ).aggregate(c=Sum('charge'), r=Sum('rent'))
                charge = agg['c'] or 0
                rent = agg['r'] or 0

                monthly_charges.append(charge)
                monthly_rents.append(rent)
                room_charge_total += charge
                room_rent_total += rent
                monthly_totals[month-1] += charge
                monthly_rent_totals[month-1] += rent

            yearly_data.append({
                'room': room.number,
                'monthly_charges': monthly_charges,
                'monthly_rents': monthly_rents,
                'charge_total': room_charge_total,
                'rent_total': room_rent_total,
                'total': room_charge_total + room_rent_total,
            })
            total_charge += room_charge_total
            total_rent += room_rent_total

        # JSON 직렬화를 위한 데이터 준비 (차트용: 관리비만)
        yearly_data_json = json.dumps(yearly_data, cls=DjangoJSONEncoder)

        monthly_grand_totals = [monthly_totals[i] + monthly_rent_totals[i] for i in range(12)]

        context.update({
            'year': selected_year,
            'selected_year': selected_year,
            'available_years': available_years,
            'months': range(1, 13),
            'yearly_data': yearly_data,
            'yearly_data_json': yearly_data_json,
            'monthly_totals': monthly_totals,
            'monthly_rent_totals': monthly_rent_totals,
            'monthly_grand_totals': monthly_grand_totals,
            'total_charge': total_charge,
            'total_rent': total_rent,
            'grand_total': total_charge + total_rent,
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


class MaintenanceMarkPaidView(LoginRequiredMixin, View):
    def post(self, request, pk):
        maintenance = get_object_or_404(Maintenance, pk=pk)
        date_paid_str = request.POST.get('date_paid', '')
        try:
            maintenance.date_paid = datetime.date.fromisoformat(date_paid_str)
            maintenance.save()
            messages.success(request, f'{maintenance.room.number}호 납부 처리되었습니다.')
        except (ValueError, TypeError):
            messages.error(request, '올바른 날짜를 입력해주세요.')
        return redirect(
            reverse('maintenance:monthly_report')
            + f'?year={maintenance.date.year}&month={maintenance.date.month}'
        )


class MaintenanceCancelPaidView(LoginRequiredMixin, View):
    def post(self, request, pk):
        maintenance = get_object_or_404(Maintenance, pk=pk)
        year, month = maintenance.date.year, maintenance.date.month
        maintenance.date_paid = None
        maintenance.save()
        messages.success(request, f'{maintenance.room.number}호 납부가 취소되었습니다.')
        return redirect(
            reverse('maintenance:monthly_report')
            + f'?year={year}&month={month}'
        )


class RoomListView(LoginRequiredMixin, ListView):
    model = Room
    template_name = 'maintenance/room_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_rooms'] = Room.objects.filter(is_active=True).order_by('number')
        context['inactive_rooms'] = Room.objects.filter(is_active=False).order_by('number')
        return context


class RoomCreateView(LoginRequiredMixin, CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'maintenance/room_form.html'
    success_url = reverse_lazy('maintenance:room_list')

    def form_valid(self, form):
        messages.success(self.request, f'{form.instance.number}호가 추가되었습니다.')
        return super().form_valid(form)


class RoomUpdateView(LoginRequiredMixin, UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'maintenance/room_form.html'
    success_url = reverse_lazy('maintenance:room_list')

    def form_valid(self, form):
        messages.success(self.request, f'{form.instance.number}호 정보가 수정되었습니다.')
        return super().form_valid(form)