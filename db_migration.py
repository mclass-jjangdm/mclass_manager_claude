import json
import mysql.connector
import mclass_settings
import traceback

def connect_to_db():
    """MariaDB 연결 설정"""
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password= mclass_settings.db_password,
        database='mclass_manager_db',
        charset='utf8mb4',
        collation='utf8mb4_general_ci'
    )

def get_column_names(cursor, table_name):
    """테이블의 실제 컬럼 이름 가져오기"""
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    return [column[0] for column in cursor.fetchall()]

def process_fields(fields, table_name, column_names):
    """필드 데이터 처리"""
    processed = {}
    
    # auth.user 모델 특별 처리
    if table_name == 'auth_user':
        fields.pop('groups', None)
        fields.pop('user_permissions', None)
        if 'first_name' in fields and not fields['first_name']:
            fields['first_name'] = ''
        if 'last_name' in fields and not fields['last_name']:
            fields['last_name'] = ''

    # ForeignKey 필드 처리를 위한 매핑
    fk_fields = {
        'teacher': 'teacher_id',
        'school': 'school_id',
        'bank': 'bank_id',
        'room': 'room_id',
        'subject': 'subject_id',
        'publisher': 'publisher_id'
    }
    
    # 필드 변환
    for key, value in fields.items():
        # ForeignKey 필드인 경우
        if key in fk_fields and fk_fields[key] in column_names:
            processed[fk_fields[key]] = value
        # 일반 필드인 경우
        elif key in column_names:
            processed[key] = value
    
    return processed

def migrate_data():
    """데이터 마이그레이션 실행"""
    conn = None
    cursor = None
    
    try:
        # 데이터베이스 연결
        print("Connecting to database...")
        conn = connect_to_db()
        cursor = conn.cursor()
        
        # JSON 파일 읽기
        print("Reading backup_data.json file...")
        with open('backup_data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 외래 키 체크 비활성화
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        
        # 모델 순서 정의
        migration_order = [
            'auth.user',
            'common.bank',
            'common.publisher',
            'common.subject',
            'common.school',
            'common.purchaselocation',
            'teachers.teacher',
            'teachers.attendance',
            'teachers.salary',
            'maintenance.room',
            'maintenance.maintenance',
            'books.book',
            'students.student'
        ]
        
        for model_name in migration_order:
            table_name = model_name.replace('.', '_')
            print(f"\nProcessing {table_name}...")
            
            # 테이블의 실제 컬럼 이름 가져오기
            column_names = get_column_names(cursor, table_name)
            print(f"Available columns: {', '.join(column_names)}")
            
            # 테이블 비우기
            cursor.execute(f"TRUNCATE TABLE {table_name}")
            
            # 현재 모델의 데이터만 필터링
            model_data = [item for item in data if item['model'] == model_name]
            print(f"Found {len(model_data)} records to migrate")
            
            success_count = 0
            error_count = 0
            
            for item in model_data:
                try:
                    fields = process_fields(item['fields'].copy(), table_name, column_names)
                    pk = item['pk']
                    fields['id'] = pk
                    
                    # SQL 쿼리 생성
                    columns = ', '.join(fields.keys())
                    placeholders = ', '.join(['%s'] * len(fields))
                    values = list(fields.values())
                    
                    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    
                    cursor.execute(sql, values)
                    success_count += 1
                    print(f"Inserted record {pk} into {table_name}")
                    
                except mysql.connector.Error as err:
                    error_count += 1
                    print(f"Error inserting record {pk} into {table_name}: {err}")
                    print("SQL:", sql)
                    print("Values:", values)
            
            print(f"\nResults for {table_name}:")
            print(f"Successfully inserted: {success_count}")
            print(f"Failed: {error_count}")
            
            # 각 테이블마다 커밋
            conn.commit()
            print(f"Changes committed for {table_name}")
        
        # 외래 키 체크 활성화
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        print("\nMigration completed successfully")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_data()