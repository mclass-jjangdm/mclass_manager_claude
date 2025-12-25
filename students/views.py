from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from .models import Student, School  # Import School model
from .forms import StudentForm, StudentImportForm, BulkSMSForm
import pandas as pd
from django.http import HttpResponse
from .models import Student, StudentFile
import datetime
from common.utils import send_sms


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    success_url = reverse_lazy('students:student_list')
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        queryset = Student.objects.all()
        search_query = self.request.GET.get('search', '')
        show_inactive = self.request.GET.get('show_inactive') == 'on'
        
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        if not show_inactive:
            queryset = queryset.filter(is_active=True)
            
        return queryset.order_by('-is_active', '-first_class_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_inactive'] = self.request.GET.get('show_inactive') == 'on'
        context['search_query'] = self.request.GET.get('search', '')
        return context


class StudentCreateView(LoginRequiredMixin, CreateView):
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:student_list')

    def form_valid(self, form):
        student = form.save(commit=False)
        student.student_id = self.generate_student_id()
        student.save()

        # Add a success message to inform the user about registration
        messages.success(self.request, f"학생 '{student.name}' 등록되었습니다.")

        return redirect('students:student_list')  # Redirect to the list view

    def generate_student_id(self):
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(8)])


def student_detail(request, pk):
    from bookstore.models import BookSale
    from django.utils import timezone

    student = get_object_or_404(Student, pk=pk)

    # 교재 구매 내역 조회
    unpaid_sales = BookSale.objects.filter(student=student, is_paid=False).select_related('book').order_by('-sale_date')
    paid_sales = BookSale.objects.filter(student=student, is_paid=True).select_related('book').order_by('-payment_date')

    # 총 납부 금액 계산
    total_paid = sum(sale.get_total_price() for sale in paid_sales)

    context = {
        'student': student,
        'unpaid_sales': unpaid_sales,
        'paid_sales': paid_sales,
        'total_unpaid': student.unpaid_amount,
        'total_paid': total_paid,
        'today': timezone.now().date(),
    }
    return render(request, 'students/student_detail.html', context)


def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, '학생 정보가 성공적으로 수정되었습니다.')
            return redirect('students:student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/student_form.html', {'form': form})


def student_import(request):
    if request.method == 'POST':
        form = StudentImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = form.cleaned_data['file']
                file_ext = file.name.split('.')[-1].lower()

                # 파일 형식에 따라 적절한 방법으로 읽기
                if file_ext == 'csv':
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)

                # 중복 체크를 위한 카운터 초기화
                new_count = 0
                duplicate_count = 0

                # 데이터프레임의 각 행 처리
                for index, row in df.iterrows():
                    school_name = row.get('school', '').strip()
                    if school_name:
                        school, created = School.objects.get_or_create(name=school_name)
                    else:
                        school = None

                    # 날짜 필드 처리 함수
                    def parse_date(value):
                        if pd.isnull(value):
                            return None
                        elif isinstance(value, (pd.Timestamp, datetime.date, datetime.datetime)):
                            return value.date()
                        elif isinstance(value, str):
                            for fmt in ('%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d'):
                                try:
                                    return datetime.datetime.strptime(value, fmt).date()
                                except ValueError:
                                    continue
                            return None  # 지원되지 않는 형식일 경우
                        else:
                            return None

                    first_class_date = parse_date(row.get('first_class_date'))
                    quit_date = parse_date(row.get('quit_date'))

                    student_data = {
                        'school': school,
                        'grade': row.get('grade'),
                        'phone_number': row.get('phone_number'),
                        'email': row.get('email'),
                        'gender': row.get('gender'),
                        'parent_phone': row.get('parent_phone'),
                        'receipt_number': row.get('receipt_number'),
                        'first_class_date': first_class_date,
                        'quit_date': quit_date,
                        'etc': row.get('etc'),
                        # 필요한 다른 필드 추가
                    }

                    student, created = Student.objects.update_or_create(
                        name=row['name'],
                        defaults=student_data
                    )
                    if created:
                        new_count += 1
                    else:
                        duplicate_count += 1

                messages.success(request, f"{new_count}명 학생이 새로 추가되었고, {duplicate_count}명 학생은 이미 존재하여 업데이트되었습니다.")
                return redirect('students:student_list')
            except Exception as e:
                messages.error(request, f"파일 처리 중 오류가 발생했습니다: {e}")
        else:
            messages.error(request, "폼이 유효하지 않습니다.")
    else:
        form = StudentImportForm()
    return render(request, 'students/student_import.html', {'form': form})


def student_export(request):
    students = Student.objects.all()

    df = pd.DataFrame({
        'name': [student.name for student in students],
        'school': [student.school.name if student.school else '' for student in students],
        'grade': [student.grade for student in students],
        'phone_number': [student.phone_number for student in students],
        'email': [student.email for student in students],
        'gender': [student.get_gender_display() for student in students],
        'parent_phone': [student.parent_phone for student in students],
        'receipt_number': [student.receipt_number for student in students],
        'interview_date': [student.interview_date.strftime('%Y-%m-%d') if student.interview_date else '' for student in students],
        'interview_score': [student.interview_score for student in students],
        'interview_info': [student.interview_info for student in students],
        'first_class_date': [student.first_class_date.strftime('%Y-%m-%d') if student.first_class_date else '' for student in students],
        'quit_date': [student.quit_date.strftime('%Y-%m-%d') if student.quit_date else '' for student in students],
        'etc': [student.etc for student in students]
    })

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="students.xlsx"'
    df.to_excel(response, sheet_name='학생 목록', index=False, engine='xlsxwriter')

    return response

def student_files(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        if 'file' in request.FILES:
            file = request.FILES['file']
            description = request.POST.get('description', '')
            
            student_file = StudentFile(
                student=student,
                file=file,
                file_name=file.name,
                description=description
            )
            student_file.save()
            messages.success(request, '파일이 성공적으로 업로드되었습니다.')
            return redirect('students:student_files', pk=pk)
        
    files = student.files.all()
    context = {
        'student': student,
        'files': files,
    }
    return render(request, 'students/student_files.html', context)

def delete_student_file(request, file_id):
    file = get_object_or_404(StudentFile, id=file_id)
    student_pk = file.student.pk

    if request.method == 'POST':
        file.file.delete()  # 실제 파일 삭제
        file.delete()       # DB 레코드 삭제
        messages.success(request, '파일이 삭제되었습니다.')

    return redirect('students:student_files', pk=student_pk)


@login_required
def bulk_sms_send(request):
    """여러 학생/학부모에게 일괄 문자 발송"""

    if request.method == 'POST':
        form = BulkSMSForm(request.POST)
        if form.is_valid():
            student_ids = form.cleaned_data['student_ids']
            target = form.cleaned_data['target']
            message = form.cleaned_data['message']

            # 선택된 학생들 조회
            students = Student.objects.filter(pk__in=student_ids)

            success_count = 0
            fail_messages = []

            for student in students:
                # 학생에게 발송
                if target in ['student', 'both'] and student.phone_number:
                    phone = student.phone_number.replace('-', '').strip()
                    is_success, msg = send_sms(phone, message)
                    if is_success:
                        success_count += 1
                    else:
                        fail_messages.append(f"{student.name}(학생): {msg}")

                # 학부모에게 발송
                if target in ['parent', 'both'] and student.parent_phone:
                    phone = student.parent_phone.replace('-', '').strip()
                    is_success, msg = send_sms(phone, message)
                    if is_success:
                        success_count += 1
                    else:
                        fail_messages.append(f"{student.name}(학부모): {msg}")

            # 결과 메시지 처리
            if success_count > 0:
                messages.success(request, f"{success_count}건의 문자를 발송했습니다.")

            if fail_messages:
                for f_msg in fail_messages[:10]:  # 최대 10개까지만 표시
                    messages.error(request, f_msg)
                if len(fail_messages) > 10:
                    messages.error(request, f"외 {len(fail_messages) - 10}건의 발송 실패")

            return redirect('students:student_list')
    else:
        # GET 요청: 선택된 학생 ID들을 가져옴
        student_ids = request.GET.get('student_ids', '')
        if not student_ids:
            messages.error(request, '발송 대상 학생을 선택해주세요.')
            return redirect('students:student_list')

        # 선택된 학생들 조회
        id_list = [int(id.strip()) for id in student_ids.split(',') if id.strip()]
        students = Student.objects.filter(pk__in=id_list)

        form = BulkSMSForm(initial={'student_ids': student_ids})

    return render(request, 'students/bulk_sms_form.html', {
        'form': form,
        'students': students,
    })


@login_required
def student_send_email(request, pk):
    """학생에게 이메일 발송"""
    from django.core.mail import EmailMessage
    from django.conf import settings
    from .forms import StudentEmailForm

    student = get_object_or_404(Student, pk=pk)

    if not student.email:
        messages.error(request, '해당 학생의 이메일 주소가 등록되어 있지 않습니다.')
        return redirect('students:student_detail', pk=pk)

    if request.method == 'POST':
        form = StudentEmailForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # 발신자 이메일 설정
            from_email = settings.DEFAULT_FROM_EMAIL if request.user.username == 'admin' else settings.EMAIL_HOST_USER

            try:
                # EmailMessage 객체 생성
                email = EmailMessage(
                    subject=subject,
                    body=message,
                    from_email=from_email,
                    to=[student.email],
                )

                # 첨부파일 처리
                files = request.FILES.getlist('attachments')
                for file in files:
                    email.attach(file.name, file.read(), file.content_type)

                # 이메일 전송
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f'Sending email to {student.email} from {from_email}')

                result = email.send(fail_silently=False)

                logger.info(f'Email send result: {result}')

                messages.success(request, f'{student.name} 학생에게 이메일을 성공적으로 발송했습니다.')
                return redirect('students:student_detail', pk=pk)
            except Exception as e:
                import logging
                import traceback
                logger = logging.getLogger(__name__)
                logger.error(f'Email sending failed: {str(e)}')
                logger.error(traceback.format_exc())
                messages.error(request, f'이메일 발송 중 오류가 발생했습니다: {str(e)}')
    else:
        form = StudentEmailForm()

    context = {
        'form': form,
        'student': student,
    }
    return render(request, 'students/student_email_form.html', context)


@login_required
def student_send_sms(request, pk):
    """학생에게 문자 발송"""
    from .forms import StudentSMSForm
    import requests

    student = get_object_or_404(Student, pk=pk)

    if not student.phone_number:
        messages.error(request, '해당 학생의 전화번호가 등록되어 있지 않습니다.')
        return redirect('students:student_detail', pk=pk)

    if request.method == 'POST':
        form = StudentSMSForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']

            try:
                # Aligo SMS API 설정
                from django.conf import settings

                sms_url = 'https://apis.aligo.in/send/'
                sms_data = {
                    'key': settings.SMS_API_KEY,
                    'user_id': settings.SMS_USER_ID,
                    'sender': settings.SMS_SENDER_NUMBER,
                    'receiver': student.phone_number,
                    'msg': message,
                    'msg_type': 'LMS' if len(message.encode('euc-kr')) > 90 else 'SMS',
                    'title': '엠클래스' if len(message.encode('euc-kr')) > 90 else '',
                }

                response = requests.post(sms_url, data=sms_data)
                result = response.json()

                if result.get('result_code') == '1':
                    messages.success(request, f'{student.name} 학생에게 문자를 성공적으로 발송했습니다.')
                else:
                    messages.error(request, f'문자 발송 실패: {result.get("message", "알 수 없는 오류")}')

                return redirect('students:student_detail', pk=pk)
            except Exception as e:
                import logging
                import traceback
                logger = logging.getLogger(__name__)
                logger.error(f'SMS sending failed: {str(e)}')
                logger.error(traceback.format_exc())
                messages.error(request, f'문자 발송 중 오류가 발생했습니다: {str(e)}')
    else:
        form = StudentSMSForm()

    context = {
        'form': form,
        'student': student,
    }
    return render(request, 'students/student_sms_form.html', context)


@login_required
def student_send_sms_parent(request, pk):
    """부모님에게 문자 발송"""
    from .forms import StudentSMSForm
    import requests

    student = get_object_or_404(Student, pk=pk)

    if not student.parent_phone:
        messages.error(request, '해당 학생의 부모님 전화번호가 등록되어 있지 않습니다.')
        return redirect('students:student_detail', pk=pk)

    if request.method == 'POST':
        form = StudentSMSForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']

            try:
                # Aligo SMS API 설정
                from django.conf import settings

                sms_url = 'https://apis.aligo.in/send/'
                sms_data = {
                    'key': settings.SMS_API_KEY,
                    'user_id': settings.SMS_USER_ID,
                    'sender': settings.SMS_SENDER_NUMBER,
                    'receiver': student.parent_phone,
                    'msg': message,
                    'msg_type': 'LMS' if len(message.encode('euc-kr')) > 90 else 'SMS',
                    'title': '엠클래스' if len(message.encode('euc-kr')) > 90 else '',
                }

                response = requests.post(sms_url, data=sms_data)
                result = response.json()

                if result.get('result_code') == '1':
                    messages.success(request, f'{student.name} 학생 부모님에게 문자를 성공적으로 발송했습니다.')
                else:
                    messages.error(request, f'문자 발송 실패: {result.get("message", "알 수 없는 오류")}')

                return redirect('students:student_detail', pk=pk)
            except Exception as e:
                import logging
                import traceback
                logger = logging.getLogger(__name__)
                logger.error(f'SMS sending failed: {str(e)}')
                logger.error(traceback.format_exc())
                messages.error(request, f'문자 발송 중 오류가 발생했습니다: {str(e)}')
    else:
        form = StudentSMSForm()

    context = {
        'form': form,
        'student': student,
        'is_parent': True,  # 부모님에게 보내는 것임을 표시
    }
    return render(request, 'students/student_sms_form.html', context)