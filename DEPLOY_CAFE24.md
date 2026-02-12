# 카페24 가상 호스팅 배포 가이드

## 1. 사전 준비

### 카페24 호스팅 요구사항
- Python 3.10 이상 지원 플랜
- MySQL 데이터베이스
- SSH 접속 가능

### 로컬에서 준비
```bash
# 정적 파일 수집
python manage.py collectstatic --noinput

# 의존성 파일 확인
pip freeze > requirements.txt
```

## 2. 카페24 서버 설정

### SSH 접속
```bash
ssh 사용자ID@사용자ID.cafe24.com
```

### 가상환경 생성
```bash
cd ~
python3 -m venv venv
source venv/bin/activate
```

### 프로젝트 업로드
```bash
# FTP 또는 Git으로 프로젝트 업로드
cd ~/www
git clone https://github.com/your-repo/mclass_manager_claude.git
# 또는 FTP로 업로드
```

### 의존성 설치
```bash
source ~/venv/bin/activate
cd ~/www/mclass_manager_claude
pip install -r requirements.txt
```

## 3. 환경변수 설정

### .env 파일 생성
```bash
cp .env.example .env
nano .env
```

### 필수 설정값
```
DEBUG=False
SECRET_KEY=생성한-시크릿-키
DJANGO_SETTINGS_MODULE=mclass_manager.settings_production
ALLOWED_HOSTS=mclass.co.kr,www.mclass.co.kr

DB_NAME=카페24DB명
DB_USER=카페24DB사용자
DB_PASSWORD=카페24DB비밀번호
DB_HOST=localhost
```

## 4. 데이터베이스 설정

### 마이그레이션 실행
```bash
source ~/venv/bin/activate
cd ~/www/mclass_manager_claude
python manage.py migrate
```

### 슈퍼유저 생성
```bash
python manage.py createsuperuser
```

## 5. Passenger WSGI 설정

### passenger_wsgi.py 수정
```python
# 실제 경로로 수정
PROJECT_PATH = '/home/사용자ID/www/mclass_manager_claude'
VENV_PATH = '/home/사용자ID/venv/lib/python3.10/site-packages'
```

### .htaccess 수정
```apache
PassengerAppRoot /home/사용자ID/www/mclass_manager_claude
PassengerPython /home/사용자ID/venv/bin/python3
```

## 6. 정적 파일 설정

### 정적 파일 수집
```bash
python manage.py collectstatic --noinput
```

### 심볼릭 링크 생성 (필요 시)
```bash
cd ~/www
ln -s mclass_manager_claude/staticfiles static
ln -s mclass_manager_claude/media media
```

## 7. 폴더 권한 설정

```bash
chmod 755 ~/www/mclass_manager_claude
chmod 755 ~/www/mclass_manager_claude/staticfiles
chmod 755 ~/www/mclass_manager_claude/media
chmod 644 ~/www/mclass_manager_claude/*.py
chmod 600 ~/www/mclass_manager_claude/.env
```

## 8. 서비스 재시작

카페24 관리자 페이지에서 웹서버 재시작 또는:
```bash
touch ~/www/mclass_manager_claude/tmp/restart.txt
```

## 9. 문제 해결

### 500 에러 발생 시
1. 로그 확인: `tail -f ~/www/mclass_manager_claude/logs/django.log`
2. DEBUG=True로 임시 변경하여 상세 에러 확인
3. 권한 문제 확인

### Static 파일 404 에러
1. `collectstatic` 재실행
2. .htaccess의 Static 파일 경로 확인

### 데이터베이스 연결 오류
1. DB 호스트/포트 확인 (카페24는 보통 localhost)
2. DB 사용자 권한 확인

## 10. 유지보수

### 코드 업데이트
```bash
cd ~/www/mclass_manager_claude
git pull origin main
source ~/venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch tmp/restart.txt
```

### 백업
```bash
# DB 백업
mysqldump -u 사용자ID -p 데이터베이스명 > backup_$(date +%Y%m%d).sql

# 미디어 파일 백업
tar -czvf media_backup_$(date +%Y%m%d).tar.gz media/
```
