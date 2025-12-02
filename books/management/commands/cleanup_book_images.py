from django.core.management.base import BaseCommand
from django.conf import settings
from books.models import Book
import os

class Command(BaseCommand):
    help = '사용되지 않는 바코드와 QR 코드 이미지 파일을 정리합니다.'

    def handle(self, *args, **options):
        # 데이터베이스에 있는 모든 이미지 경로 수집
        db_barcodes = set(Book.objects.exclude(barcode='').values_list('barcode', flat=True))
        db_qrcodes = set(Book.objects.exclude(qr_code='').values_list('qr_code', flat=True))

        # 바코드 디렉토리 정리
        barcode_dir = os.path.join(settings.MEDIA_ROOT, 'books/barcodes')
        if os.path.exists(barcode_dir):
            for filename in os.listdir(barcode_dir):
                filepath = f'books/barcodes/{filename}'
                if filepath not in db_barcodes:
                    full_path = os.path.join(barcode_dir, filename)
                    os.remove(full_path)
                    self.stdout.write(
                        self.style.SUCCESS(f'삭제됨: {full_path}')
                    )

        # QR 코드 디렉토리 정리
        qrcode_dir = os.path.join(settings.MEDIA_ROOT, 'books/qrcodes')
        if os.path.exists(qrcode_dir):
            for filename in os.listdir(qrcode_dir):
                filepath = f'books/qrcodes/{filename}'
                if filepath not in db_qrcodes:
                    full_path = os.path.join(qrcode_dir, filename)
                    os.remove(full_path)
                    self.stdout.write(
                        self.style.SUCCESS(f'삭제됨: {full_path}')
                    )

        self.stdout.write(
            self.style.SUCCESS('이미지 파일 정리가 완료되었습니다.')
        )
