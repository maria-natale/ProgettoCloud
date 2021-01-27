from botbuilder.dialogs import (ComponentDialog, DialogContext, DialogTurnResult, DialogTurnStatus, TextPrompt, 
    WaterfallDialog, WaterfallStepContext)
from botbuilder.schema import ActivityTypes, InputHints
from botbuilder.core import MessageFactory
from .cancel_and_help_dialog import CancelAndHelpDialog
from botbuilder.dialogs.prompts.prompt_options import PromptOptions
from botbuilder.dialogs.prompts import ConfirmPrompt
import requests
from bean import BookInfo


class FindBookDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(FindBookDialog, self).__init__(dialog_id or FindBookDialog.__name__)

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.prompt_step, self.search_step, self.confirm_step, self.add_to_wishlist]
            )
        )

        self.initial_dialog_id = "WFDialog"
        self.books=[]

    async def prompt_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        message_text = "Quale libro vuoi cercare?"
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )
        return await step_context.prompt(
            TextPrompt.__name__, PromptOptions(prompt=prompt_message)
        )
    
    async def search_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result is not None:
            book_name=step_context.result
            validate_result = self._validate_title(book_name)
            if validate_result:
                card=self.find_book(book_name)
                #visualizza risultati
                message_text = ("trovati")
                message = MessageFactory.text(message_text, message_text, InputHints.ignoring_input)
                await step_context.context.send_activity(message)

                message_text = "Desideri aggiungere un libro alla tua wishlist?"
                prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
                return await step_context.prompt(
                    ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message)
                    )
        await step_context.context.send_activity(
                MessageFactory.text(
                    "Input non valido"
                )
            )
        return await step_context.end_dialog()


    async def confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        result=step_context.result
        if result:
            message_text="Su quale sito desideri acquistare il libro?"
            prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.end_dialog()

    
    async def add_to_wishlist(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        result=step_context.result
        
        return await step_context.end_dialog()
    

    def find_book(self, title: str):
        r=requests.get("https://find-book-function.azurewebsites.net/api/FindBooksScraper?name={}&who=all".format(title))
        string_result=r.text.split("\n")
        book=BookInfo()
        for i, s in enumerate(string_result):
            if i%6==0:
                book=BookInfo()
                book.site=s
            elif i%6==1:
                book.name=s
            elif i%6==2:
                book.author=s
            elif i%6==3:
                book.availability=s
            elif i%6==4:
                if s!=None:
                    s=s.replace(",", ".")
                try:
                    book.price=float(s)
                except ValueError:
                    book.price=None
                book.price=None
            elif i%6==5:
                book.genre=s
                self.books.append(book)
        for book in self.books:
            print(book.name)
        return create_result_card()
        

    def _validate_title(self, user_input: str) -> bool:
        if not len(user_input)>=5:
            return False
        return True
    

    def create_result_card(self):
        pass
