from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.BookListView.as_view(), name='book_list'),
    path('create/', views.BookCreateView.as_view(), name='book_create'),
    path('<int:pk>/update/', views.BookUpdateView.as_view(), name='book_update'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('export/', views.BookExportView.as_view(), name='book_export'),
    path('import/', views.BookImportView.as_view(), name='book_import'),
    path('<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
]