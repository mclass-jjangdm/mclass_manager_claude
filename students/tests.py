import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from classes.models import Enrollment, Lesson
from students.models import Student


class StudentReadmitTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff = User.objects.create_user(
            username='staff', password='pw', is_staff=True
        )
        self.client.force_login(self.staff)

        self.student = Student.objects.create(
            name='김노아', grade='K9', student_id='S0001', is_active=True,
        )
        self.lesson = Lesson.objects.create(name='수학 정규반', base_tuition=200000)
        self.enroll = Enrollment.objects.create(
            student=self.student, lesson=self.lesson,
            enrollment_date=datetime.date(2026, 3, 1), is_active=True,
        )

    def _quit(self, quit_date):
        self.client.post(
            reverse('students:student_quit', args=[self.student.pk]),
            {'quit_date': quit_date.isoformat()},
        )

    def test_quit_then_readmit_reactivates_selected_enrollment(self):
        self._quit(datetime.date(2026, 7, 22))
        self.enroll.refresh_from_db()
        self.assertFalse(self.enroll.is_active)
        self.assertEqual(self.enroll.end_date, datetime.date(2026, 7, 22))

        resp = self.client.post(
            reverse('students:student_readmit', args=[self.student.pk]),
            {'readmit_date': '2026-08-17', 'enrollment_ids': [str(self.enroll.pk)]},
        )
        self.assertEqual(resp.status_code, 302)

        self.student.refresh_from_db()
        self.enroll.refresh_from_db()
        self.assertTrue(self.student.is_active)
        self.assertIsNone(self.student.quit_date)
        self.assertTrue(self.enroll.is_active)
        self.assertIsNone(self.enroll.end_date)
        self.assertEqual(self.enroll.enrollment_date, datetime.date(2026, 8, 17))

    def test_readmit_without_selection_leaves_enrollment_inactive(self):
        self._quit(datetime.date(2026, 7, 22))
        self.client.post(
            reverse('students:student_readmit', args=[self.student.pk]),
            {'readmit_date': '2026-08-17'},
        )
        self.enroll.refresh_from_db()
        self.assertFalse(self.enroll.is_active)


class EnrollmentCreateReactivateTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff = User.objects.create_user(
            username='staff', password='pw', is_staff=True
        )
        self.client.force_login(self.staff)
        self.student = Student.objects.create(
            name='이하늘', grade='K10', student_id='S0002', is_active=True,
        )
        self.lesson = Lesson.objects.create(name='영어 정규반', base_tuition=180000)
        Enrollment.objects.create(
            student=self.student, lesson=self.lesson,
            enrollment_date=datetime.date(2026, 3, 1),
            end_date=datetime.date(2026, 7, 22), is_active=False,
        )

    def test_enrollment_create_reactivates_ended_row(self):
        resp = self.client.post(
            reverse('classes:enrollment_create', args=[self.lesson.pk]),
            {
                'student': [str(self.student.pk)],
                'enrollment_date': '2026-08-17',
                'is_active': 'on',
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            Enrollment.objects.filter(student=self.student, lesson=self.lesson).count(), 1
        )
        enroll = Enrollment.objects.get(student=self.student, lesson=self.lesson)
        self.assertTrue(enroll.is_active)
        self.assertIsNone(enroll.end_date)
        self.assertEqual(enroll.enrollment_date, datetime.date(2026, 8, 17))
