from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, F, Q, Value, OuterRef, Subquery
from django.db.models.functions import Coalesce
from students.models import Student
from bookstore.models import BookDistribution, BookStock
from payment.models import BookPayment, Payment, PaymentHistory

def dashboard(request):
    search_query = request.GET.get('search', '').strip()
    
    # BookDistribution 데이터 확인
    print("\n=== 마이그레이션된 데이터 확인 ===")
    all_distributions = BookDistribution.objects.select_related(
        'student', 'book_stock__book'
    ).order_by('-sold_date')
    
    print(f"총 배부 기록 수: {all_distributions.count()}")
    for dist in all_distributions[:5]:  # 처음 5개만 출력
        print(f"학생: {dist.student.name}")
        print(f"교재: {dist.book_stock.book.name}")
        print(f"판매일: {dist.sold_date}")
        print(f"수량: {dist.quantity}")
        print(f"판매가: {dist.book_stock.selling_price}")
        print("---")

    # BookPayment 데이터 확인
    print("\n=== BookPayment 데이터 확인 ===")
    all_payments = BookPayment.objects.all()
    print(f"총 결제 기록 수: {all_payments.count()}")
    for payment in all_payments[:5]:
        print(f"학생: {payment.payment.student.name}")
        print(f"교재: {payment.book_distribution.book_stock.book.name}")
        print(f"원래가격: {payment.original_price}")
        print(f"할인가격: {payment.discounted_price}")
        print("---")

    # 각 학생별 미납 금액 계산을 위한 서브쿼리
    student_distributions = BookDistribution.objects.filter(
        student=OuterRef('pk')
    ).values('student').annotate(
        total=Sum(F('book_stock__selling_price') * F('quantity'))
    ).values('total')

    student_payments = BookPayment.objects.filter(
        payment__student=OuterRef('pk')
    ).values('payment__student').annotate(
        total=Sum('discounted_price')
    ).values('total')

    # 학생 쿼리셋 생성
    students = Student.objects.annotate(
        total_distribution=Coalesce(Subquery(student_distributions), 0),
        total_payment=Coalesce(Subquery(student_payments), 0),
        unpaid_amount=F('total_distribution') - F('total_payment')
    )
    
    # 검색 적용
    if search_query:
        students = students.filter(name__icontains=search_query)
    else:
        students = students.filter(unpaid_amount__gt=0)
    
    students = students.order_by('name')
    
    # 전체 통계 계산
    total_students = students.count()
    total_unpaid = students.aggregate(total=Sum('unpaid_amount'))['total'] or 0
    
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

    # 디버깅을 위한 출력
    print("\n=== 전체 학생 목록 및 미납금액 ===")
    for student in students:
        print(f"학생: {student.name}")
        print(f"총 배부금액: {student.total_distribution}")
        print(f"총 결제금액: {student.total_payment}")
        print(f"미납액: {student.unpaid_amount}")
        print("---")
    
    context = {
        'students': students_page,
        'search_query': search_query,
        'total_students': total_students,
        'total_unpaid': total_unpaid,
        'page_range': page_range,
        'total_pages': total_pages,
        'current_page': current_page
    }
    
    return render(request, 'payment/dashboard.html', context)


def student_detail(request, student_id):
    student = get_object_or_404(Student.objects.annotate(
        unpaid_amount=Sum(
            F('bookdistribution__book_stock__selling_price') * F('bookdistribution__quantity'),
            filter=Q(bookdistribution__bookpayment__payment__isnull=True)
        )
    ), pk=student_id)
    
    unpaid_books = student.get_unpaid_books()
    
    return render(request, 'payment/student_detail.html', {
        'student': student,
        'unpaid_books': unpaid_books,
    })