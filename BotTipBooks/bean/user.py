from typing import List


class User:
    def __init__(self, id:str =None, categories: List = None, wishlist: List =None):
        self.idUser=id
        self.categories=[] if categories is None else categories
        self.wishlist=[] if wishlist is None else wishlist
    
    def add_category(self, category: str):
        self.categories.append(category)
    


        