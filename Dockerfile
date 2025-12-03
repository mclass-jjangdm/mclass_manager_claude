# Python 3.13 slim 이미지 사용
FROM python:3.13-slim

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 작업 디렉터리 설정
WORKDIR /app

# 시스템 패키지 설치 (MySQL 클라이언트 라이브러리 포함)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 프로젝트 파일 복사
COPY . .

# static 파일 수집을 위한 디렉터리 생성
RUN mkdir -p /app/staticfiles /app/media

# 포트 노출
EXPOSE 8000

# 엔트리포인트 스크립트 실행 권한 부여
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 엔트리포인트 설정
ENTRYPOINT ["/entrypoint.sh"]

# 기본 명령어
CMD ["gunicorn", "mclass_manager.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
