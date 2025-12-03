# MClass Manager - Docker 배포 가이드

이 프로젝트는 Docker와 Docker Compose를 사용하여 쉽게 배포할 수 있습니다.

## 사전 요구사항

- Docker Desktop (Windows/Mac) 또는 Docker Engine (Linux)
- Docker Compose

## 빠른 시작

### 1. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 필요한 값을 설정합니다:

```bash
cp .env.example .env
```

`.env` 파일 수정:
```env
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-here
DB_PASSWORD=your-strong-database-password
```

### 2. Docker 컨테이너 실행

```bash
# 이미지 빌드 및 컨테이너 시작
docker-compose up -d --build

# 로그 확인
docker-compose logs -f
```

### 3. 애플리케이션 접속

브라우저에서 `http://localhost:8000` 접속

기본 관리자 계정:
- 사용자명: `admin`
- 비밀번호: `admin`

## 주요 명령어

### 컨테이너 관리

```bash
# 컨테이너 시작
docker-compose up -d

# 컨테이너 중지
docker-compose down

# 컨테이너 및 볼륨 삭제 (주의: 데이터 손실)
docker-compose down -v

# 컨테이너 재시작
docker-compose restart

# 로그 확인
docker-compose logs -f web
docker-compose logs -f db
```

### Django 관리 명령어

```bash
# Django 쉘 접속
docker-compose exec web python manage.py shell

# 마이그레이션 생성
docker-compose exec web python manage.py makemigrations

# 마이그레이션 적용
docker-compose exec web python manage.py migrate

# 슈퍼유저 생성
docker-compose exec web python manage.py createsuperuser

# Static 파일 수집
docker-compose exec web python manage.py collectstatic --noinput
```

### 데이터베이스 관리

```bash
# MySQL 콘솔 접속
docker-compose exec db mysql -u root -p

# 데이터베이스 백업
docker-compose exec db mysqldump -u root -p mclass_manager_db > backup.sql

# 데이터베이스 복원
docker-compose exec -T db mysql -u root -p mclass_manager_db < backup.sql
```

## 프로덕션 배포

프로덕션 환경에서는 다음 설정을 변경해야 합니다:

1. **`.env` 파일 수정:**
```env
DEBUG=False
SECRET_KEY=매우-강력한-비밀키-생성
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_PASSWORD=강력한-데이터베이스-비밀번호
```

2. **docker-compose.yml 수정 (옵션):**
   - Nginx 리버스 프록시 추가
   - SSL/TLS 인증서 설정
   - 포트 변경

3. **보안 강화:**
   - 기본 관리자 계정 비밀번호 변경
   - 방화벽 설정
   - 정기적인 백업 설정

## 문제 해결

### 컨테이너가 시작되지 않는 경우

```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs

# 컨테이너 재빌드
docker-compose up -d --build --force-recreate
```

### 데이터베이스 연결 오류

```bash
# DB 컨테이너가 준비될 때까지 대기
docker-compose up db
# 다른 터미널에서
docker-compose up web
```

### Static 파일이 로드되지 않는 경우

```bash
docker-compose exec web python manage.py collectstatic --noinput
docker-compose restart web
```

## 개발 환경

개발 시에는 로컬 파일 변경사항이 자동으로 반영됩니다:

```bash
# 개발 모드로 실행
docker-compose up

# 코드 변경 후 자동 재시작됨
```

## 볼륨

Docker Compose는 다음 볼륨을 생성합니다:

- `mysql_data`: MySQL 데이터베이스 데이터
- `static_volume`: Django static 파일
- `media_volume`: 사용자 업로드 파일

볼륨 확인:
```bash
docker volume ls
```

## 네트워크

컨테이너들은 기본 네트워크로 연결됩니다:
- `web` 컨테이너: 포트 8000
- `db` 컨테이너: 포트 3306

## 지원

문제가 발생하면 GitHub Issues를 통해 문의해주세요.
