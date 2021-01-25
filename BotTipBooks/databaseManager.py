import pyodbc
from bean import User

server = 'servercc.database.windows.net'
database = 'BotTipBooksDatabase'
username = 'useradmin'
password = 'Progettocloud21'   
driver= '{ODBC Driver 17 for SQL Server}'


class DatabaseManager:
    @staticmethod
    def user_is_registered(id: str):
        register=False
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT TOP 1 id FROM Utenti")
                row = cursor.fetchone()
                while row:
                    register=True
                    row = cursor.fetchone() 
        return register  