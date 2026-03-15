from datetime import date as date_cls

from django.db import models
from django.db.models import F, Sum
from django.contrib.auth.models import User


class Notice(models.Model):
    """공지사항"""
    title = models.CharField(max_length=200, verbose_name='제목')
    content = models.TextField(verbose_name='내용')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='작성자')
    is_published = models.BooleanField(default=True, verbose_name='게시 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '공지사항'
        verbose_name_plural = '공지사항'

    def __str__(self):
        return self.title


class Column(models.Model):
    """원장 칼럼"""
    title = models.CharField(max_length=200, verbose_name='제목')
    content = models.TextField(verbose_name='내용')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='작성자')
    is_published = models.BooleanField(default=True, verbose_name='게시 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '원장칼럼'
        verbose_name_plural = '원장칼럼'

    def __str__(self):
        return self.title


class ExamNews(models.Model):
    """입시 뉴스"""
    title = models.CharField(max_length=300, verbose_name='제목')
    content = models.TextField(verbose_name='내용')
    source_url = models.URLField(blank=True, verbose_name='스크래핑 URL')
    source_name = models.CharField(max_length=100, blank=True, verbose_name='출처명')
    original_url = models.URLField(blank=True, verbose_name='원문 링크')
    is_published = models.BooleanField(default=True, verbose_name='게시 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '입시뉴스'
        verbose_name_plural = '입시뉴스'

    def __str__(self):
        return self.title


class ConsultationRequest(models.Model):
    """상담 신청"""
    STATUS_CHOICES = [
        ('new', '신규'),
        ('contacted', '연락 완료'),
        ('registered', '등록 완료'),
    ]
    GRADE_CHOICES = [
        ('K5', '초5'), ('K6', '초6'),
        ('K7', '중1'), ('K8', '중2'), ('K9', '중3'),
        ('K10', '고1'), ('K11', '고2'), ('K12', '고3'),
    ]
    GENDER_CHOICES = [('M', '남'), ('F', '여')]

    # 기본 정보
    name = models.CharField(max_length=50, verbose_name='이름')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='성별')
    school = models.CharField(max_length=100, verbose_name='학교')
    grade = models.CharField(max_length=3, choices=GRADE_CHOICES, verbose_name='학년')
    phone_number = models.CharField(max_length=20, verbose_name='학생 전화번호')
    email = models.EmailField(blank=True, verbose_name='이메일')
    parent_phone = models.CharField(max_length=20, verbose_name='부모님 전화번호')

    # 상담 추가 정보
    subjects = models.CharField(max_length=300, blank=True, verbose_name='상담 과목')
    learning_methods = models.CharField(max_length=200, blank=True, verbose_name='기존 학습 방법')
    current_status = models.TextField(blank=True, verbose_name='현재 학습 상황')
    current_textbook = models.CharField(max_length=200, blank=True, verbose_name='학습 중인 교재')
    last_score = models.IntegerField(null=True, blank=True, verbose_name='직전 학기 점수')
    expectation = models.TextField(blank=True, verbose_name='학원에 바라는 점')

    # 관리 정보
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='처리 상태')
    admin_memo = models.TextField(blank=True, verbose_name='관리자 메모')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='신청일시')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '상담 신청'
        verbose_name_plural = '상담 신청'

    def __str__(self):
        return f"{self.name} ({self.get_grade_display()}) - {self.created_at.strftime('%Y.%m.%d')}"

    def get_interview_info_text(self):
        """StudentCreateView의 interview_info 필드에 채울 형식화된 텍스트"""
        lines = ['[상담 신청 정보]', f'학교(입력): {self.school}']
        if self.subjects:
            lines.append(f'상담 과목: {self.subjects}')
        if self.learning_methods:
            lines.append(f'기존 학습 방법: {self.learning_methods}')
        if self.current_status:
            lines.append(f'현재 학습 상황: {self.current_status}')
        if self.current_textbook:
            lines.append(f'학습 중인 교재: {self.current_textbook}')
        if self.last_score is not None:
            lines.append(f'직전 학기 점수: {self.last_score}점')
        if self.expectation:
            lines.append(f'학원에 바라는 점: {self.expectation}')
        return '\n'.join(lines)


class SchoolIntro(models.Model):
    """학원 소개 (singleton, pk=1 고정)"""
    academy_name = models.CharField(max_length=100, default='엠클래스 수학과학전문학원', verbose_name='학원명')
    subtitle = models.CharField(max_length=200, default='수학·과학 전문 학원', verbose_name='슬로건')
    intro_text = models.TextField(default='', verbose_name='학원 소개')
    vision_text = models.TextField(default='', verbose_name='교육 철학')
    address = models.CharField(max_length=300, default='', verbose_name='주소')
    phone = models.CharField(max_length=20, default='031-439-1222', verbose_name='전화번호')
    email = models.EmailField(default='jjangdm@mclass.co.kr', verbose_name='이메일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '학원소개'
        verbose_name_plural = '학원소개'

    def __str__(self):
        return self.academy_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class VisitorStat(models.Model):
    """일별 방문자 통계"""
    date = models.DateField(unique=True, verbose_name='날짜')
    count = models.PositiveIntegerField(default=0, verbose_name='일일 방문자 수')

    class Meta:
        verbose_name = '방문자 통계'
        verbose_name_plural = '방문자 통계'
        ordering = ['-date']

    def __str__(self):
        return f"{self.date}: {self.count}명"

    @classmethod
    def record_visit(cls, session, today=None):
        """세션 기반 중복 방지 - 하루 1회만 카운트"""
        if today is None:
            today = date_cls.today()
        today_str = today.isoformat()
        if session.get('visitor_counted_date') == today_str:
            return  # 이미 오늘 카운트됨
        obj, created = cls.objects.get_or_create(date=today, defaults={'count': 1})
        if not created:
            cls.objects.filter(date=today).update(count=F('count') + 1)
        session['visitor_counted_date'] = today_str

    @classmethod
    def get_stats(cls, today=None):
        """오늘 방문자 수, 전체 방문자 수 반환"""
        if today is None:
            today = date_cls.today()
        today_stat = cls.objects.filter(date=today).first()
        today_count = today_stat.count if today_stat else 0
        total_count = cls.objects.aggregate(t=Sum('count'))['t'] or 0
        return today_count, total_count
