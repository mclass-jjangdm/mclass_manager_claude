# bookstore/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Book, BookStockLog, BookSupplier, BookSale, BookContent, StudentBookProgress
from .forms import BookForm, BookStockLogForm, BookSupplierForm, BookReturnForm, BookSaleForm, BookContentUploadForm
from teachers.models import TeacherStudentAssignment, Teacher
from django.db.models import Q
from django.contrib import messages
import pandas as pd # 엑셀 처리를 위해 필수
import re # ISBN 정리를 위해 필요
from django.utils import timezone
import requests # 외부 API 호출용
from django.http import JsonResponse # JSON 응답용
import urllib3 # SSL 경고 숨기기용
from django.db import transaction # 트랜잭션 필수
from students.models import Student # 학생 모델 참조 필요
from django.core.paginator import Paginator
from subjects.models import Subject
from collections import defaultdict
import json


# SSL 인증서 경고 무시 설정 (터미널이 지저분해지는 것 방지)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def book_list(request):
    """교재 목록 조회 (검색 실패 시 자동 이동 플래그 처리)"""
    query = request.GET.get('q', '')

    # 기본 정렬: 최신순
    books = Book.objects.all().order_by('-created_at')

    is_search_empty = False  # 검색 결과 없음 플래그

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(isbn__icontains=query) |
            Q(author__icontains=query)
        )
        # 검색어는 있는데 결과가 0개인 경우 -> 자동 이동 트리거
        if not books.exists():
            is_search_empty = True

    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'bookstore/book_list.html', {
        'page_obj': page_obj,
        'query': query,
        'is_search_empty': is_search_empty,
    })


def book_create(request):
    """신규 교재 입고 (데이터 유지 기능 강화)"""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            initial_stock = book.stock
            book.stock = 0
            book.save()

            if initial_stock > 0:
                BookStockLog.objects.create(
                    book=book,
                    supplier=book.supplier,
                    quantity=initial_stock,
                    cost_price=book.cost_price,
                    created_at=book.created_at,
                    memo="신규 도서 등록 (초기 재고)"
                )
            messages.success(request, f"'{book.title}' 도서가 등록되었습니다.")
            return redirect('bookstore:book_list')
    else:
        # [핵심] URL 파라미터(?isbn=...&title=...)를 폼 초기값으로 설정
        initial_data = {
            'created_at': timezone.now().date(),      # timezone.localtime(timezone.now()).date(),
            'isbn': request.GET.get('isbn', ''),
            'title': request.GET.get('title', ''),
            'author': request.GET.get('author', ''),
            'publisher': request.GET.get('publisher', ''),
            'original_price': request.GET.get('original_price', ''),
            'cost_price': request.GET.get('cost_price', ''),
            'price': request.GET.get('price', ''),
            'stock': request.GET.get('stock', ''),
            'memo': request.GET.get('memo', ''),
        }

        # supplier_id가 넘어왔다면 처리
        supplier_id = request.GET.get('supplier')
        if supplier_id:
            try:
                initial_data['supplier'] = int(supplier_id)
            except ValueError:
                pass

        form = BookForm(initial=initial_data)

    # 과목을 카테고리별로 그룹화
    subjects = Subject.objects.filter(is_active=True).order_by('subject_code')
    grouped_subjects = defaultdict(list)
    for subject in subjects:
        grouped_subjects[subject.category].append({
            'id': subject.id,
            'name': subject.name,
            'code': subject.subject_code
        })

    # 카테고리 목록 (정렬)
    categories = sorted(grouped_subjects.keys())

    return render(request, 'bookstore/book_form.html', {
        'form': form,
        'title': '📚 신규 교재 등록',
        'grouped_subjects_json': json.dumps(dict(grouped_subjects), ensure_ascii=False),
        'categories': categories,
    })


def book_update(request, pk):
    """교재 정보 수정"""
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('bookstore:book_list')
    else:
        form = BookForm(instance=book)

    # 과목을 카테고리별로 그룹화
    subjects = Subject.objects.filter(is_active=True).order_by('subject_code')
    grouped_subjects = defaultdict(list)
    for subject in subjects:
        grouped_subjects[subject.category].append({
            'id': subject.id,
            'name': subject.name,
            'code': subject.subject_code
        })

    # 카테고리 목록 (정렬)
    categories = sorted(grouped_subjects.keys())

    # 현재 선택된 과목의 카테고리 찾기
    selected_category = None
    if book.subject:
        selected_category = book.subject.category

    return render(request, 'bookstore/book_form.html', {
        'form': form,
        'title': f'교재 정보 수정: {book.title}',
        'grouped_subjects_json': json.dumps(dict(grouped_subjects), ensure_ascii=False),
        'categories': categories,
        'selected_category': selected_category,
    })


def book_delete(request, pk):
    """도서 삭제"""
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('bookstore:book_list')

    # GET 요청 시에는 그냥 목록으로 (혹은 삭제 확인 페이지)
    return redirect('bookstore:book_list')


def book_restock(request, pk):
    """기존 교재 추가 입고 (재고 증가)"""
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        form = BookStockLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.book = book
            log.save()  # 모델 save()에서 재고 증가 및 총액 계산

            messages.success(request, f"'{book.title}' {log.quantity}권이 입고되었습니다.")
            return redirect('bookstore:book_list')
    else:
        # 오늘 날짜를 기본 지급일로 설정
        form = BookStockLogForm(initial={
            'cost_price': book.cost_price,
            'payment_date': timezone.now().date()
        })

    recent_logs = book.stock_logs.all()[:5]

    return render(request, 'bookstore/book_restock.html', {
        'form': form,
        'book': book,
        'recent_logs': recent_logs
    })


def book_detail(request, pk):
    """도서 상세 정보 및 입고 이력 조회"""
    book = get_object_or_404(Book, pk=pk)

    # 해당 도서의 모든 입고 기록을 최신순으로 조회
    stock_logs = book.stock_logs.all().order_by('-created_at')

    # 해당 교재의 판매(지급) 이력 조회
    from bookstore.models import BookSale
    sales = BookSale.objects.filter(book=book).select_related('student').order_by('-sale_date')

    return render(request, 'bookstore/book_detail.html', {
        'book': book,
        'stock_logs': stock_logs,
        'sales': sales
    })


def book_return(request, pk):
    """교재 반품 처리 (재고 감소)"""
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        form = BookReturnForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.quantity = -abs(log.quantity)  # 음수 변환
            log.book = book

            # 재고 체크
            if book.stock + log.quantity < 0:
                messages.error(request, f"재고가 부족합니다. 현재 재고: {book.stock}권, 반품 요청: {abs(log.quantity)}권")
                return redirect('bookstore:book_return', pk=pk)

            log.save()
            messages.warning(request, f"'{book.title}' {abs(log.quantity)}권이 반품 처리되었습니다. (현재 재고: {book.stock}권)")
            return redirect('bookstore:book_list')
    else:
        form = BookReturnForm(initial={
            'cost_price': book.cost_price,

            # [핵심 수정] UTC 시간을 한국 시간(Local Time)으로 변환 후 날짜 추출
            'payment_date': timezone.now().date(),         # timezone.localtime(timezone.now()).date(),
            'memo': '재고 반품'
        })

    recent_logs = book.stock_logs.all()[:5]

    return render(request, 'bookstore/book_return.html', {
        'form': form,
        'book': book,
        'recent_logs': recent_logs
    })


def book_upload(request):
    """엑셀/CSV 파일로 도서 일괄 등록"""
    if request.method == 'POST' and request.FILES.get('upload_file'):
        upload_file = request.FILES['upload_file']
        selected_subject_id = request.POST.get('subject')

        # 선택된 과목 가져오기
        selected_subject = None
        if selected_subject_id:
            try:
                selected_subject = Subject.objects.get(pk=selected_subject_id)
            except Subject.DoesNotExist:
                pass

        try:
            if upload_file.name.endswith('.csv'):
                df = pd.read_csv(upload_file)
            else:
                df = pd.read_excel(upload_file)

            success_count = 0
            skip_count = 0

            for index, row in df.iterrows():
                # 1. 필수값(ISBN, 교재명) 확인
                title = row.get('교재명')
                raw_isbn = str(row.get('ISBN', '')).strip()

                if pd.isna(title) or not raw_isbn:
                    continue

                # 2. ISBN 정리 (하이픈 제거 및 13자리 변환 로직 간소화)
                isbn = re.sub(r'[^0-9X]', '', raw_isbn.upper())

                # 3. 중복 확인 (이미 등록된 ISBN이면 건너뜀)
                if Book.objects.filter(isbn=isbn).exists():
                    skip_count += 1
                    continue

                # 4. 파일에서 과목코드 읽기 (있는 경우)
                subject = selected_subject  # 기본값: 폼에서 선택한 과목
                subject_code = row.get('과목코드')
                if subject_code and not pd.isna(subject_code):
                    subject_code = str(subject_code).strip()
                    try:
                        subject = Subject.objects.get(subject_code=subject_code)
                    except Subject.DoesNotExist:
                        pass  # 과목코드가 없으면 폼에서 선택한 과목 사용

                # 5. 데이터 추출 및 저장
                Book.objects.create(
                    subject=subject,
                    title=title,
                    isbn=isbn,
                    author=row.get('저자', ''),
                    publisher=row.get('출판사', ''),
                    original_price=pd.to_numeric(row.get('정상가격'), errors='coerce') or 0,
                    cost_price=pd.to_numeric(row.get('입고가격'), errors='coerce') or 0,
                    price=pd.to_numeric(row.get('판매가격'), errors='coerce') or 0,
                    stock=pd.to_numeric(row.get('재고'), errors='coerce') or 0,
                )
                success_count += 1

            messages.success(request, f"{success_count}권의 도서가 등록되었습니다. (중복 제외: {skip_count}권)")
            return redirect('bookstore:book_list')

        except Exception as e:
            messages.error(request, f"파일 업로드 중 오류가 발생했습니다: {e}")
            return redirect('bookstore:book_upload')

    # 과목을 카테고리별로 그룹화
    subjects = Subject.objects.filter(is_active=True).order_by('subject_code')
    grouped_subjects = defaultdict(list)
    for subject in subjects:
        grouped_subjects[subject.category].append({
            'id': subject.id,
            'name': subject.name,
            'code': subject.subject_code
        })

    categories = sorted(grouped_subjects.keys())

    return render(request, 'bookstore/book_upload.html', {
        'grouped_subjects_json': json.dumps(dict(grouped_subjects), ensure_ascii=False),
        'categories': categories,
    })


def supplier_list(request):
    """구매처 목록 조회"""
    suppliers = BookSupplier.objects.all().order_by('name')
    return render(request, 'bookstore/supplier_list.html', {'suppliers': suppliers})


def supplier_create(request):
    """새로운 도서 공급처 등록 (등록 후 이전 페이지로 복귀 기능 추가)"""

    # [핵심] URL에 '?next=...'가 있는지 확인 (있다면 그 주소를 저장)
    next_url = request.GET.get('next')

    if request.method == 'POST':
        form = BookSupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f"구매처 '{supplier.name}' 등록이 완료되었습니다.")

            # [핵심] 돌아갈 주소가 있다면 거기로 리다이렉트
            if next_url:
                return redirect(next_url)

            # 없으면 원래대로 목록으로 이동
            return redirect('bookstore:supplier_list')
    else:
        form = BookSupplierForm()

    return render(request, 'bookstore/supplier_form.html', {
        'form': form,
        'title': '새 구매처 등록'
    })


def supplier_update(request, pk):
    """구매처 정보 수정"""
    supplier = get_object_or_404(BookSupplier, pk=pk)
    if request.method == 'POST':
        form = BookSupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('bookstore:supplier_list')
    else:
        form = BookSupplierForm(instance=supplier)

    return render(request, 'bookstore/supplier_form.html', {'form': form, 'title': f'구매처 수정: {supplier.name}'})


def supplier_delete(request, pk):
    """구매처 삭제"""
    supplier = get_object_or_404(BookSupplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, "구매처 정보가 삭제되었습니다.")
        return redirect('bookstore:supplier_list')
    return redirect('bookstore:supplier_list')


def supplier_detail(request, pk):
    """구매처 상세: 지급 대상과 환불 대상을 분리하여 조회"""
    supplier = get_object_or_404(BookSupplier, pk=pk)

    # 1. 지급 대상 (입고: quantity > 0) 이면서 미정산
    unpaid_restocks = BookStockLog.objects.filter(
        supplier=supplier,
        is_paid=False,
        quantity__gt=0
    ).order_by('-created_at')

    # 2. 환불/차감 대상 (반품: quantity < 0) 이면서 미정산
    unpaid_returns = BookStockLog.objects.filter(
        supplier=supplier,
        is_paid=False,
        quantity__lt=0
    ).order_by('-created_at')

    # 지급 완료 내역
    paid_logs = BookStockLog.objects.filter(
        supplier=supplier,
        is_paid=True
    ).order_by('-payment_date', '-created_at')

    # 총액 계산 (각각 계산)
    total_to_pay = sum(log.total_payment for log in unpaid_restocks)
    total_to_refund = sum(log.total_payment for log in unpaid_returns)  # 반품액 합계

    return render(request, 'bookstore/supplier_detail.html', {
        'supplier': supplier,
        'unpaid_restocks': unpaid_restocks,  # 변경
        'unpaid_returns': unpaid_returns,  # 변경
        'paid_logs': paid_logs,
        'total_to_pay': total_to_pay,  # 변경
        'total_to_refund': total_to_refund,  # 변경
        'today': timezone.now().strftime('%Y-%m-%d'),           # timezone.localtime(timezone.now()).strftime('%Y-%m-%d')
    })


# 지급 취소(정산 취소) 뷰
def supplier_payment_cancel(request, pk):
    """선택한 내역의 정산 처리를 취소하고 미지급 상태로 되돌림"""
    supplier = get_object_or_404(BookSupplier, pk=pk)

    if request.method == 'POST':
        # 선택된 로그 ID들 가져오기
        selected_ids = request.POST.getlist('log_ids')

        if selected_ids:
            # 정산 취소 (is_paid=False, payment_date=None)
            updated_count = BookStockLog.objects.filter(
                id__in=selected_ids,
                supplier=supplier
            ).update(is_paid=False, payment_date=None)

            messages.warning(request, f"{updated_count}건의 정산이 취소되었습니다. '미지급 내역'으로 복구되었습니다.")
        else:
            messages.error(request, "취소할 내역을 선택해주세요.")

    return redirect('bookstore:supplier_detail', pk=pk)


def supplier_settle(request, pk):
    """선택한 입고 내역 정산(입금) 처리"""
    supplier = get_object_or_404(BookSupplier, pk=pk)

    if request.method == 'POST':
        # 1. 선택된 로그 ID들 가져오기
        selected_ids = request.POST.getlist('log_ids')
        payment_date = request.POST.get('payment_date')

        if not selected_ids:
            messages.error(request, "정산할 내역을 선택해주세요.")
            return redirect('bookstore:supplier_detail', pk=pk)

        # 2. 업데이트 (정산 완료 처리 + 날짜 기록)
        updated_count = BookStockLog.objects.filter(
            id__in=selected_ids,
            supplier=supplier
        ).update(is_paid=True, payment_date=payment_date)

        messages.success(request, f"{updated_count}건의 내역이 정산 처리되었습니다. (지급일: {payment_date})")

    return redirect('bookstore:supplier_detail', pk=pk)


def search_book_api(request):
    """국립중앙도서관 API 조회 (Key 수정 및 데이터 정제)"""
    isbn = request.GET.get('isbn')

    # API
    API_KEY = "a36e5ab3c6a0d4359b7fffbca22dd34734921dea812fcdf66f711abf3ee10aae"

    if not isbn:
        return JsonResponse({'error': 'ISBN이 제공되지 않았습니다.'}, status=400)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    url = "https://www.nl.go.kr/NL/search/openApi/search.do"
    params = {
        'key': API_KEY,
        'kwd': isbn,
        'detailSearch': 'true',
        'f1': 'isbn',
        'category': '도서',
        'apiType': 'json'
    }

    try:
        # 타임아웃은 안전하게 5초
        response = requests.get(url, params=params, headers=headers, verify=False, timeout=5)

        if response.status_code != 200:
            return JsonResponse({'error': 'API 서버 접속 실패'}, status=500)

        data = response.json()

        # total이 문자열일 수도, 숫자일 수도 있어서 안전하게 변환
        total = int(data.get('total', 0))

        if total > 0:
            # result 키 사용
            items = data.get('result', [])

            if items:
                item = items[0]

                # [핵심 수정] 로그에 찍힌 정확한 Key 이름(camelCase) 사용
                title = item.get('titleInfo', '')
                author_raw = item.get('authorInfo', '')
                publisher = item.get('pubInfo', '')

                # 가격 정보는 로그에 없었으므로 일단 '0'으로 두거나 priceInfo 시도
                price_raw = item.get('priceInfo', '0')

                # [데이터 정제 1] 저자 정보에서 '지은이:' 제거
                # 예: "지은이: 유시민" -> "유시민"
                author = author_raw.replace('지은이:', '').strip()

                # [데이터 정제 2] 가격 정보에서 숫자만 추출
                price = str(price_raw).replace('원', '').replace(',', '').strip()
                if not price or not price.isdigit():
                    price = '0'

                result = {
                    'title': title,
                    'author': author,
                    'publisher': publisher,
                    'price': price,
                }
                print(f"최종 데이터 매핑 성공: {result}")
                return JsonResponse(result)
            else:
                return JsonResponse({'error': '도서 정보 리스트가 비어있습니다.'}, status=404)
        else:
            return JsonResponse({'error': '해당 도서 정보가 없습니다.'}, status=404)

    except Exception as e:
        print(f"에러 발생: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def book_sale_create(request, student_pk):
    """학생에게 교재 판매(분배) 및 재고/미납금 처리"""
    student = get_object_or_404(Student, pk=student_pk)

    if request.method == 'POST':
        form = BookSaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.student = student
            book = sale.book

            # 1. 재고 재확인
            if book.stock < sale.quantity:
                messages.error(request, f"재고가 부족합니다. (현재 재고: {book.stock}권)")
                return redirect('students:student_detail', pk=student.pk)

            try:
                with transaction.atomic():
                    # 2. 판매 날짜 설정
                    if sale.is_paid:
                        sale.payment_date = timezone.now().date()       #timezone.localtime(timezone.now()).date()
                    sale.save()

                    # 3. 재고 차감
                    book.stock -= sale.quantity
                    book.save()

                    # 4. 학생 미납금(unpaid_amount) 증가 (미납인 경우만)
                    if not sale.is_paid:
                        total_price = sale.price * sale.quantity
                        # 이제 모델에 필드가 있으므로 에러가 안 납니다!
                        student.unpaid_amount += total_price
                        student.save()

                    # 5. 교재 목차가 있는 경우 진도 레코드 자동 생성
                    progress_count = sale.create_progress_records()

                    msg = f"'{book.title}' {sale.quantity}권이 지급되었습니다."
                    if progress_count > 0:
                        msg += f" (진도 항목 {progress_count}개 생성)"
                    if not sale.is_paid:
                        msg += " (비용이 미납금에 합산되었습니다)"
                    messages.success(request, msg)

            except Exception as e:
                messages.error(request, f"처리 중 오류 발생: {e}")

            return redirect('students:student_detail', pk=student.pk)
    else:
        # 초기값에 오늘 날짜(한국 시간) 넣어주기
        form = BookSaleForm(initial={
            'sale_date': timezone.now().date()      #timezone.localtime(timezone.now()).date()
        })

    return render(request, 'bookstore/book_sale_form.html', {
        'form': form,
        'student': student
    })


def book_sale_settle(request, pk):
    """개별 교재 판매 건 납부(정산) 처리 (디버깅 추가)"""
    print(f"[디버깅] 납부 처리 요청 받음 - Sale ID: {pk}")
    sale = get_object_or_404(BookSale, pk=pk)

    if request.method == 'POST':
        print("[디버깅] POST 요청 확인.")
        payment_date = request.POST.get('payment_date')
        print(f"[디버깅] 제출된 납부일: {payment_date}")

        if not payment_date:
            print("[디버깅] 납부일이 누락되었습니다.")
            messages.error(request, "납부일이 입력되지 않았습니다.")
            return redirect('students:student_detail', pk=sale.student.pk)

        try:
            from datetime import datetime

            with transaction.atomic():
                # 1. 판매 기록 업데이트 (결제 완료)
                sale.is_paid = True
                # 날짜 문자열을 date 객체로 변환 (YYYY-MM-DD)
                sale.payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
                sale.save()
                print("[디버깅] 판매 기록 업데이트 완료 (결제 상태 변경).")

                # 2. 학생 미납금 차감
                total_price = sale.get_total_price()
                sale.student.unpaid_amount -= total_price
                sale.student.save()
                print(f"[디버깅] 학생 미납금 차감 완료. (남은 미납액: {sale.student.unpaid_amount})")

                messages.success(request, f"'{sale.book.title}' 납부 처리가 완료되었습니다.")

        except Exception as e:
            print(f"[디버깅] 처리 중 치명적 에러 발생: {e}")
            import traceback
            print(traceback.format_exc())  # 에러 상세 내용 출력
            messages.error(request, f"처리 중 오류 발생: {e}")

    else:
        print("[디버깅] POST 요청이 아닙니다.")

    return redirect('students:student_detail', pk=sale.student.pk)


def book_sale_update(request, pk):
    """판매 기록 수정"""
    sale = get_object_or_404(BookSale, pk=pk)
    student = sale.student
    original_quantity = sale.quantity
    original_book = sale.book
    original_is_paid = sale.is_paid
    original_total = sale.get_total_price()

    if request.method == 'POST':
        form = BookSaleForm(request.POST, instance=sale)
        if form.is_valid():
            updated_sale = form.save(commit=False)

            try:
                with transaction.atomic():
                    # 1. 교재가 변경되었거나 수량이 변경된 경우 재고 조정
                    if original_book != updated_sale.book or original_quantity != updated_sale.quantity:
                        # 원래 교재 재고 복원
                        original_book.stock += original_quantity
                        original_book.save()

                        # 새 교재 재고 차감
                        new_book = updated_sale.book
                        if new_book.stock < updated_sale.quantity:
                            messages.error(request, f"재고가 부족합니다. (현재 재고: {new_book.stock}권)")
                            return redirect('bookstore:book_sale_update', pk=pk)

                        new_book.stock -= updated_sale.quantity
                        new_book.save()

                    # 2. 납부 상태 변경 처리
                    new_is_paid = updated_sale.is_paid
                    new_total = updated_sale.get_total_price()

                    # 미납 → 납부 완료
                    if not original_is_paid and new_is_paid:
                        updated_sale.payment_date = timezone.now().date()
                        student.unpaid_amount -= new_total
                    # 납부 완료 → 미납
                    elif original_is_paid and not new_is_paid:
                        updated_sale.payment_date = None
                        student.unpaid_amount += new_total
                    # 미납 상태 유지, 금액만 변경
                    elif not original_is_paid and not new_is_paid:
                        student.unpaid_amount = student.unpaid_amount - original_total + new_total
                    # 납부 완료 상태 유지 (금액 변경은 미납금에 영향 없음)

                    student.save()
                    updated_sale.save()

                    messages.success(request, '판매 기록이 수정되었습니다.')
                    return redirect('students:student_detail', pk=student.pk)

            except Exception as e:
                messages.error(request, f'처리 중 오류 발생: {e}')
    else:
        form = BookSaleForm(instance=sale)

    return render(request, 'bookstore/book_sale_update.html', {
        'form': form,
        'sale': sale,
        'student': student
    })


def book_sale_cancel(request, pk):
    """납부 취소 - 납부 완료를 미납으로 되돌림"""
    sale = get_object_or_404(BookSale, pk=pk)
    student = sale.student

    if request.method == 'POST':
        if not sale.is_paid:
            messages.warning(request, '이미 미납 상태입니다.')
            return redirect('students:student_detail', pk=student.pk)

        try:
            with transaction.atomic():
                # 납부 완료 → 미납으로 변경
                sale.is_paid = False
                sale.payment_date = None
                sale.save()

                # 학생 미납금 증가
                total_price = sale.get_total_price()
                student.unpaid_amount += total_price
                student.save()

                messages.success(request, f"'{sale.book.title}' 납부가 취소되었습니다. 미납금에 추가되었습니다.")

        except Exception as e:
            messages.error(request, f'처리 중 오류 발생: {e}')

    return redirect('students:student_detail', pk=student.pk)


def book_sale_delete(request, pk):
    """판매 취소 - 판매 기록을 완전히 삭제하고 재고 복원"""
    sale = get_object_or_404(BookSale, pk=pk)
    student = sale.student
    book = sale.book
    quantity = sale.quantity
    total_price = sale.get_total_price()
    is_paid = sale.is_paid
    book_title = sale.book.title

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # 1. 재고 복원
                book.stock += quantity
                book.save()

                # 2. 미납 상태였다면 미납금 차감
                if not is_paid:
                    student.unpaid_amount -= total_price
                    student.save()

                # 3. 판매 기록 삭제
                sale.delete()

                messages.success(request, f"'{book_title}' 판매가 취소되었습니다. 재고가 복원되었습니다.")

        except Exception as e:
            messages.error(request, f'처리 중 오류 발생: {e}')

    return redirect('students:student_detail', pk=student.pk)


def book_content_list(request, pk):
    """교재 세부 목차 조회"""
    book = get_object_or_404(Book, pk=pk)
    contents = book.contents.all().order_by('page')

    # 대단원별로 그룹화
    chapters = {}
    for content in contents:
        chapter_key = (content.chapter_num, content.chapter_title)
        if chapter_key not in chapters:
            chapters[chapter_key] = {'sections': {}}

        section_key = (content.section_num, content.section_title)
        if section_key not in chapters[chapter_key]['sections']:
            chapters[chapter_key]['sections'][section_key] = []

        chapters[chapter_key]['sections'][section_key].append(content)

    return render(request, 'bookstore/book_content_list.html', {
        'book': book,
        'chapters': chapters,
        'contents': contents,
        'total_pages': contents.count(),
    })


def book_content_upload(request, pk):
    """교재 세부 목차 CSV 업로드"""
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST' and request.FILES.get('upload_file'):
        upload_file = request.FILES['upload_file']
        replace_existing = request.POST.get('replace_existing') == 'on'

        try:
            # CSV/Excel 파일 읽기
            if upload_file.name.endswith('.csv'):
                # 인코딩 자동 감지
                try:
                    df = pd.read_csv(upload_file, encoding='utf-8')
                except UnicodeDecodeError:
                    upload_file.seek(0)
                    df = pd.read_csv(upload_file, encoding='cp949')
            else:
                df = pd.read_excel(upload_file)

            # 기존 데이터 삭제 옵션
            if replace_existing:
                deleted_count = book.contents.all().delete()[0]
                messages.info(request, f"기존 목차 {deleted_count}개가 삭제되었습니다.")

            success_count = 0
            skip_count = 0

            for index, row in df.iterrows():
                # 필수 필드 확인
                chapter_num = row.get('대단원')
                chapter_title = row.get('대단원 주제', '')
                section_num = row.get('중단원')
                section_title = row.get('중단원 주제', '')
                subsection_num = row.get('소단원', '')
                subsection_title = row.get('소단원 주제', '')
                page = row.get('page')

                # 필수값 체크
                if pd.isna(chapter_num) or pd.isna(section_num) or pd.isna(page):
                    skip_count += 1
                    continue

                # 중복 체크 (같은 페이지)
                if not replace_existing and book.contents.filter(page=int(page)).exists():
                    skip_count += 1
                    continue

                # 데이터 생성
                BookContent.objects.update_or_create(
                    book=book,
                    page=int(page),
                    defaults={
                        'chapter_num': int(chapter_num),
                        'chapter_title': str(chapter_title) if not pd.isna(chapter_title) else '',
                        'section_num': int(section_num),
                        'section_title': str(section_title) if not pd.isna(section_title) else '',
                        'subsection_num': str(int(subsection_num)) if not pd.isna(subsection_num) else '',
                        'subsection_title': str(subsection_title) if not pd.isna(subsection_title) else '',
                    }
                )
                success_count += 1

            messages.success(request, f"'{book.title}' 목차 {success_count}개가 업로드되었습니다. (건너뜀: {skip_count}개)")
            return redirect('bookstore:book_content_list', pk=pk)

        except Exception as e:
            messages.error(request, f"파일 업로드 중 오류가 발생했습니다: {e}")
            return redirect('bookstore:book_content_upload', pk=pk)

    return render(request, 'bookstore/book_content_upload.html', {
        'book': book,
    })


def book_content_edit(request, pk, content_pk):
    """개별 목차 항목 수정"""
    book = get_object_or_404(Book, pk=pk)
    content = get_object_or_404(BookContent, pk=content_pk, book=book)

    if request.method == 'POST':
        try:
            content.chapter_num = int(request.POST.get('chapter_num', content.chapter_num))
            content.chapter_title = request.POST.get('chapter_title', content.chapter_title)
            content.section_num = int(request.POST.get('section_num', content.section_num))
            content.section_title = request.POST.get('section_title', content.section_title)
            content.subsection_num = request.POST.get('subsection_num', content.subsection_num)
            content.subsection_title = request.POST.get('subsection_title', content.subsection_title)
            content.page = int(request.POST.get('page', content.page))
            content.save()
            messages.success(request, "목차 정보가 수정되었습니다.")
        except Exception as e:
            messages.error(request, f"수정 중 오류 발생: {e}")

        return redirect('bookstore:book_content_list', pk=pk)

    return render(request, 'bookstore/book_content_edit.html', {
        'book': book,
        'content': content,
    })


def book_content_delete(request, pk, content_pk):
    """개별 목차 항목 삭제"""
    book = get_object_or_404(Book, pk=pk)
    content = get_object_or_404(BookContent, pk=content_pk, book=book)

    if request.method == 'POST':
        content.delete()
        messages.success(request, "목차 항목이 삭제되었습니다.")

    return redirect('bookstore:book_content_list', pk=pk)


def book_content_delete_all(request, pk):
    """교재의 모든 목차 삭제"""
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        deleted_count = book.contents.all().delete()[0]
        messages.success(request, f"'{book.title}'의 목차 {deleted_count}개가 모두 삭제되었습니다.")

    return redirect('bookstore:book_content_list', pk=pk)


def student_book_progress_list(request, sale_pk):
    """학생의 교재 진도 목록 조회"""
    sale = get_object_or_404(BookSale, pk=sale_pk)
    student = sale.student

    # 교사 포털에서 접근했는지 확인
    from_teacher_portal = request.GET.get('from') == 'teacher_portal'

    # 교사가 접근한 경우, 배정된 학생인지 확인
    if hasattr(request.user, 'teacher_profile') and not request.user.is_staff:
        from teachers.models import TeacherStudentAssignment
        from django.utils import timezone

        teacher = request.user.teacher_profile
        today = timezone.now().date()

        # 오늘 이 교사에게 배정된 학생인지 확인
        is_assigned = TeacherStudentAssignment.objects.filter(
            teacher=teacher,
            student=student,
            date=today,
            assignment_type='normal'
        ).exists()

        if not is_assigned:
            messages.error(request, '이 학생은 오늘 배정된 학생이 아닙니다.')
            return redirect('progress:my_progress')

        from_teacher_portal = True

    # 진도 레코드가 없으면 생성
    if not sale.progress_records.exists():
        created = sale.create_progress_records()
        if created > 0:
            messages.info(request, f"진도 항목 {created}개가 생성되었습니다.")

    progress_records = sale.progress_records.select_related('book_content', 'teacher').order_by('book_content__page')
    stats = sale.get_progress_stats()

    # 대단원별 그룹화
    chapters = {}
    for record in progress_records:
        content = record.book_content
        chapter_key = (content.chapter_num, content.chapter_title)
        if chapter_key not in chapters:
            chapters[chapter_key] = {'sections': {}}

        section_key = (content.section_num, content.section_title)
        if section_key not in chapters[chapter_key]['sections']:
            chapters[chapter_key]['sections'][section_key] = []

        chapters[chapter_key]['sections'][section_key].append(record)

    # 교사 포털에서 접근한 경우 별도 템플릿 사용
    template_name = 'bookstore/student_book_progress_list_teacher.html' if from_teacher_portal else 'bookstore/student_book_progress_list.html'

    return render(request, template_name, {
        'sale': sale,
        'student': student,
        'book': sale.book,
        'progress_records': progress_records,
        'chapters': chapters,
        'stats': stats,
        'achievement_choices': StudentBookProgress.ACHIEVEMENT_CHOICES,
        'from_teacher_portal': from_teacher_portal,
    })


def student_book_progress_update(request, sale_pk, progress_pk):
    """개별 진도 항목 평가/수정"""
    sale = get_object_or_404(BookSale, pk=sale_pk)
    progress = get_object_or_404(StudentBookProgress, pk=progress_pk, book_sale=sale)
    student = sale.student

    # 교사 포털에서 접근했는지 확인
    from_teacher_portal = request.GET.get('from') == 'teacher_portal' or request.POST.get('from_teacher_portal') == 'true'

    # 교사가 접근한 경우, 배정된 학생인지 확인
    if hasattr(request.user, 'teacher_profile') and not request.user.is_staff:
        teacher = request.user.teacher_profile
        today = timezone.now().date()

        is_assigned = TeacherStudentAssignment.objects.filter(
            teacher=teacher,
            student=student,
            date=today,
            assignment_type='normal'
        ).exists()

        if not is_assigned:
            messages.error(request, '이 학생은 오늘 배정된 학생이 아닙니다.')
            return redirect('progress:my_progress')

        from_teacher_portal = True

    if request.method == 'POST':
        try:
            # 학습 날짜
            study_date = request.POST.get('study_date')
            progress.study_date = study_date if study_date else None

            # 성취 수준
            progress.achievement = request.POST.get('achievement', '')

            # 보완 추천 여부
            progress.needs_review = request.POST.get('needs_review') == 'on'

            # 과제 수행 여부
            progress.homework_done = request.POST.get('homework_done') == 'on'

            # 담당 교사 자동 설정: 오늘 날짜 기준 배정된 교사 찾기
            today = timezone.now().date()
            assignment = TeacherStudentAssignment.objects.filter(
                student=student,
                date=today,
                assignment_type='normal'
            ).first()

            if assignment and assignment.teacher:
                progress.teacher = assignment.teacher

            progress.save()
            messages.success(request, f"p.{progress.book_content.page} 평가가 저장되었습니다.")

        except Exception as e:
            messages.error(request, f"저장 중 오류 발생: {e}")

        # 다음 항목으로 이동하거나 목록으로 돌아가기
        next_action = request.POST.get('next_action', 'list')

        # 교사 포털 파라미터 유지
        portal_param = '?from=teacher_portal' if from_teacher_portal else ''

        if next_action == 'next':
            # 다음 진도 항목 찾기
            next_progress = StudentBookProgress.objects.filter(
                book_sale=sale,
                book_content__page__gt=progress.book_content.page
            ).order_by('book_content__page').first()
            if next_progress:
                url = reverse('progress:student_book_progress_update', kwargs={'sale_pk': sale_pk, 'progress_pk': next_progress.pk})
                return redirect(url + portal_param)

        url = reverse('progress:student_book_progress_list', kwargs={'sale_pk': sale_pk})
        return redirect(url + portal_param)

    # 이전/다음 항목 찾기
    prev_progress = StudentBookProgress.objects.filter(
        book_sale=sale,
        book_content__page__lt=progress.book_content.page
    ).order_by('-book_content__page').first()

    next_progress = StudentBookProgress.objects.filter(
        book_sale=sale,
        book_content__page__gt=progress.book_content.page
    ).order_by('book_content__page').first()

    # 교사 포털에서 접근한 경우 별도 템플릿 사용
    template_name = 'bookstore/student_book_progress_update_teacher.html' if from_teacher_portal else 'bookstore/student_book_progress_update.html'

    return render(request, template_name, {
        'sale': sale,
        'student': student,
        'book': sale.book,
        'progress': progress,
        'content': progress.book_content,
        'prev_progress': prev_progress,
        'next_progress': next_progress,
        'achievement_choices': StudentBookProgress.ACHIEVEMENT_CHOICES,
        'from_teacher_portal': from_teacher_portal,
    })


def student_book_progress_bulk_update(request, sale_pk):
    """여러 진도 항목 일괄 평가"""
    sale = get_object_or_404(BookSale, pk=sale_pk)
    student = sale.student

    # 교사 포털에서 접근했는지 확인
    from_teacher_portal = request.GET.get('from') == 'teacher_portal' or request.POST.get('from_teacher_portal') == 'true'

    # 교사가 접근한 경우, 배정된 학생인지 확인
    if hasattr(request.user, 'teacher_profile') and not request.user.is_staff:
        teacher = request.user.teacher_profile
        today = timezone.now().date()

        is_assigned = TeacherStudentAssignment.objects.filter(
            teacher=teacher,
            student=student,
            date=today,
            assignment_type='normal'
        ).exists()

        if not is_assigned:
            messages.error(request, '이 학생은 오늘 배정된 학생이 아닙니다.')
            return redirect('progress:my_progress')

        from_teacher_portal = True

    if request.method == 'POST':
        updated_count = 0
        today = timezone.now().date()

        # 배정된 교사 찾기
        assignment = TeacherStudentAssignment.objects.filter(
            student=student,
            date=today,
            assignment_type='normal'
        ).first()
        teacher = assignment.teacher if assignment else None

        # 선택된 진도 항목들 처리
        progress_ids = request.POST.getlist('progress_ids')

        for progress_id in progress_ids:
            try:
                progress = StudentBookProgress.objects.get(pk=progress_id, book_sale=sale)

                study_date = request.POST.get(f'study_date_{progress_id}')
                achievement = request.POST.get(f'achievement_{progress_id}', '')
                needs_review = request.POST.get(f'needs_review_{progress_id}') == 'on'
                homework_done = request.POST.get(f'homework_done_{progress_id}') == 'on'

                progress.study_date = study_date if study_date else None
                progress.achievement = achievement
                progress.needs_review = needs_review
                progress.homework_done = homework_done

                if teacher:
                    progress.teacher = teacher

                progress.save()
                updated_count += 1

            except StudentBookProgress.DoesNotExist:
                continue

        if updated_count > 0:
            messages.success(request, f"{updated_count}개 항목이 업데이트되었습니다.")

        portal_param = '?from=teacher_portal' if from_teacher_portal else ''
        url = reverse('progress:student_book_progress_list', kwargs={'sale_pk': sale_pk})
        return redirect(url + portal_param)

    portal_param = '?from=teacher_portal' if from_teacher_portal else ''
    url = reverse('progress:student_book_progress_list', kwargs={'sale_pk': sale_pk})
    return redirect(url + portal_param)

