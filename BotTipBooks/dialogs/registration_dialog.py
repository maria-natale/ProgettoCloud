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

server = 'servercc.database.windows.net'
database = 'BotTipBooksDatabase'
username = 'useradmin'
password = 'Progettocloud21'   
driver= '{ODBC Driver 17 for SQL Server}'
CARD_PROMPT = "cardPrompt"

class RegistrationDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(RegistrationDialog, self).__init__(dialog_id or RegistrationDialog.__name__)
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(CARD_PROMPT))
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.select_categories, self.validate]
            )
        )

        self.initial_dialog_id = "WFDialog"


    async def select_categories(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        #await step_context.context.send_activity("Scegli categorie")
        print("sono nella registrzione")
        relative_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(relative_path, "../cards/cardreg.json")
        with open(path) as in_file:
            card = json.load(in_file)

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt = MessageFactory.attachment(CardFactory.adaptive_card(card))
            )
        )        
        


    async def validate(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        message=step_context.result
        print(message)

        

       
