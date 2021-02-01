from botbuilder.dialogs import (ComponentDialog, DialogContext, DialogTurnResult, DialogTurnStatus, TextPrompt, 
    WaterfallDialog, WaterfallStepContext)
from botbuilder.schema import ActivityTypes, InputHints
from botbuilder.core import MessageFactory
from .cancel_and_help_dialog import CancelAndHelpDialog
from botbuilder.dialogs.prompts.prompt_options import PromptOptions
from botbuilder.dialogs.prompts import PromptValidatorContext
from botbuilder.dialogs.prompts import ConfirmPrompt
import requests
from bean import BookInfo
from databaseManager import DatabaseManager
from botbuilder.core.card_factory import CardFactory
from pyadaptivecards.card import AdaptiveCard
from pyadaptivecards.components import TextBlock, Column
from pyadaptivecards.container import ColumnSet
from pyadaptivecards.options import Colors, HorizontalAlignment, Spacing, FontWeight
import os
from pyadaptivecards.options import FontSize
from typing import List
import time
import json
import re
from text_analyzer import TextAnalyzer


class FindBookDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(FindBookDialog, self).__init__(dialog_id or FindBookDialog.__name__)

        self.add_dialog(TextPrompt("TextPromptLibro", FindBookDialog.validateName))
        self.add_dialog(TextPrompt("TextPromptSito", FindBookDialog.validateSite))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__, FindBookDialog.yes_noValidator))
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.prompt_step, 
                self.search_step, 
                self.confirmRec_step,
                self.prompt_to_wish,
                self.confirm_step, 
                self.add_to_wishlist]
            )
        )

        self.initial_dialog_id = "WFDialog"
        self.books=[]

    async def prompt_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        message_text = "Quale libro vuoi cercare?"
        self.books=[]
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )
        return await step_context.prompt(
            "TextPromptLibro", PromptOptions(prompt=prompt_message,
            retry_prompt=MessageFactory.text('''Quale libro vuoi cercare? Il nome del libro deve avere lunghezza
            compresa tra 5 e 30'''))
        )
        
    
    async def search_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        book_name=step_context.result
        card= self.find_book(book_name)
        await step_context.context.send_activity(MessageFactory.attachment(card))

        message_text = "Vuoi conoscere le recensioni sul libro?"
        prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message,
                retry_prompt=MessageFactory.text('''Vuoi conoscere le recensioni sul libro? Scrivi yes o no'''))
            )


    async def confirmRec_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        result=step_context.result
        link=None
        if result:
            for book  in self.books:
                if book.site.lower()=="amazon":
                    link=book.link
                    break
            if link is not None:
                results, mean = FindBookDialog.get_reviews(link)
                max=results["positive"]
                strMax = "Ti consiglio fortemente l'acquisto."
                if results["negative"] > max:
                    max = results["negative"]
                    strMax = "Non te lo consiglio affatto."
                elif results["neutral"] > max:
                    max = results["neutral"]
                    strMax = "Ti consiglio di dargli un'occhiata."
                message_text = ('''Ho analizzato le recensioni.\nI lettori hanno espresso {} opinioni positive,
                {} opinioni neutrali e {} opinioni negative.\nLa media del valore delle recensioni è {} stelle.\n{}
                '''.format(results["positive"], results["neutral"], results["negative"], mean, strMax))
                message = MessageFactory.text(message_text, message_text, InputHints.ignoring_input)
                await step_context.context.send_activity(message)
            message_text = ('''Errore durante l'analisi delle recensioni''')
            message = MessageFactory.text(message_text, message_text, InputHints.ignoring_input)
            await step_context.context.send_activity(message)
        return await step_context.next([])


    async def prompt_to_wish(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        message_text = "Desideri aggiungere il libro alla tua wishlist?"
        prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message,
                retry_prompt=MessageFactory.text('''Desideri aggiungere il libro alla tua wishlist? 
                Scrivi yes o no'''))
            )


    async def confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        result=step_context.result
        if result:
            message_text="Su quale sito desideri acquistare il libro?"
            prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
            return await step_context.prompt(
                "TextPromptSito", PromptOptions(prompt=prompt_message,
                retry_prompt=MessageFactory.text('''Su quale sito desideri acquistare il libro? Inserisci
                un sito valido''')),
            )
        return await step_context.end_dialog()

    
    async def add_to_wishlist(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        result=step_context.result
        iduser=step_context.context.activity.from_property.id
        book_to_add=BookInfo()
        for book in self.books:
            if book.site.lower()==result.lower():
                book_to_add=book
                break
        for book in self.books:
            if book.name is not None:
                book_to_add.name=book.name
                break
        for book in self.books:
            if book.author is not None:
                book_to_add.author=book.author
                break
                    
        genres=[]
        for book in self.books:
            if book.genre is not None:
                genres.append(book.genre)
        if book_to_add.site is not None:
            if DatabaseManager.add_book_wishlist(iduser, book_to_add, genres):
                message_text = ("Il libro {} è stato aggiunto alla tua wishlist".format(book_to_add.name))
                message = MessageFactory.text(message_text, message_text, InputHints.ignoring_input)
                await step_context.context.send_activity(message)
                return await step_context.end_dialog()
        message_text = ("Si è verificato un errore durante l'aggiunta del libro {} alla tua wishlist".format(book_to_add.name))
        message = MessageFactory.text(message_text, message_text, InputHints.ignoring_input)
        await step_context.context.send_activity(message)
        return await step_context.end_dialog()
    

    def create_result_card(self):
        for book in self.books:
            if book.name is not None:
                title=book.name
                break
        for book in self.books:
            if book.author is not None:
                author=book.author
                break
        for book in self.books:
            if book.genre is not None:
                genre=book.genre
                break
        
        try:
            firstcolumnSet = ColumnSet([Column([TextBlock("RISULTATI", color=Colors(7), weight=FontWeight(3), horizontalAlignment=HorizontalAlignment(2), wrap=True)])])
            items=[]
            items.append(TextBlock("{} di {} ".format(title, author), weight=FontWeight(3), color=Colors(2), wrap=True, isSubtle=True))
            items.append(TextBlock("Genere: {}".format(genre), weight=FontWeight(3), color=Colors(2), wrap=True, isSubtle=True))
            columnsSet=[]
     
            for book in self.books:
                items.append(TextBlock("Nome del sito: {} ".format(book.site), spacing=Spacing(3), wrap=True)) 
                if book.price is not None:
                    items.append(TextBlock("Prezzo: {}€ ".format(book.price), spacing=Spacing(3), wrap=True))
                else: 
                    items.append(TextBlock("Prezzo non disponibile", spacing=Spacing(3), wrap=True))
                items.append(TextBlock("Disponibilità: {} ".format(book.availability), spacing=Spacing(3), wrap=True))
                items.append(TextBlock("Link per l'acquisto: {} ".format(book.link), spacing=Spacing(3), wrap=True, color=Colors(5)))
                columnsSet.append(ColumnSet([Column(items)], separator=True, spacing=Spacing(4)))
                items=[]
            card = AdaptiveCard(body=[firstcolumnSet]+columnsSet)

            return CardFactory.adaptive_card(card.to_dict())
        except UnboundLocalError:
            message="Si è vericato un errore durante la ricerca del libro."
            firstcolumnSet = ColumnSet([Column([TextBlock(message, weight=FontWeight(3), wrap=True)])])
            card = AdaptiveCard(body=[firstcolumnSet])
            


    def find_book(self, title: str):
        r= requests.get("https://find-book-function.azurewebsites.net/api/FindBooksScraper?name={}&who=all".format(title))      
        string_result=r.text.split("\n")
        book=BookInfo()
        print(string_result)
        for i, s in enumerate(string_result):
            if i%7==0:
                book=BookInfo()
                book.site=s 
            elif i%7==1:
                book.name=s if s!="None" or s!='' else None
            elif i%7==2:
                book.author=s if s!="None" or s!='' else None
            elif i%7==3:
                book.availability=s if s!="None" else "Non disponibile"
            elif i%7==4:
                if s!="None":
                    s=s.replace(",", ".")
                    try:
                        book.price=float(s)
                    except ValueError:
                        book.price=None
                else:
                    book.price=None
            elif i%7==5:
                book.genre=s  if s!="None" or s!='' else None
            elif i%7==6:
                book.link=s
                self.books.append(book)
        for book in self.books:
            print(book.name)
        return self.create_result_card()
        

    @staticmethod
    async def validateName(prompt_context: PromptValidatorContext) -> bool:
        return (
            prompt_context.recognized.succeeded
            and 5 <= len(prompt_context.recognized.value) <= 30
        )
    
    @staticmethod
    async def yes_noValidator(prompt_context: PromptValidatorContext) -> bool:
        return (
            prompt_context.recognized.succeeded
            and isinstance(prompt_context.recognized.value, bool)
        )
    
    @staticmethod
    async def validateSite(prompt_context: PromptValidatorContext) -> bool:
        return (
            prompt_context.recognized.succeeded
            and str(prompt_context.recognized.value).lower() in ["mondadori", "feltrinelli", "ibs", "amazon", "hoepli"]
        )
    

    @staticmethod
    def get_reviews(link: str):
        asin = link[link.rindex('/') + 1:]
        params = {
            'api_key': '78ECAD39F78C435C8D50238C0406637B',
            'type': 'reviews',
            'amazon_domain': 'amazon.it',
            'asin': asin
        }

        # make the http GET request to Rainforest API
        api_result = requests.get('https://api.rainforestapi.com/request', params)

        jsonStringResult = json.dumps(api_result.json())
        jsonResult = json.loads(jsonStringResult)
        print(jsonResult)
        reviews = jsonResult["reviews"]
        list_of_body=[]
        for review in reviews:
            list_of_body.append(review["body"])
        
        sum=0
        for review in reviews:
            sum+=float(review["rating"])
        
        if len(reviews)>0:
            mean=sum/len(reviews)
        else:
            mean=0
        
        text_analyzer=TextAnalyzer()
        results = text_analyzer.sentiment_analysis(list_of_body)
        
        return (results, mean)

    

    
