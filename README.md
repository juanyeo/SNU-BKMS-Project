# SNU-BKMS-Project
Peer Q&amp;A 프로젝트 Repository (김권호, 박수영, 송무호, 여주안, 최문원)

## 🚀 프로젝트 Import
1. (장고 설치) $ python3 -m pip install django
2. (DB 연결 설정) 로컬 PostgreSQL을 qa_project > settings.py 의 DATABASES 설정과 매칭
- PgAdmin에서 "QuestionDB" 이름으로 데이터베이스 생성
- 유저이름: postgres, 패스워드: postgres (현재 로컬DB의 설정이 다를 경우 setting.py 변경)
3. (DB 테이블 생성) $ python3 manage.py makemigrations 
4. (DB 테이블 생성) $ python3 manage.py migrate
- Migration 결과 QuestionDB에 12개의 테이블이 생성됨 (PgAdmin에서 확인)
5. (실행) $ python3 manage.py runserver
- 브라우저에서 http://127.0.0.1:8000/ 입력
