from botbuilder.dialogs import (ComponentDialog, DialogContext, DialogTurnResult, DialogTurnStatus, TextPrompt, 
    WaterfallDialog, WaterfallStepContext)
from botbuilder.schema import ActivityTypes, InputHints
from botbuilder.core import MessageFactory
from .cancel_and_help_dialog import CancelAndHelpDialog


class FindBookDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(FindBookDialog, self).__init__(dialog_id or FindBookDialog.__name__)

        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.destination_step]
            )
        )

        self.initial_dialog_id = "WFDialog"

    async def destination_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.end_dialog()