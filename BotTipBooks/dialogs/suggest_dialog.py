from botbuilder.dialogs import ConfirmPrompt, DialogTurnResult, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
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
from botbuilder.dialogs.prompts import PromptValidatorContext
from botbuilder.schema import InputHints

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
        self.add_dialog(TextPrompt("TextPromptTitle", SuggestBooksDialog.titleValidator))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__, SuggestBooksDialog.yes_noValidator))
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.showBooks_step, self.confirm_step, self.add_step]
            )
        )

        self.initial_dialog_id = "WFDialog"
        
    
    async def showBooks_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        iduser=step_context.context.activity.from_property.id
        SuggestBooksDialog.find_suggests(iduser)
        card=SuggestBooksDialog.create_card()
        await step_context.context.send_activity(MessageFactory.attachment(card))
        message_text="Vuoi aggiungere un libro alla tua wishlist?"
        prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
        return await step_context.prompt(
                ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message,
                retry_prompt=MessageFactory.text('''Vuoi aggiungere un libro alla tua wishlist? 
                Scrivi yes o no'''))
        )
    

    async def confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        result=step_context.result
        message_text="Inserisci il titolo del libro che vuoi aggiungere alla wishlist"
        prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
        if result:
            return await step_context.prompt(
                "TextPromptTitle", PromptOptions(prompt=prompt_message,
                retry_prompt=MessageFactory.text('''Inserisci un titolo valido'''))
            )
        else:
            return await step_context.end_dialog()
        

    async def add_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        title=step_context.result
        book_to_add=self.find_book(title)
        iduser=step_context.context.activity.from_property.id
        print(book_to_add.name)
        print(book_to_add.genre)
        if book_to_add is not None:
            if DatabaseManager.add_book_wishlist(iduser, book_to_add, [book_to_add.genre]):
                message_text="Il libro {} è stato aggiunto alla tua wishlist.".format(book_to_add.name)
                await step_context.context.send_activity(MessageFactory.text(message_text))
            else:
                message_text="Il libro {} non è stato aggiunto alla tua wishlist.".format(book_to_add.name)
                await step_context.context.send_activity(MessageFactory.text(message_text))
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
            'api_key': '78ECAD39F78C435C8D50238C0406637B',
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
    

    @staticmethod
    async def yes_noValidator(prompt_context: PromptValidatorContext) -> bool:
        return (
            prompt_context.recognized.succeeded
            and isinstance(prompt_context.recognized.value, bool)
        )


    @staticmethod
    async def titleValidator(prompt_context: PromptValidatorContext) -> bool:
        title=prompt_context.recognized.value
        book_to_add=None
        for book in list_of_books:
            if book.name.replace(",","").lower()==title.replace(",","").lower():
                book_to_add=book
                break
        return (
            prompt_context.recognized.succeeded
            and book_to_add is not None
        )



    def find_book(self, title: str):
        r= requests.get("https://find-book-function.azurewebsites.net/api/FindBooksScraper?name={}&who=amazon".format(title))      
        string_result=r.text.split("\n")
        book=BookInfo()
        print(string_result)
        for i, s in enumerate(string_result):
            if i==0:
                book.site=s 
            elif i==1:
                book.name=s if s!="None" or s!='' else None
            elif i==2:
                book.author=s if s!="None" or s!='' else None
            elif i==3:
                book.availability=s if s!="None" else "Non disponibile"
            elif i==4:
                if s!="None":
                    s=s.replace(",", ".")
                    try:
                        book.price=float(s)
                    except ValueError:
                        book.price=None
                else:
                    book.price=None
            elif i==5:
                book.genre=s  if s!="None" or s!='' else None
            elif i==6:
                book.link=s
            elif i==7:
                break
        return book
