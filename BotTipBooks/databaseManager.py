import pyodbc
from bean import User
from bean import BookInfo

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
    

    @staticmethod
    def add_book_wishlist(id: str, book: BookInfo):
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO wishlist (utente, titoloLibro, autoreLibro, prezzo, sito, diponibilita, link) values (?,?,?,?,?,?,?)", id, book.name, book.author, book.price, book.site, book.availability, book.link)
                conn.commit()
                return True
        return False

    
    @staticmethod 
    def find_user_info(id: str):
        if DatabaseManager.user_is_registered(id):
            user=User(id)
            with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT ALL categoria FROM UtentiCategorie WHERE utente=?",id)
                    row = cursor.fetchone()
                    while row:
                        user.add_category(str(row[0]))
                        row = cursor.fetchone() 
            with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT ALL titolo, autore, categoria, prezzo, sito, disponibilita, link FROM Libri, Wishlist WHERE utente=?",id)
                    row = cursor.fetchone()
                    while row:
                        bookinfo=BookInfo()
                        bookinfo.name=str(row[0])
                        bookinfo.author=str(row[1])
                        bookinfo.genre=str(row[2]) if row[2] is not None else None
                        bookinfo.price=float(str(row[3])) if row[3] is not None else None
                        bookinfo.site=str(row[4])
                        bookinfo.availability=str(row[5]) if row[5] is not None else None
                        bookinfo.link=str(row[6]) if row[6] is not None else None
                        user.add_book(bookinfo)
                        row = cursor.fetchone()
            return user
        return None
            

    
