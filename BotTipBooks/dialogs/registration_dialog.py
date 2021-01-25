from botbuilder.dialogs import ComponentDialog, DialogContext, DialogTurnResult, DialogTurnStatus, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
from botbuilder.schema import ActivityTypes, InputHints
from botbuilder.core import CardFactory, MessageFactory
from .cancel_and_help_dialog import CancelAndHelpDialog
from botbuilder.schema._models_py3 import CardAction, HeroCard
from botbuilder.schema._connector_client_enums import ActionTypes

import pyodbc
server = 'servercc.database.windows.net'
database = 'BotTipBooksDatabase'
username = 'useradmin'
password = 'Progettocloud21'   
driver= '{ODBC Driver 17 for SQL Server}'




CATEGORIES=[]

class RegistrationDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(RegistrationDialog, self).__init__(dialog_id or RegistrationDialog.__name__)

        #cercare le categorie dal database
        search_categories()

        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.add_categories]
            )
        )

        self.initial_dialog_id = "WFDialog"

    async def add_categories(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        #await step_context.context.send_activity("Scegli categorie")
        print("sono nella registrzione")
        return await step_context.end_dialog()



def search_categories():
    with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ALL nomeCategoria FROM Categorie")
            row = cursor.fetchone()
            while row:
                CATEGORIES.append(str(row[0]))
                row = cursor.fetchone()   