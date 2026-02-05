# MClass Manager - Claude 개발 참고 문서

이 문서는 Claude AI와의 협업 개발을 위한 프로젝트 핵심 정보를 정리한 것입니다.

## 프로젝트 개요

- **프로젝트명**: MClass Manager (엠클래스 학원 관리 시스템)
- **기술 스택**: Django 5.2.4 + MySQL 8.0 + TailwindCSS/Bootstrap 4
- **Python 버전**: 3.13
- **개발 서버 실행**: `python manage.py runserver`

## 핵심 앱 구조

| 앱 | 주요 기능 | 주요 모델 |
|---|---|---|
| `students` | 학생 관리, 엑셀 연동 | Student |
| `teachers` | 교사 관리, 급여/출근 | Teacher, Attendance, Salary, Message |
| `bookstore` | 교재/재고/판매 관리 | Book, BookContent, BookSale, StudentBookProgress |
| `progress` | 진도 평가 (URL 라우팅) | - (bookstore 모델 사용) |
| `grades` | 성적 관리 | Grade, MockExamGrade |
| `payment` | 수납 관리 | Payment, PaymentHistory |
| `common` | 공통 데이터 | School, Subject, Publisher, Bank |

## 진도 평가 시스템 (최근 집중 개발 영역)

### URL 구조
- `/progress/book/<sale_pk>/` - 학생별 교재 진도 목록
- `/progress/book/<sale_pk>/<progress_pk>/` - 개별 진도 수정
- `/progress/book/<sale_pk>/<progress_pk>/reset/` - 개별 진도 초기화 (관리자)
- `/progress/book/<sale_pk>/bulk-reset/` - 선택 진도 일괄 초기화 (관리자)
- `/progress/book/<sale_pk>/bulk-update/` - 미완료 항목 일괄 저장

### 주요 뷰 함수 (bookstore/views.py)
```python
student_book_progress_list(request, sale_pk)      # 진도 목록
student_book_progress_update(request, sale_pk, progress_pk)  # 개별 수정
student_book_progress_bulk_update(request, sale_pk)  # 일괄 저장
student_book_progress_reset(request, sale_pk, progress_pk)   # 개별 초기화
student_book_progress_bulk_reset(request, sale_pk)  # 일괄 초기화
```

### 핵심 모델 관계
```
Student → BookSale → Book
                  → StudentBookProgress → BookContent
```

### 템플릿 위치
- `templates/bookstore/student_book_progress_list.html` - 진도 목록 (대단원별 폴딩 UI)
- `templates/bookstore/student_book_progress_form.html` - 진도 수정 폼

## 부모님 페이지 시스템

### URL 구조
- `/parent/` - 부모 조회 페이지 (학생 정보 입력)
- `/parent/student/<pk>/` - 학생 상세 정보 (교재 결제 현황)

### 세션 기반 접근 제어
- `parent_student_id` 세션 키로 조회 권한 관리
- 비로그인 사용자도 학생 정보 입력 후 접근 가능

## HTML Form 관련 주의사항

### form 태그 중첩 불가
HTML에서 `<form>` 태그 안에 또 다른 `<form>` 태그를 넣을 수 없음.
Django 템플릿에서 `{% if user.is_staff %}` 등으로 조건부 렌더링 시 주의 필요.

**해결 방법**: 숨겨진 form + JavaScript로 우회
```html
<!-- 메인 폼 외부에 숨겨진 폼 배치 -->
<form method="POST" id="hidden-form" style="display:none;">
    {% csrf_token %}
</form>

<script>
function submitHiddenForm(action) {
    const form = document.getElementById('hidden-form');
    form.action = action;
    form.submit();
}
</script>
```

## 자주 사용하는 Django 패턴

### 관리자 전용 뷰
```python
@login_required
def admin_only_view(request, pk):
    if not request.user.is_staff:
        messages.error(request, '관리자만 사용 가능합니다.')
        return redirect('...')
    # 로직
```

### TailwindCSS 스타일 (인라인)
프로젝트는 TailwindCSS 클래스를 주로 사용:
```html
<button class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
    버튼
</button>
```

### 날짜 입력 필드 (Flatpickr)
```html
<input type="text" class="mclass-datepicker" readonly>
```

## 최근 개발 이력 (2026-02)

### 부모님 페이지 개선
- 조회 폼 숨기기 (학생 찾은 후)
- 버튼 아이콘 변경 (화폐 → 가족)
- 나가기 버튼 위치 이동
- 푸터에 연락처 추가

### 진도 평가 테이블 개선
- 미완료 항목 대단원별 폴딩 UI
- 완료 항목 관리자 초기화 기능 (개별/일괄)
- 학습일/성취도 컬럼 폭 조정
- 체크박스 기본값 해제

## 디버깅 팁

### 웹 서버 재시작
Django 개발 서버는 코드 변경 시 자동 재시작되지만,
템플릿 변경은 브라우저 새로고침만 필요.

### 로그 확인
```bash
# debug.log 파일 확인
tail -f debug.log
```

### 마이그레이션 확인
```bash
python manage.py showmigrations
python manage.py makemigrations --dry-run
```

## 파일 구조 참고

```
mclass_manager_claude/
├── bookstore/
│   ├── models.py      # Book, BookContent, BookSale, StudentBookProgress
│   ├── views.py       # 진도 평가 뷰 포함
│   └── urls.py        # 교재 관리 URL
├── progress/
│   └── urls.py        # 진도 평가 URL (bookstore.views로 연결)
├── students/
│   ├── models.py      # Student
│   └── views.py       # 학생 관리, 부모 페이지
├── teachers/
│   ├── models.py      # Teacher, Message, MessageReadStatus
│   └── views.py       # 교사 포털, 메시지 시스템
├── templates/
│   ├── bookstore/     # 교재/진도 템플릿
│   ├── students/      # 학생/부모 템플릿
│   └── teachers/      # 교사 포털 템플릿
└── mclass_manager/
    ├── settings.py    # Django 설정
    └── urls.py        # 메인 URL 라우팅
```

## Git 커밋 컨벤션

```
<타입>: <제목 (한글)>

<본문 설명>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

타입 예시: 기능 추가, 버그 수정, UI 개선, 리팩토링
