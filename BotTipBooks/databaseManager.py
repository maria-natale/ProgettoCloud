import pyodbc
from bean import User
from bean import BookInfo
from bean import Book, Category
from typing import List

server = 'servercc.database.windows.net'
database = 'BotTipBooksDatabase'
username = 'useradmin'
password = 'Progettocloud21'   
driver= '{ODBC Driver 17 for SQL Server}'


class DatabaseManager:
    @staticmethod
    def user_is_registered(iduser: str):
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
    def add_book_wishlist(iduser: str, book: BookInfo, genres: List):
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                book=DatabaseManager.add_book(book, genres)
                if book!=None and book.price!=None:
                    try:
                        cursor.execute("INSERT INTO wishlist (utente, titoloLibro, autoreLibro, prezzo, sito, disponibilita, link) values (?,?,?,?,?,?,?)", iduser, book.name, book.author, book.price, book.site, book.availability, book.link)
                    except pyodbc.IntegrityError:
                        return False
                elif book!=None:
                    try:
                        cursor.execute("INSERT INTO wishlist (utente, titoloLibro, autoreLibro, sito, disponibilita, link) values (?,?,?,?,?,?)", iduser, book.name, book.author, book.site, book.availability, book.link)
                    except pyodbc.IntegrityError:
                        return False
                conn.commit()
                return True
        return False


    @staticmethod
    def add_user(iduser:str, categories: List):
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO Utenti (id) values (?)", iduser)
                conn.commit()
                for c in categories:
                    cursor.execute("INSERT INTO UtentiCategorie (utente, categoria) values (?,?)", iduser, c.name)
                conn.commit()
                return True
        return False

    
    @staticmethod 
    def find_user_info(iduser: str):
        if DatabaseManager.user_is_registered(iduser):
            user=User(iduser)
            with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT ALL categoria FROM UtentiCategorie WHERE utente=?",iduser)
                    row = cursor.fetchone()
                    while row:
                        user.add_category(str(row[0]))
                        row = cursor.fetchone() 
            with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('''SELECT ALL titolo, autore, categoria, prezzo, sito, disponibilita, link 
                        FROM Libri, Wishlist WHERE utente=? and Libri.titolo=Wishlist.titoloLibro and Libri.autore=Wishlist.autoreLibro''',iduser)
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


    @staticmethod
    def find_categories():
        categories=[]
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT ALL nomeCategoria, sinonimi FROM Categorie")
                row = cursor.fetchone()
                while row:
                    synonyms=str(row[1]).split(";")
                    categories.append(Category(str(row[0]),synonyms))
                    row = cursor.fetchone() 
        return categories 

    
    @staticmethod
    def add_book(book:BookInfo, genres: List):
        categories=DatabaseManager.find_categories()
        book.genre=None
        for c in categories:
            for s in c.synonyms:
                for x in genres:
                    if c.name=="Storia":
                        if x.lower()==s.lower():
                            book.genre=c.name
                            break
                    if x.lower() in s.lower() or s.lower() in x.lower():
                        book.genre=c.name
                        break
        if book.genre==None:
            book.genre="Genere sconosciuto"
        print(book.genre)
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("INSERT INTO Libri (titolo, autore, categoria) values (?, ?, ?)", book.name, book.author, book.genre)
                    conn.commit()
                except pyodbc.IntegrityError:
                    return book
            return book
        return None
        
    
    @staticmethod
    def remove_wishlist(iduser, book: BookInfo):
        with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute('''Delete from Wishlist where utente=? and titoloLibro=? and autoreLibro=?
                    ''', iduser, book.name, book.author)
                    conn.commit()
                except pyodbc.IntegrityError:
                    return False
            return True
            

    
