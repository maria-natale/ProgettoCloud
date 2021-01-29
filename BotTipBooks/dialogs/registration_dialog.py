from botbuilder.dialogs import ComponentDialog, DialogContext, DialogTurnResult, DialogTurnStatus, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
from botbuilder.schema import ActivityTypes, InputHints
from botbuilder.core import CardFactory, MessageFactory
from .cancel_and_help_dialog import CancelAndHelpDialog
from botbuilder.schema._models_py3 import Attachment, CardAction, HeroCard
from botbuilder.schema._connector_client_enums import ActionTypes
import pyodbc
import os
import json
from botbuilder.dialogs.prompts.choice_prompt import ChoicePrompt
from botbuilder.dialogs.choices import Choice
from botbuilder.dialogs.choices.list_style import ListStyle
from databaseManager import DatabaseManager
from pyadaptivecards.container import ColumnSet
from pyadaptivecards.components import Column, TextBlock
from pyadaptivecards.options import Colors, FontWeight, HorizontalAlignment, Spacing
from pyadaptivecards.card import AdaptiveCard

server = 'servercc.database.windows.net'
database = 'BotTipBooksDatabase'
username = 'useradmin'
password = 'Progettocloud21'   
driver= '{ODBC Driver 17 for SQL Server}'


class RegistrationDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(RegistrationDialog, self).__init__(dialog_id or RegistrationDialog.__name__)

        self.CATEGORIES=DatabaseManager.find_categories()
        self.selected=[]
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.select_categories, self.validate, self.loop_step]
            )
        )

        self.initial_dialog_id = "WFDialog"


    async def select_categories(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        card=self.create_card()

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                prompt = MessageFactory.attachment(card)
            )
        )        
        


    async def validate(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        message=step_context.result
        valid=False
        for c in self.CATEGORIES:
            if message.lower().replace(",", "").replace(" ", "")==c.name.lower().replace(",", "").replace(" ", ""):
                self.selected.append(c)
                self.CATEGORIES.remove(c)
                valid=True
                break
        if not valid:
            message_text = ("La categoria inserita non è valida")
            message = MessageFactory.text(message_text, message_text, InputHints.ignoring_input)
            await step_context.context.send_activity(message)
        else:
            n=3-len(self.selected)
            if n>0:
                message_text = ("La categoria {} è stata selezionata correttamente. Ti restano ancora {} categorie da selezionare".format(c.name, n))
                message = MessageFactory.text(message_text, message_text, InputHints.ignoring_input)
                await step_context.context.send_activity(message)
            else:
                message_text = ("La categoria {} è stata selezionata correttamente. ".format(c.name))
                message = MessageFactory.text(message_text, message_text, InputHints.ignoring_input)
                await step_context.context.send_activity(message)
        return await step_context.next([])


    
    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if len(self.selected)<3:
            return await step_context.replace_dialog("WFDialog")
        else:
            iduser=step_context.context.activity.from_property.id
            DatabaseManager.add_user(iduser, self.selected)
            return await step_context.end_dialog()
    

    def create_card(self):
        firstcolumnSet = ColumnSet([Column([TextBlock("Scegli una categoria", weight=FontWeight(3), horizontalAlignment=HorizontalAlignment(2), wrap=True)])])
        items=[]
        columnsSet=[]
     
        for c in self.CATEGORIES:
            items.append(TextBlock("{} ".format(c.name), spacing=Spacing(3), wrap=True)) 
            columnsSet.append(ColumnSet([Column(items)]))
            items=[]
        card = AdaptiveCard(body=[firstcolumnSet]+columnsSet)

        return CardFactory.adaptive_card(card.to_dict())

        

       
