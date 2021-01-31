from botbuilder.dialogs import ComponentDialog, ConfirmPrompt, DialogContext, DialogTurnResult, DialogTurnStatus, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
from .cancel_and_help_dialog import CancelAndHelpDialog
from botbuilder.core import CardFactory, MessageFactory
from databaseManager import DatabaseManager
from typing import List
from pyadaptivecards.card import AdaptiveCard
from pyadaptivecards.container import ColumnSet
from pyadaptivecards.components import Column, TextBlock
from bean import BookInfo
from pyadaptivecards.options import Colors, FontWeight, HorizontalAlignment, Spacing
from botbuilder.schema import InputHints
from bot_recognizer import BotRecognizer
from helpers.luis_helper import Intent, LuisHelper
from botbuilder.dialogs.prompts import PromptValidatorContext
import time

class WishlistDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(WishlistDialog, self).__init__(dialog_id or WishlistDialog.__name__)
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__, WishlistDialog.yes_noValidator))
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.first_step, self.input_step, self.begin_next]
            )
        )

        self.add_dialog(
            WaterfallDialog(
                "WFDialogCancella", [
                    self.confirm_step,
                    self.cancel_step,
                    self.final_step
                ]
            )
        )

        self.initial_dialog_id = "WFDialog"
        self._luis_recognizer=None
        self.user=None
        self.book_to_remove=None
        self.title=None
    
    async def first_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        user=DatabaseManager.find_user_info(step_context.context.activity.from_property.id)
        self.user=user
        card, flag=self.create_wishlist_card(user.wishlist)
        await step_context.context.send_activity(MessageFactory.attachment(card))
        if flag:
            message_text="Puoi cancellare un libro dalla tua wishlist oppure tornare al menu principale. Cosa desideri fare?"
            prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.end_dialog()
    

    async def input_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        intent = await LuisHelper.execute_luis_query(self._luis_recognizer,step_context.context)
        print(str(intent))
        if intent == Intent.MENU_INTENT.value:
            return await step_context.end_dialog()
        if intent == Intent.CANCELLA_WISHLIST.value:
            message_text="Inserisci il titolo del libro che vuoi cancellare"
            prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        
        await step_context.context.send_activity(
            MessageFactory.text(
                "Input non valido"
            )
        )
        return await step_context.end_dialog()


    async def begin_next(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        result=step_context.result
        self.title=result
        print(result)
        return await step_context.replace_dialog("WFDialogCancella")


    async def confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        result=self.title
        for book in self.user.wishlist:
            if book.name.replace(",","").lower()==result.replace(",","").lower():
                self.book_to_remove=book
                break
        
        if self.book_to_remove is not None:
            message_text = "Sei sicuro di voler cancellare {}?".format(self.book_to_remove.name)
            prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
            return await step_context.prompt(
                ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message,
                retry_prompt='''Sei sicuro di voler cancellare? Scrivi yes o no''')
            )
        else:
            message_text="Il libro {} non è stato trovato nella tua wishlist. Per favore, inserisci nuovamente il titolo".format(result)
            prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
            self.book_to_remove=None
            self.title=None
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
            

    
    async def cancel_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if self.title is None:
            self.title=step_context.result
            return await step_context.replace_dialog("WFDialogCancella")
        result=step_context.result
        if result:
            self.user.wishlist.remove(self.book_to_remove)
            DatabaseManager.remove_wishlist(self.user.idUser, self.book_to_remove)
            message_text="Il libro {} è stato rimosso correttamente.".format(self.book_to_remove.name)
            await step_context.context.send_activity(MessageFactory.text(message_text))
            return await step_context.next([])
        else:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "Operazione annullata"
                )
            )
            return await step_context.end_dialog()

            

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        card=self.create_wishlist_card(self.user.wishlist)
        await step_context.context.send_activity(MessageFactory.attachment(card))
        return await step_context.end_dialog()

                

    def create_wishlist_card(self, books: List):
        firstcolumnSet = ColumnSet([Column([TextBlock("La tua wishlist", color=Colors(7), weight=FontWeight(3),
            horizontalAlignment=HorizontalAlignment(2), wrap=True)])])
        items=[]
        columnsSet=[]
        flag=False
        for book in books:
            flag=True
            if book.author is not None:
                items.append(TextBlock("{} di {} ".format(book.name, book.author), weight=FontWeight(3), color=Colors(2), wrap=True, isSubtle=True))
            else:
                items.append(TextBlock("{}".format(book.name, book.author), weight=FontWeight(3), color=Colors(2), wrap=True, isSubtle=True))
            items.append(TextBlock("Genere: {}".format(book.genre), weight=FontWeight(3), color=Colors(2), wrap=True, isSubtle=True))
            items.append(TextBlock("Nome del sito: {} ".format(book.site), spacing=Spacing(3), wrap=True)) 
            if book.price is not None:
                items.append(TextBlock("Prezzo: {} € ".format(book.price), spacing=Spacing(3), wrap=True))
            else: 
                items.append(TextBlock("Prezzo non disponibile", spacing=Spacing(3), wrap=True))
            items.append(TextBlock("Disponibilità: {} ".format(book.availability), spacing=Spacing(3), wrap=True))
            items.append(TextBlock("Link per l'acquisto: {} ".format(book.link), spacing=Spacing(3), wrap=True, color=Colors(5)))
            columnsSet.append(ColumnSet([Column(items)], separator=True, spacing=Spacing(4)))
            items=[]
        if flag:
            card = AdaptiveCard(body=[firstcolumnSet]+columnsSet)
            return (CardFactory.adaptive_card(card.to_dict()), True)
        else:
            firstcolumnSet = ColumnSet([Column([TextBlock("La tua wishlist è vuota", color=Colors(7), weight=FontWeight(3),
            horizontalAlignment=HorizontalAlignment(2), wrap=True)])])
            columnSet = ColumnSet([Column([TextBlock('''Non puoi eseguire nessuna operazione.
                Puoi cercare un libro ed aggiungerlo. Ti riporto al menù principale.''',wrap=True)])])
            card = AdaptiveCard(body=[firstcolumnSet, columnSet])
            return (CardFactory.adaptive_card(card.to_dict()), False)

    
    def set_recognizer(self, luis_recognizer: BotRecognizer):
        self._luis_recognizer=luis_recognizer


    @staticmethod
    async def yes_noValidator(prompt_context: PromptValidatorContext) -> bool:
        return (
            prompt_context.recognized.succeeded
            and isinstance(prompt_context.recognized.value, bool)
        )
