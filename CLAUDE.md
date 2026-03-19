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

## 과목 코드 체계 (subjects 앱)

### 교육과정 버전 분리
- **2015 교육과정**: 기존 4자리 코드 유지 (현 고3 대상, `curriculum_year=2015`)
- **2022 개정교육과정**: 아래 6자리 코드 체계 적용 (`curriculum_year=2022`)

### 2022 과목 코드: 6자리 `GG-T-S-NN`

| 자리 | 의미 | 값 |
|------|------|----|
| GG (1–2) | 교과(군) | 01=국어, 02=수학, 03=영어, 04=사회(역사/도덕 포함), 05=과학, 06=기술가정/정보, 07=체육, 08=예술, 09=제2외국어/한문, 10=교양 |
| T (3) | 과목 유형 | 0=공통과목, 1=일반선택, 2=진로선택, 3=융합선택 |
| S (4) | 수능 출제 | 0=비수능, 1=수능 |
| NN (5–6) | 교과군 내 일련번호 | 01~99 (교과군 전체 기준 순번) |

**예시**
- `010001` → 국어 / 공통 / 비수능 / 01번 → 공통국어1
- `011103` → 국어 / 일반선택 / 수능 / 03번 → 화법과 언어
- `022008` → 수학 / 진로선택 / 비수능 / 08번 → 기하
- `042109` → 사회 / 진로선택 / 수능 / 09번 → 한국지리 탐구

### 수능 출제(S=1) 기준 과목
- **국어**: 화법과 언어, 독서와 작문, 문학
- **수학**: 공통수학1, 공통수학2, 대수, 미적분1, 확률과 통계
- **영어**: 영어1, 영어2
- **사회**: 한국사1, 한국사2 / 세계 시민과 지리, 세계사, 사회와 문화, 현대사회와 윤리 / 한국지리 탐구, 동아시아 역사 기행, 정치, 법과 사회, 경제, 윤리와 사상, 인문학과 윤리, 국제 관계의 이해
- **과학**: 물리학, 화학, 생명과학, 지구과학 / 역학과 에너지, 전자기와 양자, 물질과 에너지, 화학 반응의 세계, 세포와 물질대사, 생물의 유전, 지구시스템과학, 행성우주과학
- **제2외국어/한문**: 독일어, 프랑스어, 스페인어, 중국어, 일본어, 러시아어, 아랍어, 베트남어, 한문

### 위계(선수과목)
`Subject.prerequisite` ForeignKey(self)로 관리. 공통과목(T=0)이 선택과목의 선수과목이 되는 경우 명시적으로 지정.

### 관련 모델 필드 (subjects/models.py)
- `Subject.curriculum_year` — 2015 또는 2022
- `Subject.prerequisite` — 선수과목 FK (nullable)
- `Subject.subject_type_display` — property: 코드에서 유형명 반환
- `Subject.is_csat` — property: 수능 출제 여부 반환

### 관련 모델 필드 (grades/models.py)
- `Grade.subject_classification` — `common/general/elective/fusion` (is_elective 대체)
- `Grade.is_elective` — deprecated, subject_classification과 자동 동기화

### 관련 모델 필드 (students/models.py)
- `Student.hs_admission_year` — 고등학교 입학년도 (2025 이상 → 2022 교육과정)
- `Student.curriculum_year` — property: 입학년도 기준 교육과정 자동 반환

### 새 과목 임포트
`subject_list.csv` 파일에 `교육과정` 컬럼을 추가하면 `import_subjects` 관리 명령어가 자동 처리.
컬럼 없으면 default 2015.

## Git 커밋 컨벤션

```
<타입>: <제목 (한글)>

<본문 설명>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

타입 예시: 기능 추가, 버그 수정, UI 개선, 리팩토링
