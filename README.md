# MClass Manager (엠클래스 학원 관리 시스템)

**MClass Manager**는 학원 운영을 효율적으로 돕기 위해 개발된 통합 관리 시스템입니다. 학생 및 강사 관리부터 교재 재고, 수납, 급여 정산까지 학원 운영에 필요한 핵심 기능을 제공합니다.

## 프로젝트 소개

이 프로젝트는 Django와 MySQL을 기반으로 구축되었으며, Docker를 통해 손쉽게 배포하고 운영할 수 있도록 설계되었습니다. 데이터의 엑셀 가져오기/내보내기, PDF 보고서 생성, 바코드/QR 코드를 활용한 교재 관리 등 실무에 최적화된 기능들을 포함하고 있습니다.

## 기술 스택

### Backend
- Python 3.13
- Django 5.2.4
- Django REST Framework 3.16.0
- MySQL 8.0

### Frontend
- Bootstrap 4
- django-crispy-forms

### 데이터 처리
- pandas, openpyxl, xlsxwriter (엑셀 처리)
- reportlab (PDF 생성)
- python-barcode, qrcode (바코드/QR 생성)

### 배포
- Docker & Docker Compose
- gunicorn
- WhiteNoise (정적 파일)

## 앱 구성

| 앱 | 기능 |
|---|---|
| **common** | 공통 데이터 (학교, 과목, 출판사, 은행) |
| **students** | 학생 관리, 엑셀 연동, 파일 관리 |
| **teachers** | 교사 관리, 출근/급여 정산, PDF 보고서 |
| **bookstore** | 교재 재고 관리, 판매/반품, 구매처 관리 |
| **subjects** | 과목 코드 관리 |
| **grades** | 내신/모의고사 성적 관리 |
| **payment** | 수납 내역 및 결제 상태 관리 |
| **progress** | 진도표 시스템, 문제 유형 코딩 |
| **maintenance** | 시설/관리비 관리 |

## 주요 기능

### 1. 학생 관리 (Students)
- 학생 정보 CRUD (이름, 학교, 학년, 연락처)
- 엑셀 일괄 등록/내보내기
- 학생 상태 관리 (재원/퇴원/휴원)
- 학년 승격 기능
- SMS/이메일 발송
- 개인 파일 첨부

### 2. 교사 관리 (Teachers)
- 교사 정보 관리
- 일별 출퇴근 기록 및 근무시간 계산
- 월별 급여 정산 (기본급 + 추가급)
- PDF 보고서 생성 (급여명세서, 근무내역서)
- 퇴사/재입사 관리

### 3. 교재 관리 (Bookstore)
- 교재 정보 (제목, ISBN, 바코드, 가격)
- 재고 관리 (입고, 출고, 반품)
- 교재 코드 자동 생성 (7자리)
- 학생별 교재 판매/분배
- 구매처 관리 및 정산

### 4. 성적 관리 (Grades)
- 내신 성적 (학기별, 과목별)
- 모의고사 성적
- 진로선택 과목 대응
- 엑셀 일괄 등록

### 5. 진도표 시스템 (Progress)
- 20자리 문제 유형 코드 체계
  - 교재코드(7) + 대단원(2) + 중단원(2) + 소단원(2) + 유형(3) + 문제번호(4)
- 교재-문제 연결
- 학생별 진도 추적 및 진도율 계산

### 6. 수납 관리 (Payment)
- 수납 내역 기록
- 결제 상태 추적 (미납/부분납부/완납)
- 대시보드 현황 조회

### 7. 시설 관리 (Maintenance)
- 호실별 정보 관리
- 월별 관리비 기록
- 납부 현황 관리

## 설치 및 실행

### 요구사항
- Python 3.13+
- MySQL 8.0+
- Docker & Docker Compose (선택)

### 로컬 설치

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정 (.env 파일 생성)
cp .env.example .env
# .env 파일 수정

# 데이터베이스 마이그레이션
python manage.py migrate

# 정적 파일 수집
python manage.py collectstatic

# 개발 서버 실행
python manage.py runserver
```

### Docker 실행

```bash
docker-compose up -d
```

## 환경 변수

`.env` 파일에 다음 변수들을 설정하세요:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=mclass_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306

# SMS (Aligo)
ALIGO_API_KEY=your-api-key
ALIGO_USER_ID=your-user-id
ALIGO_SENDER=your-sender-number
```

## URL 구조

| 경로 | 설명 |
|------|------|
| `/` | 메인 대시보드 |
| `/login/` | 로그인 |
| `/admin/` | 관리자 페이지 |
| `/students/` | 학생 관리 |
| `/teachers/` | 교사 관리 |
| `/bookstore/` | 교재 관리 |
| `/grades/` | 성적 관리 |
| `/payment/` | 수납 관리 |
| `/progress/` | 진도표 관리 |
| `/subjects/` | 과목 관리 |
| `/maintenance/` | 시설 관리 |

## 프로젝트 구조

```
mclass_manager_claude/
├── mclass_manager/          # 메인 프로젝트 설정
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── common/                  # 공통 모델 (학교, 은행, 출판사)
├── students/                # 학생 관리
├── teachers/                # 교사 관리
├── bookstore/               # 교재 관리
├── subjects/                # 과목 관리
├── grades/                  # 성적 관리
├── payment/                 # 수납 관리
├── progress/                # 진도표 관리
├── maintenance/             # 시설 관리
├── templates/               # HTML 템플릿
├── static/                  # 정적 파일
│   ├── css/
│   └── fonts/
├── media/                   # 업로드 파일
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── manage.py
```

## 데이터베이스 모델 관계

```
Student ─┬─ BookSale ─── Book ─── BookSupplier
         ├─ StudentProgress ─── ProgressEntry
         ├─ Grade
         └─ Payment ─── PaymentHistory

Teacher ─┬─ Attendance
         ├─ Salary
         └─ ProgressEntry

Book ─── BookProblem ─── ProblemType

Room ─── Maintenance
```

## 개발 가이드

### 새 앱 추가
```bash
python manage.py startapp app_name
```

### 마이그레이션
```bash
python manage.py makemigrations
python manage.py migrate
```

### 테스트
```bash
python manage.py test
```

### 정적 파일 수집
```bash
python manage.py collectstatic
```

## 라이선스

Private - All Rights Reserved

## 작성자

MClass Academy
