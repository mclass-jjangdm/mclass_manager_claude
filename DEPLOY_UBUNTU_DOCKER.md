# 카페24 Ubuntu VPS Docker 배포 가이드

## 개요
- **서버**: 카페24 Ubuntu VPS (2GB RAM, 40GB Storage)
- **구성**: Docker + Nginx + Gunicorn + MariaDB
- **자동 배포**: GitHub Actions

---

## 1. 서버 초기 설정

### 1.1 SSH 접속
```bash
ssh root@서버IP주소
```

### 1.2 시스템 업데이트
```bash
apt update && apt upgrade -y
```

### 1.3 필수 패키지 설치
```bash
apt install -y git curl vim
```

### 1.4 일반 사용자 생성 (권장)
```bash
adduser mclass
usermod -aG sudo mclass
su - mclass
```

---

## 2. Docker 설치

### 2.1 Docker 설치
```bash
# Docker 공식 설치 스크립트
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# 재로그인 후 확인
docker --version
```

### 2.2 Docker Compose 설치
```bash
# Docker Compose V2는 Docker에 포함됨
docker compose version
```

---

## 3. 프로젝트 배포

### 3.1 프로젝트 클론
```bash
cd ~
git clone https://github.com/mclass-jjangdm/mclass_manager_claude.git
cd mclass_manager_claude
```

### 3.2 환경 변수 설정
```bash
cp .env.example .env
nano .env
```

**필수 설정값:**
```bash
# 반드시 변경해야 하는 값들
DEBUG=False
SECRET_KEY=생성한-시크릿-키-여기에-입력
DB_PASSWORD=안전한-데이터베이스-비밀번호
ALLOWED_HOSTS=mclass.co.kr,www.mclass.co.kr,서버IP
```

**SECRET_KEY 생성:**
```bash
python3 -c "from secrets import token_urlsafe; print(token_urlsafe(50))"
```

### 3.3 로그 디렉토리 생성
```bash
mkdir -p logs
chmod 755 logs
```

---

## 4. SSL 인증서 발급 (Let's Encrypt)

### 4.1 초기 Nginx 설정 (SSL 발급 전)
```bash
# SSL 없는 초기 설정 사용
cp nginx/nginx.init.conf nginx/nginx.conf
```

### 4.2 컨테이너 시작 (HTTP만)
```bash
docker compose -f docker-compose.prod.yml up -d db web nginx
```

### 4.3 SSL 인증서 발급
```bash
# 도메인이 서버를 가리키고 있어야 함
# 카페24 도메인 예시 (실제 도메인으로 변경)
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d mclassmanager.cafe24.com \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email
```

### 4.4 SSL 설정 적용
```bash
# 기존 설정 백업
cp nginx/nginx.conf nginx/nginx.conf.backup

# SSL 포함 설정으로 교체 (이미 SSL 설정이 포함된 원본 사용)
git checkout nginx/nginx.conf

# Nginx 재시작
docker compose -f docker-compose.prod.yml restart nginx
```

---

## 5. 데이터베이스 초기화

### 5.1 마이그레이션 실행
```bash
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### 5.2 슈퍼유저 생성
```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### 5.3 정적 파일 수집
```bash
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## 6. GitHub Actions 자동 배포 설정

### 6.1 GitHub Secrets 설정
GitHub 리포지토리 > Settings > Secrets and variables > Actions에서 추가:

| Secret 이름 | 값 |
|------------|-----|
| `SERVER_HOST` | 서버 IP 주소 |
| `SERVER_USER` | SSH 사용자명 (예: mclass) |
| `SERVER_SSH_KEY` | SSH 개인키 내용 |
| `SERVER_PORT` | SSH 포트 (기본: 22) |

### 6.2 SSH 키 생성 (서버에서)
```bash
# 서버에서 실행
ssh-keygen -t ed25519 -C "github-actions"

# 공개키를 authorized_keys에 추가
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys

# 개인키 내용을 GitHub Secret에 등록
cat ~/.ssh/id_ed25519
```

### 6.3 배포 테스트
- `main` 브랜치에 push하면 자동 배포
- 또는 GitHub Actions 탭에서 수동 실행 (Run workflow)

---

## 7. 운영 명령어

### 7.1 컨테이너 관리
```bash
# 상태 확인
docker compose -f docker-compose.prod.yml ps

# 로그 확인
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f nginx

# 재시작
docker compose -f docker-compose.prod.yml restart

# 중지
docker compose -f docker-compose.prod.yml down

# 시작
docker compose -f docker-compose.prod.yml up -d
```

### 7.2 Django 관리
```bash
# Django 쉘
docker compose -f docker-compose.prod.yml exec web python manage.py shell

# 마이그레이션
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# 정적 파일 수집
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### 7.3 데이터베이스 백업
```bash
# 백업
docker compose -f docker-compose.prod.yml exec db mysqldump -u root -p$DB_PASSWORD mclass_manager_db > backup_$(date +%Y%m%d).sql

# 복원
docker compose -f docker-compose.prod.yml exec -T db mysql -u root -p$DB_PASSWORD mclass_manager_db < backup_20250212.sql
```

---

## 8. 문제 해결

### 8.1 502 Bad Gateway
```bash
# Django 컨테이너 상태 확인
docker compose -f docker-compose.prod.yml logs web

# 컨테이너 재시작
docker compose -f docker-compose.prod.yml restart web
```

### 8.2 Static 파일 404
```bash
# 정적 파일 재수집
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Nginx 재시작
docker compose -f docker-compose.prod.yml restart nginx
```

### 8.3 데이터베이스 연결 오류
```bash
# DB 컨테이너 상태 확인
docker compose -f docker-compose.prod.yml logs db

# 연결 테스트
docker compose -f docker-compose.prod.yml exec web python manage.py dbshell
```

### 8.4 메모리 부족
```bash
# 메모리 사용량 확인
docker stats

# 사용하지 않는 리소스 정리
docker system prune -a
```

---

## 9. 보안 체크리스트

- [ ] `DEBUG=False` 설정 확인
- [ ] `SECRET_KEY` 변경 완료
- [ ] `ALLOWED_HOSTS` 설정 확인
- [ ] 방화벽 설정 (80, 443만 허용)
- [ ] SSH 키 인증만 허용 (비밀번호 로그인 비활성화)
- [ ] SSL 인증서 자동 갱신 확인
- [ ] 정기 백업 설정

---

## 10. 유용한 팁

### 10.1 방화벽 설정 (ufw)
```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 10.2 Swap 메모리 추가 (선택사항)
```bash
# 2GB Swap 생성
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 10.3 자동 보안 업데이트
```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```
