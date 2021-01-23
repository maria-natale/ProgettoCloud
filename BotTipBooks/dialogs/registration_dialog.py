from botbuilder.dialogs import ComponentDialog, DialogContext, DialogTurnResult, DialogTurnStatus, PromptOptions, TextPrompt, WaterfallDialog, WaterfallStepContext
from botbuilder.schema import ActivityTypes, InputHints
from botbuilder.core import CardFactory, MessageFactory
from .cancel_and_help_dialog import CancelAndHelpDialog
from botbuilder.schema._models_py3 import CardAction, HeroCard
from botbuilder.schema._connector_client_enums import ActionTypes

CATEGORIES=[]

class RegistrationDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(RegistrationDialog, self).__init__(dialog_id or RegistrationDialog.__name__)

        #cercare le categorie dal database
        CATEGORIES=["Cucina", "Arte", "Tempo libero", "Storia", "Gialli", "Biografie", "Libri per bambini"]

        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.add_categories]
            )
        )

        self.initial_dialog_id = "WFDialog"

    async def add_categories(self, step_context: WaterfallStepContext) -> DialogTurnResult:
       
        #await step_context.context.send_activity("Scegli categorie")
        return await step_context.end_dialog()