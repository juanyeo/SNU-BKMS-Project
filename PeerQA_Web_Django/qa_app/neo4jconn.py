from neo4j import GraphDatabase

class Neo4jConnection:
    
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)
        
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
        
    def execute(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try: 
            session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally: 
            if session is not None:
                session.close()
        return response


class Database2():
    def __init__(self):
            self.cursor = Neo4jConnection(
                uri='bolt://localhost:7687',
                user='neo4j',
                pwd='8752fm$$fm'
            )

    def __del__(self):
        self.cursor.close()

    def update(self):
        apoc_string = 'CALL apoc.load.jdbc("jdbc:postgresql://147.47.200.145:34543/teamdb6?user=team6&password=snupeer6",'
        node1 = apoc_string + '"qa_app_user") YIELD row MERGE (u:User {id: toInteger(row.id), uname:row.username})'
        node2 = apoc_string + '"qa_app_question") YIELD row MERGE (q:Question {id: toInteger(row.id), user_id:toInteger(row.user_id), tag:row.tag})'
        node3 = apoc_string + '"qa_app_comment") YIELD row MERGE (c:Comment {id: toInteger(row.id), question_id:toInteger(row.question_id), user_id:toInteger(row.user_id)})'
        rel1 = apoc_string + '"qa_app_user") YIELD row MATCH (u:User {id:toInteger(row.id)}) MATCH (q:Question {user_id:toInteger(row.id)}) MERGE (u)-[:ASK]->(q)'
        rel2 = apoc_string + '"qa_app_question") YIELD row MATCH (q:Question {id:toInteger(row.id)}) MATCH (c:Comment {question_id:toInteger(row.id)}) MERGE (c)-[:Relate]->(q)'
        rel3 = apoc_string + '"qa_app_user") YIELD row MATCH (u:User {id:toInteger(row.id)}) MATCH (c:Comment {user_id:toInteger(row.id)}) MERGE (u)-[:Answer]->(c)'
        self.cursor.execute(node1)
        self.cursor.execute(node2)
        self.cursor.execute(node3)
        self.cursor.execute(rel1)
        self.cursor.execute(rel2)
        self.cursor.execute(rel3)