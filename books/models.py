from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import Subject, Publisher
from django.utils.translation import gettext_lazy as _
from barcode import EAN13
from io import BytesIO
from django.core.files import File
from barcode.writer import ImageWriter
from django.db import models, transaction
from django.core.files.storage import default_storage
import logging
import os
import qrcode
import uuid


logger = logging.getLogger(__name__)


class Book(models.Model):
    name = models.CharField(
        max_length=200, 
        verbose_name='교재 이름'
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='과목'
    )
    isbn = models.CharField(
        max_length=13, 
        null=True, 
        blank=True, 
        verbose_name='ISBN'
    )
    publisher = models.ForeignKey(
        Publisher, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='출판사'
    )
    difficulty_level = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        null=True, 
        blank=True, 
        verbose_name='교재 난이도'
    )
    memo = models.TextField(
        null=True, 
        blank=True, 
        verbose_name='메모'
    )
    # 바코드와 QR 코드를 위한 필드 추가
    barcode = models.ImageField(
        upload_to='books/barcodes/',
        null=True,
        blank=True,
        verbose_name='바코드'
    )
    qr_code = models.ImageField(
        upload_to='books/qrcodes/',
        null=True,
        blank=True,
        verbose_name='QR 코드'
    )
    unique_code = models.CharField(
        max_length=36,
        unique=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='고유 코드'
    )
    spare1 = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name='예비1'
    )
    spare2 = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name='예비2'
    )
    spare3 = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name='예비3'
    )

    class Meta:
        verbose_name = '교재'
        verbose_name_plural = '교재 목록'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # ISBN이 있는 경우 바코드 생성
        if self.isbn and not self.barcode:
            isbn = self.isbn.replace('-', '').strip()
            if len(isbn) == 13:
                barcode_image = BytesIO()
                EAN13(isbn, writer=ImageWriter()).write(barcode_image)
                self.barcode.save(
                    f'barcode_{self.isbn}.png',
                    File(barcode_image),
                    save=False
                )

        # ISBN이 있는 경우 QR 코드 생성
        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr_data = {
                'id': str(self.unique_code),
                'name': self.name,
                'isbn': self.isbn or ''
            }
            qr.add_data(str(qr_data))
            qr.make(fit=True)

            qr_image = qr.make_image(fill_color="black", back_color="white")
            qr_image_io = BytesIO()
            qr_image.save(qr_image_io, format='PNG')
            self.qr_code.save(
                f'qr_{self.unique_code}.png',
                File(qr_image_io),
                save=False
            )

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            with transaction.atomic():
                # 바코드 이미지 삭제
                if self.barcode:
                    try:
                        # 실제 파일 경로 가져오기
                        barcode_path = self.barcode.path
                        # ImageField의 delete() 메서드 호출
                        self.barcode.delete(save=False)
                        # 실제 파일이 여전히 존재하는지 확인하고 삭제
                        if os.path.exists(barcode_path):
                            default_storage.delete(barcode_path)
                        logger.info(f"Successfully deleted barcode image for book: {self.name} (ID: {self.id})")
                    except Exception as e:
                        logger.error(f"Error deleting barcode image for book {self.name} (ID: {self.id}): {str(e)}")
                        raise

                # QR 코드 이미지 삭제
                if self.qr_code:
                    try:
                        # 실제 파일 경로 가져오기
                        qr_path = self.qr_code.path
                        # ImageField의 delete() 메서드 호출
                        self.qr_code.delete(save=False)
                        # 실제 파일이 여전히 존재하는지 확인하고 삭제
                        if os.path.exists(qr_path):
                            default_storage.delete(qr_path)
                        logger.info(f"Successfully deleted QR code image for book: {self.name} (ID: {self.id})")
                    except Exception as e:
                        logger.error(f"Error deleting QR code image for book {self.name} (ID: {self.id}): {str(e)}")
                        raise

                # 상위 클래스의 delete 메서드 호출
                super().delete(*args, **kwargs)
                logger.info(f"Successfully deleted book: {self.name} (ID: {self.id})")

        except Exception as e:
            logger.error(f"Failed to delete book {self.name} (ID: {self.id}): {str(e)}")
            raise