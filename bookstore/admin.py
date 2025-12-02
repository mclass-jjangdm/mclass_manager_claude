from django.contrib import admin
from .models import BookStock, BookDistribution


@admin.register(BookStock)
class BookStockAdmin(admin.ModelAdmin):
    list_display = ('received_date', 'book', 'quantity', 'list_price', 'unit_price', 'selling_price', 'memo')
    list_filter = ('received_date',)
    search_fields = ('book__name', 'book__isbn')
    autocomplete_fields = ['book']
    readonly_fields = ['received_date'] 


@admin.register(BookDistribution)
class BookDistributionAdmin(admin.ModelAdmin):
    list_display = ('student', 'book_stock', 'sold_date', 'quantity', 'notes')
    list_filter = ('sold_date',)
    search_fields = ('student__name', 'book_stock__book__name', 'book_stock__book__isbn')
    autocomplete_fields = ['student', 'book_stock']

