from botbuilder.dialogs import TextPrompt, WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.core import CardFactory, MessageFactory
from typing import List
from databaseManager import DatabaseManager
from dialogs import CancelAndHelpDialog
import requests
import json
from bean import BookInfo
from pyadaptivecards.container import ColumnSet
from pyadaptivecards.components import Column, Image, TextBlock
from pyadaptivecards.options import BlockElementHeight, Colors, FontWeight, HorizontalAlignment, Spacing
from pyadaptivecards.card import AdaptiveCard
from pyadaptivecards.actions import OpenUrl

cat_and_code = {"Adolescenti e ragazzi": "13077484031",
    "Arte cinema e fotografia": "13077485031",
    "Biografie": "13077512031",
    "Cucina": "508822031",
    "Fantascienza e fantasy": "508773031",
    "Fumetti e manga": "508784031",
    "Gialli e thriller": "508771031",
    "Letteratura": "508770031",
    "Romanzi rosa": "508775031",
    "Scienze e tecnologia": "508867031",
    "Storia": "508796031"
}

list_of_books=[]
books_images=dict()

class SuggestBooksDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(SuggestBooksDialog, self).__init__(dialog_id or SuggestBooksDialog.__name__)

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.showBooks_step]
            )
        )

        self.initial_dialog_id = "WFDialog"
    
    async def showBooks_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        iduser=step_context.context.activity.from_property.id
        SuggestBooksDialog.find_suggests(iduser)
        card=SuggestBooksDialog.create_card()
        await step_context.context.send_activity(MessageFactory.attachment(card))
        return await step_context.end_dialog()
    

    @staticmethod
    def find_suggests(iduser: str):
        wishlist_of_user = []
        genres_user = []

        user_with_info = DatabaseManager.find_user_info(iduser)
        genres_user = user_with_info.categories
        for cat in genres_user:
            category = cat.name
            code = cat_and_code[category]
            SuggestBooksDialog.call_amazon(code)
    

    @staticmethod
    def call_amazon(code: str):
        params = {
            'api_key': 'A2E5C7D9C233454FAE27F2A0911C42A8',
            'type': 'bestsellers',
            'url': 'https://www.amazon.it/gp/bestsellers/books/'+ code,
            'page': '1'
        }

        api_result = requests.get('https://api.rainforestapi.com/request', params)# print the JSON response from Rainforest APIprint(json.dumps(api_result.json()))
        jsonStringResult = json.dumps(api_result.json())
        jsonResult = json.loads(jsonStringResult)
        lista_bestseller = jsonResult['bestsellers']
        book = BookInfo()
        for i, libro in enumerate(lista_bestseller):
            if i < 3:
                title = libro['title']
                price = libro['price']['value']
                category = libro['current_category']['name']
                image_link = libro['image']
                link = libro['link']
                book.name = title
                book.price = price
                book.genre = category
                book.link = link
                list_of_books.append(book)
                books_images[title] = image_link
                book=BookInfo()
            else:
                break
        


    @staticmethod
    def create_card():
        firstcolumnSet = ColumnSet([Column([TextBlock("Ecco i miei suggerimenti per te", color=Colors(4),
        weight=FontWeight(3), horizontalAlignment=HorizontalAlignment(2), wrap=True)])])
        items=[]
        columnsSet=[]
     
        for book in list_of_books:
            title=book.name
            image_link = books_images[title]
            open_url=OpenUrl(url=book.link)
            itemImage=Image(url=image_link, spacing=Spacing(3), horizontalAlignment=HorizontalAlignment(2),
                width="170px", height="180px", selectAction=open_url)
            items.append(TextBlock("Titolo: {}".format(title), spacing=Spacing(3), wrap=True))
            items.append(TextBlock("Prezzo: {} € ".format(book.price), spacing=Spacing(3), wrap=True))
            items.append(TextBlock("Genere: {} ".format(book.genre), spacing=Spacing(3), wrap=True))
            columnsSet.append(ColumnSet([Column([itemImage]),Column(items)], separator=True, spacing=Spacing(5)))
            items=[]

        card = AdaptiveCard(body=[firstcolumnSet]+columnsSet)

        return CardFactory.adaptive_card(card.to_dict())