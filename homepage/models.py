from django.db import models
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
