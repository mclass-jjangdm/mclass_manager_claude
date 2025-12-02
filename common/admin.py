from django.contrib import admin
from .models import School, Publisher, Bank, PurchaseLocation, Subject

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address')
    search_fields = ('name', 'phone')
    list_filter = ('name', 'phone')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(PurchaseLocation)
class PurchaseLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone1', 'phone2', 'email', 'business_number')
    search_fields = ('name', )

