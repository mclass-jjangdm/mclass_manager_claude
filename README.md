# MClass Manager (엠클래스 학원 관리 시스템)

**MClass Manager**는 학원 운영을 효율적으로 돕기 위해 개발된 통합 관리 시스템입니다. 학생 및 강사 관리부터 교재 재고, 수납, 급여 정산까지 학원 운영에 필요한 핵심 기능을 제공합니다.

## 📖 프로젝트 소개

이 프로젝트는 Django와 MySQL을 기반으로 구축되었으며, Docker를 통해 손쉽게 배포하고 운영할 수 있도록 설계되었습니다. 데이터의 엑셀 가져오기/내보내기, PDF 보고서 생성, 바코드/QR 코드를 활용한 교재 관리 등 실무에 최적화된 기능들을 포함하고 있습니다.

## 🚀 주요 기능

### 1. 👨‍🎓 학생 관리 (Students)
- **학생 정보 관리:** 인적사항, 학교, 학년, 상담 내역 기록
- **엑셀 연동:** 대량의 학생 데이터를 엑셀로 일괄 등록 및 내보내기 지원
- **파일 첨부:** 학생별 개인 파일 관리 기능
- **상태 관리:** 재원/퇴원/휴원 상태에 따른 필터링 및 관리

### 2. 👩‍🏫 강사 관리 (Teachers)
- **근태 관리:** 일별 출퇴근 기록 및 근무 시간 자동 계산
- **급여 정산:** 근무 시간과 기본급/추가급을 기반으로 월별 급여 자동 산출
- **보고서 생성:** 급여 명세서 및 근무 내역서 PDF 자동 생성 및 출력
- **강사 정보:** 이력 및 담당 과목 관리

### 3. 📚 교재 및 서점 관리 (Books & Bookstore)
- **교재 등록:** 바코드/QR 코드를 활용한 교재 정보 관리
- **재고 관리:** 입고, 출고, 반품 처리를 통한 실시간 재고 파악
- **지급 현황:** 학생별 교재 지급 내역 및 미납 내역 추적

### 4. 💰 수납 관리 (Payment)
- **수납 내역:** 교재비 및 교육비 수납 내역 기록
- **현황 파악:** 기간별 수납 현황 대시보드 제공

### 5. 🛠 시설 관리 (Maintenance)
- **강의실 관리:** 강의실별 유지보수 내역 및 상태 기록
- **기자재 관리:** 학원 내 비품 및 기자재 관리

## 🛠 기술 스택 (Tech Stack)

- **Backend:** Python 3.13, Django 5.2
- **Database:** MySQL 8.0
- **Infrastructure:** Docker, Docker Compose
- **Major Libraries:**
  - `pandas`: 데이터 엑셀 처리 및 분석
  - `reportlab`: PDF 문서 생성
  - `python-barcode` / `qrcode`: 교재 관리용 코드 생성
  - `whitenoise`: 정적 파일 서빙

## 💻 설치 및 실행 방법 (Docker)

이 프로젝트는 Docker 환경에서 실행하는 것을 권장합니다.

### 사전 요구사항
- Docker
- Docker Compose

### 1. 저장소 클론
```bash
git clone [https://github.com/mclass-jjangdm/mclass-manager.git](https://github.com/mclass-jjangdm/mclass-manager.git)
cd mclass-manager