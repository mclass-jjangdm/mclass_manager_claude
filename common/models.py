from django.db import models


class School(models.Model):
    name = models.CharField(max_length=100, verbose_name='교명')
    phone = models.CharField(max_length=15, verbose_name='전화번호', blank=True, null=True)
    address = models.TextField(verbose_name='주소', blank=True, null=True)

    class Meta:
        verbose_name = '학교'
        verbose_name_plural = '학교'

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='과목명')

    class Meta:
        verbose_name = '과목'
        verbose_name_plural = '과목'

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='출판사명')

    class Meta:
        verbose_name = '출판사'
        verbose_name_plural = '출판사'

    def __str__(self):
        return self.name


class Bank(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='은행명')

    class Meta:
        verbose_name = '은행'
        verbose_name_plural = '은행'

    def __str__(self):
        return self.name


