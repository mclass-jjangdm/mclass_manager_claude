# MClass Manager - Cafe24 Ubuntu VPS 배포 가이드

이 문서는 Cafe24 Ubuntu VPS에 MClass Manager를 Docker로 배포하는 과정을 상세히 설명합니다.
실제 배포 경험을 바탕으로 발생했던 문제들과 해결 방법을 포함합니다.

## 목차

1. [서버 사양 및 준비](#1-서버-사양-및-준비)
2. [서버 초기 설정](#2-서버-초기-설정)
3. [프로젝트 배포](#3-프로젝트-배포)
4. [SSL 인증서 설정 (HTTPS)](#4-ssl-인증서-설정-https)
5. [Google Drive API 설정](#5-google-drive-api-설정)
6. [트러블슈팅](#6-트러블슈팅)
7. [유지보수](#7-유지보수)

---

## 1. 서버 사양 및 준비

### 1.1 권장 서버 사양 (Cafe24 Ubuntu VPS)
- **OS**: Ubuntu 22.04 LTS
- **RAM**: 2GB 이상
- **Storage**: 40GB 이상
- **Traffic**: 500GB/월 이상

### 1.2 Cafe24 서버 구매 후 확인사항
- 서버 IP 주소 (예: `1.234.65.17`)
- 서버 도메인 (예: `mclassmanager.cafe24.com`)
- root 계정 비밀번호

### 1.3 Cafe24 방화벽 설정 (중요!)
Cafe24 관리 콘솔에서 다음 포트를 허용해야 합니다:
- **80** (HTTP)
- **443** (HTTPS)

설정 경로: `Cafe24 관리 콘솔 > 서버 관리 > 방화벽 설정 > 포트 추가`

---

## 2. 서버 초기 설정

### 2.1 SSH 접속
```bash
ssh root@서버IP
# 예: ssh root@1.234.65.17
```

### 2.2 시스템 업데이트
```bash
apt update && apt upgrade -y
```

### 2.3 Docker 설치
```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose 설치 (최신 버전)
apt install docker-compose-plugin -y

# 설치 확인
docker --version
docker compose version
```

### 2.4 Git 설치
```bash
apt install git -y
```

---

## 3. 프로젝트 배포

### 3.1 프로젝트 클론
```bash
cd ~
git clone https://github.com/mclass-jjangdm/mclass_manager_claude.git
cd mclass_manager_claude
```

### 3.2 환경변수 파일 생성
```bash
nano .env
```

`.env` 파일 내용:
```bash
# Django 설정
SECRET_KEY=your-secret-key-here-make-it-long-and-random
DEBUG=False

# 데이터베이스 설정
DB_NAME=mclass_manager_db
DB_USER=root
DB_PASSWORD=your-secure-db-password

# 호스트 설정 (Cafe24 도메인으로 변경)
ALLOWED_HOSTS=mclassmanager.cafe24.com,1.234.65.17,localhost,127.0.0.1

# CSRF 설정 (초기에는 HTTP로 시작)
CSRF_TRUSTED_ORIGINS=http://1.234.65.17,http://mclassmanager.cafe24.com

# 보안 설정 (SSL 설정 전에는 False)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Google Drive API (선택사항 - 나중에 설정)
# GOOGLE_SERVICE_ACCOUNT_FILE=/app/credentials/google_service_account.json
# GOOGLE_DRIVE_ROOT_FOLDER_ID=your-folder-id
```

**SECRET_KEY 생성 방법:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 3.3 Nginx 설정 (초기 HTTP 전용)
SSL 인증서 발급 전에는 HTTP 전용 설정을 사용합니다:
```bash
cp nginx/nginx.init.conf nginx/nginx.conf
```

`nginx/nginx.conf` 내용 확인 및 서버명 수정:
```bash
nano nginx/nginx.conf
```

`server_name`을 실제 도메인/IP로 변경:
```nginx
server_name mclassmanager.cafe24.com 1.234.65.17 localhost;
```

### 3.4 필요한 디렉토리 생성
```bash
mkdir -p logs
mkdir -p credentials
```

### 3.5 Docker 컨테이너 빌드 및 실행
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### 3.6 데이터베이스 마이그레이션 확인
```bash
docker compose -f docker-compose.prod.yml logs web
```

### 3.7 관리자 계정 생성
```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### 3.8 접속 테스트
브라우저에서 `http://서버IP` 또는 `http://도메인` 접속

---

## 4. SSL 인증서 설정 (HTTPS)

### 4.1 Let's Encrypt 인증서 발급 준비
certbot이 인증 파일을 쓸 수 있도록 디렉토리 구조 생성:
```bash
docker compose -f docker-compose.prod.yml exec nginx sh -c "mkdir -p /var/www/certbot/.well-known/acme-challenge"
```

### 4.2 인증 경로 테스트
```bash
# 테스트 파일 생성
docker compose -f docker-compose.prod.yml exec nginx sh -c "echo 'test' > /var/www/certbot/.well-known/acme-challenge/test.txt"

# 외부 접근 테스트
curl http://도메인/.well-known/acme-challenge/test.txt
# "test"가 출력되면 성공
```

### 4.3 SSL 인증서 발급
**중요: `--entrypoint ""`를 반드시 사용해야 합니다!**
```bash
docker compose -f docker-compose.prod.yml run --rm --entrypoint "" certbot certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d mclassmanager.cafe24.com \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email
```

성공 시 메시지:
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/도메인/fullchain.pem
Key is saved at: /etc/letsencrypt/live/도메인/privkey.pem
```

### 4.4 SSL용 Nginx 설정 적용
```bash
# SSL 설정 파일 생성
cat > nginx/nginx.conf << 'EOF'
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name mclassmanager.cafe24.com 1.234.65.17 localhost;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name mclassmanager.cafe24.com;

    ssl_certificate /etc/letsencrypt/live/mclassmanager.cafe24.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mclassmanager.cafe24.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    client_max_body_size 10M;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json application/xml;

    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /app/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF
```

**주의: 도메인(`mclassmanager.cafe24.com`)을 실제 도메인으로 변경하세요!**

### 4.5 Nginx 재시작
```bash
docker compose -f docker-compose.prod.yml restart nginx
```

### 4.6 HTTPS 테스트
```bash
curl -I https://도메인
# HTTP/2 200 이 나오면 성공
```

### 4.7 Django 보안 설정 활성화
`.env` 파일 수정:
```bash
nano .env
```

다음 값들을 변경:
```bash
CSRF_TRUSTED_ORIGINS=https://mclassmanager.cafe24.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

Django 재시작:
```bash
docker compose -f docker-compose.prod.yml restart web
```

---

## 5. Google Drive API 설정

### 5.1 Google Cloud Console 설정
1. https://console.cloud.google.com/ 접속
2. 새 프로젝트 생성 (예: `MClass-Manager`)
3. **APIs & Services** > **Library** > **Google Drive API** 검색 후 **Enable**

### 5.2 서비스 계정 생성
1. **APIs & Services** > **Credentials**
2. **Create Credentials** > **Service Account**
3. 서비스 계정 이름 입력 (예: `mclass-drive-service`)
4. 생성 완료 후 해당 서비스 계정 클릭
5. **Keys** 탭 > **Add Key** > **Create new key** > **JSON**
6. JSON 파일 다운로드

### 5.3 서버에 키 파일 업로드
로컬 터미널에서:
```bash
scp /path/to/downloaded-key.json root@서버IP:~/mclass_manager_claude/credentials/google_service_account.json
```

또는 서버에서 직접 파일 생성:
```bash
nano ~/mclass_manager_claude/credentials/google_service_account.json
# JSON 내용 붙여넣기
```

### 5.4 Google Drive 폴더 설정
1. Google Drive에서 MClass용 폴더 생성
2. JSON 파일의 `client_email` 값 확인:
   ```bash
   cat credentials/google_service_account.json | grep client_email
   ```
3. 해당 이메일로 폴더 공유 (**편집자** 권한)
4. 폴더 URL에서 ID 복사:
   - URL: `https://drive.google.com/drive/folders/1ABC123xyz`
   - 폴더 ID: `1ABC123xyz`

### 5.5 환경변수 설정
`.env` 파일에 추가:
```bash
GOOGLE_SERVICE_ACCOUNT_FILE=/app/credentials/google_service_account.json
GOOGLE_DRIVE_ROOT_FOLDER_ID=복사한-폴더-ID
```

### 5.6 컨테이너 재시작
```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### 5.7 설정 확인
```bash
# credentials 폴더가 컨테이너에 마운트되었는지 확인
docker compose -f docker-compose.prod.yml exec web ls -la /app/credentials/
```

---

## 6. 트러블슈팅

### 6.1 NumPy CPU 호환성 오류
**증상:**
```
Illegal instruction (core dumped)
```

**원인:** NumPy 2.x가 서버 CPU(X86_V2)와 호환되지 않음

**해결:** `requirements.txt`에서 NumPy/Pandas 버전 다운그레이드
```
numpy==1.26.4
pandas==2.2.3
```

### 6.2 CSRF 403 Forbidden 오류
**증상:** 로그인 시 `Forbidden (403)` 오류

**원인:** CSRF_TRUSTED_ORIGINS 미설정 또는 쿠키 보안 설정 문제

**해결:**
1. `.env`에 `CSRF_TRUSTED_ORIGINS` 설정
2. HTTP 사용 시 쿠키 보안 설정 비활성화:
   ```bash
   SESSION_COOKIE_SECURE=False
   CSRF_COOKIE_SECURE=False
   ```

### 6.3 SSL 인증서 발급 실패 - "No renewals were attempted"
**증상:** certbot 실행 시 아무 일도 일어나지 않음

**원인:** docker-compose.prod.yml의 certbot entrypoint가 갱신 모드로 설정됨

**해결:** `--entrypoint ""`를 사용하여 기본 entrypoint 무시
```bash
docker compose -f docker-compose.prod.yml run --rm --entrypoint "" certbot certbot certonly ...
```

### 6.4 SSL 인증서 발급 실패 - 404 Not Found
**증상:** Let's Encrypt 인증 실패

**원인:** `.well-known/acme-challenge/` 경로 접근 불가

**해결:**
1. Nginx 설정에 해당 location 블록 확인
2. certbot_www 볼륨이 `:ro` (읽기전용)가 아닌지 확인
3. 디렉토리 구조 수동 생성:
   ```bash
   docker compose -f docker-compose.prod.yml exec nginx sh -c "mkdir -p /var/www/certbot/.well-known/acme-challenge"
   ```

### 6.5 서버 파일이 GitHub과 동기화되지 않음
**증상:** `git pull`을 해도 파일이 변경되지 않음

**원인:** 로컬 변경사항과 충돌 또는 이미 최신이라고 착각

**해결:**
```bash
git fetch origin
git checkout origin/main -- 파일명
```

### 6.6 Docker 볼륨 마운트 미적용
**증상:** docker-compose.yml 수정 후에도 적용 안됨

**원인:** 컨테이너가 재생성되지 않음

**해결:**
```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### 6.7 마이그레이션 충돌 - "Table already exists"
**증상:** `migrate` 실행 시 테이블 이미 존재 오류

**해결:** 마이그레이션 기록을 수동으로 삽입
```bash
docker compose -f docker-compose.prod.yml exec db mysql -u root -p

USE mclass_manager_db;
INSERT INTO django_migrations (app, name, applied) VALUES ('앱이름', '마이그레이션명', NOW());
```

---

## 7. 유지보수

### 7.1 로그 확인
```bash
# 전체 로그
docker compose -f docker-compose.prod.yml logs

# 특정 서비스 로그
docker compose -f docker-compose.prod.yml logs web
docker compose -f docker-compose.prod.yml logs nginx

# 실시간 로그
docker compose -f docker-compose.prod.yml logs -f web
```

### 7.2 컨테이너 상태 확인
```bash
docker compose -f docker-compose.prod.yml ps
```

### 7.3 서비스 재시작
```bash
# 전체 재시작
docker compose -f docker-compose.prod.yml restart

# 특정 서비스만 재시작
docker compose -f docker-compose.prod.yml restart web
```

### 7.4 코드 업데이트 배포
```bash
cd ~/mclass_manager_claude
git pull origin main
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
```

### 7.5 데이터베이스 백업
```bash
docker compose -f docker-compose.prod.yml exec db mysqldump -u root -p mclass_manager_db > backup_$(date +%Y%m%d).sql
```

### 7.6 데이터베이스 복원
```bash
docker compose -f docker-compose.prod.yml exec -T db mysql -u root -p mclass_manager_db < backup_file.sql
```

### 7.7 SSL 인증서 갱신 (자동)
certbot 컨테이너가 12시간마다 자동으로 갱신을 시도합니다.
수동 갱신이 필요한 경우:
```bash
docker compose -f docker-compose.prod.yml run --rm --entrypoint "" certbot certbot renew
docker compose -f docker-compose.prod.yml restart nginx
```

### 7.8 디스크 정리
```bash
# 사용하지 않는 Docker 리소스 정리
docker system prune -a

# 오래된 로그 삭제
find ~/mclass_manager_claude/logs -name "*.log" -mtime +30 -delete
```

---

## 부록: 주요 파일 경로

| 파일/디렉토리 | 설명 |
|---|---|
| `~/mclass_manager_claude/` | 프로젝트 루트 |
| `.env` | 환경변수 설정 (비밀번호 등) |
| `docker-compose.prod.yml` | Docker 서비스 설정 |
| `nginx/nginx.conf` | Nginx 설정 |
| `credentials/` | Google API 인증 파일 |
| `logs/` | 애플리케이션 로그 |

---

## 부록: 유용한 명령어 모음

```bash
# 컨테이너 내부 접속
docker compose -f docker-compose.prod.yml exec web bash
docker compose -f docker-compose.prod.yml exec db bash

# Django 쉘
docker compose -f docker-compose.prod.yml exec web python manage.py shell

# 정적 파일 재수집
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 슈퍼유저 비밀번호 변경
docker compose -f docker-compose.prod.yml exec web python manage.py changepassword admin
```

---

**문서 작성일:** 2026-02-14
**최종 수정일:** 2026-02-14
**작성자:** Claude AI & 개발자
