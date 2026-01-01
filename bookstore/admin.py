from django.contrib import admin
from .models import BookSupplier, Book, BookSale, BookStockLog


@admin.register(BookSupplier)
class BookSupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'bank_name', 'account_number', 'created_at')
    search_fields = ('name', 'registration_number')
    list_filter = ('bank_name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'publisher', 'supplier', 'original_price', 'price', 'stock', 'created_at')
    search_fields = ('title', 'isbn', 'author', 'publisher')
    list_filter = ('supplier', 'publisher')
    ordering = ('title',)


@admin.register(BookSale)
class BookSaleAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'sale_date', 'price', 'quantity', 'is_paid', 'payment_date')
    search_fields = ('student__name', 'book__title')
    list_filter = ('is_paid', 'sale_date')
    date_hierarchy = 'sale_date'


@admin.register(BookStockLog)
class BookStockLogAdmin(admin.ModelAdmin):
    list_display = ('book', 'supplier', 'quantity', 'cost_price', 'total_payment', 'is_paid', 'created_at')
    search_fields = ('book__title', 'supplier__name')
    list_filter = ('is_paid', 'supplier')
    date_hierarchy = 'created_at'
