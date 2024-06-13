import mysql.connector


class MySQL:
    def __init__(
        self, user="shane", password="", database="academicworld", host="localhost"
    ):
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        self.cnx = None
        self.cursor = None

    def connect(self):
        try:
            self.cnx = mysql.connector.connect(
                user=self.user,
                password=self.password,
                database=self.database,
                host=self.host,
            )
            self.cursor = self.cnx.cursor()
        except mysql.connector.Error as err:
            print(err)
            return False
        else:
            return True

    def execute_query(self, query):
        if self.cursor:
            self.cursor.execute(query)
            return self.cursor.fetchall()

        return None

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.cnx:
            self.cnx.close()
