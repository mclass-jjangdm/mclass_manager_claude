from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib import messages
from common.models import Publisher, Subject
from .models import Book
from .forms import BookForm
from django.http import HttpResponse
from django.contrib import messages
from django.views.generic import FormView
from django.shortcuts import redirect
import logging
import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'books/books_list.html'
    context_object_name = 'books'
    ordering = ['name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 과목 필터
        subject_id = self.request.GET.get('subject')
        if subject_id:
            # Convert subject_id to an integer if it's not already
            try:
                subject_id = int(subject_id)
            except ValueError:
                pass  # Leave it as a string if it's not a valid integer
            queryset = queryset.filter(subject_id=subject_id)
        
        # 출판사 필터
        publisher_id = self.request.GET.get('publisher')
        if publisher_id:
            # Convert publisher_id to an integer if it's not already
            try:
                publisher_id = int(publisher_id)
            except ValueError:
                pass  # Leave it as a string if it's not a valid integer
            queryset = queryset.filter(publisher_id=publisher_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 필터링을 위한 선택 옵션들 추가
        context['subjects'] = Subject.objects.all()
        context['publishers'] = Publisher.objects.all()
        # 현재 적용된 필터값들 유지
        context['current_filters'] = {
            'subject': self.request.GET.get('subject', ''),
            'publisher': self.request.GET.get('publisher', ''),
        }
        return context


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/books_form.html'
    success_url = reverse_lazy('books:book_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '교재 등록'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, '교재가 성공적으로 등록되었습니다.')
        return super().form_valid(form)


class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/books_form.html'
    success_url = reverse_lazy('books:book_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '교재 수정'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, '교재가 성공적으로 수정되었습니다.')
        return super().form_valid(form)
    

class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'


class BookDeleteView(LoginRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books:book_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "교재가 성공적으로 삭제되었습니다.")
        return super().delete(request, *args, **kwargs)


class BookExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            # 교재 데이터 조회
            books = Book.objects.all().values(
                'name', 'subject__name', 'isbn', 'publisher__name', 'difficulty_level', 'memo',
            )
            
            # 데이터가 없는 경우 처리
            if not books.exists():
                messages.warning(request, '내보낼 교재 데이터가 없습니다.')
                logger.info('Export attempted with no book data available')
                return redirect('books:book_list')
            
            # DataFrame 생성 및 컬럼명 설정
            df = pd.DataFrame(list(books))
            df.columns = [
                '교재명', '과목', 'ISBN', '출판사', '난이도', '메모',
            ]
            
            # null 값 처리
            df = df.fillna('')  # null 값을 빈 문자열로 변환
            
            # 엑셀 파일 생성
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="books_export.xlsx"'
            
            # 엑셀 파일로 변환
            df.to_excel(
                response,
                index=False,
                engine='openpyxl',
                sheet_name='교재 목록'
            )
            
            logger.info(f'Successfully exported {len(df)} books to Excel')
            return response
            
        except Exception as e:
            logger.error(f'Error during book export: {str(e)}')
            messages.error(
                request,
                '교재 데이터 내보내기 중 오류가 발생했습니다. 나중에 다시 시도해 주세요.'
            )
            return redirect('books:book_list')
        

class BookImportForm(forms.Form):
    file = forms.FileField(
        label='엑셀 파일',
        help_text='*.xlsx 또는 *.csv 파일을 선택해주세요.'
    )


class BookImportView(LoginRequiredMixin, FormView):
    template_name = 'books/book_import.html'
    form_class = BookImportForm
    success_url = reverse_lazy('books:book_list')
    
    def form_valid(self, form):
        file = form.cleaned_data['file']
        
        try:
            # 파일 확장자 확인 및 데이터 읽기
            if file.name.endswith('.xlsx'):
                df = pd.read_excel(file, dtype={
                    '교재명': str,
                    '과목': str,
                    '출판사': str,
                    'ISBN': str,
                    '난이도': str,
                    '메모': str
                })
            elif file.name.endswith('.csv'):
                df = pd.read_csv(file, dtype={
                    '교재명': str,
                    '과목': str,
                    '출판사': str,
                    'ISBN': str,
                    '난이도': str,
                    '메모': str,
                })
            else:
                raise ValueError('지원하지 않는 파일 형식입니다.')
            
            # NaN 값을 None으로 변환
            df = df.replace({np.nan: None})
            
            # 필수 컬럼 확인
            required_columns = ['교재명']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f'필수 컬럼이 없습니다: {", ".join(missing_columns)}')
            
            # 데이터 저장
            for _, row in df.iterrows():
                
                # 관련 객체 조회 또는 생성
                subject = None
                if pd.notna(row.get('과목')):
                    subject = Subject.objects.filter(name=str(row.get('과목'))).first()
                
                publisher = None
                if pd.notna(row.get('출판사')):
                    publisher = Publisher.objects.filter(name=str(row.get('출판사'))).first()
                                
                # 교재 생성 또는 업데이트
                book, created = Book.objects.update_or_create(
                    name=str(row['교재명']),
                    defaults={
                        'subject': subject,
                        'isbn': str(row.get('ISBN')) if pd.notna(row.get('ISBN')) else None,
                        'publisher': publisher,
                        'difficulty_level': str(row.get('난이도')) if pd.notna(row.get('난이도')) else None,
                        'memo': str(row.get('메모')) if pd.notna(row.get('메모')) else None
                    }
                )
            
            messages.success(self.request, '교재 데이터를 성공적으로 가져왔습니다.')
            return super().form_valid(form)
            
        except Exception as e:
            messages.error(self.request, f'데이터 가져오기 실패: {str(e)}')
            return redirect('books:book_list')