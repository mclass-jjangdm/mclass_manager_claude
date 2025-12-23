from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, F, Q, Value, OuterRef, Subquery
from django.db.models.functions import Coalesce
from students.models import Student
from payment.models import Payment, PaymentHistory

def dashboard(request):
    search_query = request.GET.get('search', '').strip()

    # 학생 쿼리셋 생성
    students = Student.objects.all()

    # 검색 적용
    if search_query:
        students = students.filter(name__icontains=search_query)

    students = students.order_by('name')

    # 전체 통계 계산
    total_students = students.count()

    # 페이지네이션 적용
    paginator = Paginator(students, 20)  # 한 페이지당 20명
    page = request.GET.get('page')

    try:
        students_page = paginator.page(page)
    except PageNotAnInteger:
        students_page = paginator.page(1)
    except EmptyPage:
        students_page = paginator.page(paginator.num_pages)

    # 현재 페이지 범위 계산
    current_page = students_page.number
    total_pages = paginator.num_pages
    page_range = range(max(1, current_page - 2),
                      min(total_pages + 1, current_page + 3))

    context = {
        'students': students_page,
        'search_query': search_query,
        'total_students': total_students,
        'total_unpaid': 0,
        'page_range': page_range,
        'total_pages': total_pages,
        'current_page': current_page
    }

    return render(request, 'payment/dashboard.html', context)


def student_detail(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    return render(request, 'payment/student_detail.html', {
        'student': student,
        'unpaid_books': [],
    })