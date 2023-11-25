import psycopg2


class DBActions:

    def __init__(self, db_name, user, password, table, host='localhost'):
        self.__db_name = db_name
        self.__user = user
        self.__password = password
        self.__host = host
        self.__table = table
        
        self.__conn = psycopg2.connect(
            dbname=self.__db_name,
            user=self.__user,
            password=self.__password,
            host=self.__host,
        )
        self.__cursor = self.__conn.cursor()
        #self._cursor.execute('SELECT current_database()')
        #print(self._cursor.fetchall())
    
    def create_notion(self, name, data):
        self.__cursor.execute(
            f'INSERT INTO {self.__table} (name, objects) '
            f'VALUES (%(name)s, %(data)s)',
            {
                'name': name,
                'data': str(data)
            }
        )
        self.__conn.commit()
        self.__conn.close()
    
    def get_notion_list(self):
        self.__cursor.execute(f'SELECT id, name, objects FROM "{self.__table}";')
        notion_list = self.__cursor.fetchall()
        #self.__conn.close()
        return notion_list

    def edit_notion(self, id):
        ...

    def delete_notion(self, id):
        self.__cursor.execute(f'DELETE FROM {self.__table} WHERE id={id};')
        self.__conn.commit()
        #self.__conn.close()