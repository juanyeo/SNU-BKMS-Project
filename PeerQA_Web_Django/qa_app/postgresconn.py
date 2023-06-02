import pandas as pd
import psycopg2
from qa_project.settings import DATABASES

def tag_ranking():
    
    query = """
    
    select tag , count(*) from qa_app_question
	where user_id = 2
    group by tag
    order by count desc
    limit 5
    
    """
    df = get_dataframe(query)
    tag_list = list(df['tag'])
    count_list = list(df['count'])
    return {"tag_list":tag_list, "count_list":count_list}


def get_dataframe(given_query):
    """
    query example:
    
    query = '''
    select * from courses
    where courses.cid > 5
    limit 5; 
    '''
    --> 줄바꿈하면서 쿼리 입력해도 알아서 변환함.
    
    """
    query = given_query.replace('\n', ' ')
    
    conn = psycopg2.connect(
        host=DATABASES['default']['HOST'],
        database=DATABASES['default']['NAME'],
        user=DATABASES['default']['User'],
        password=DATABASES['default']['PASSWORD'],
        port=DATABASES['default']['PORT']
    )
    
    try:
        # 테이블을 Pandas.Dataframe으로 추출
        df = pd.read_sql(query,conn)

    except psycopg2.Error as e:
        # 데이터베이스 에러 처리
        print("DB error: ", e)
        
    finally:
        # 데이터베이스 연결 해제 필수!!
        conn.close()

    return df
