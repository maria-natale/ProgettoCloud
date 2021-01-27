# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.schema import (
    ChannelAccount,
    HeroCard,
    CardImage,
    CardAction,
    ActionTypes,
)
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions, ChoicePrompt
from botbuilder.core import MessageFactory, TurnContext, CardFactory, UserState
from botbuilder.schema import InputHints, SuggestedActions
from botbuilder.dialogs.choices import Choice
from flight_booking_recognizer import FlightBookingRecognizer
from .findbook_dialog import FindBookDialog
from bean import Book, User
from botbuilder.dialogs.prompts.oauth_prompt_settings import OAuthPromptSettings
from botbuilder.dialogs.prompts.oauth_prompt import OAuthPrompt
from .logout_dialog import LogoutDialog
from botbuilder.dialogs.prompts.confirm_prompt import ConfirmPrompt
from botbuilder.dialogs.choices.channel import Channel
from .registration_dialog import RegistrationDialog
from databaseManager import DatabaseManager
from botbuilder.schema._connector_client_enums import ActivityTypes
from botbuilder.dialogs.dialog import Dialog

registration_dialog=RegistrationDialog()
findbook=FindBookDialog()

class MainDialog(ComponentDialog):
    
    def __init__(self, connection_name: str,  luis_recognizer: FlightBookingRecognizer):
        super(MainDialog, self).__init__(MainDialog.__name__)
        self.connection_name=connection_name
        
        self._luis_recognizer = luis_recognizer
        self.findbook_dialog_id=findbook.id

        self.add_dialog(
            OAuthPrompt(
                OAuthPrompt.__name__,
                OAuthPromptSettings(
                    connection_name=connection_name,
                    text="Accedi",
                    title="Sign In",
                    timeout=300000,
                ),
            )
        )

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", 
                [
                 self.menu_step, 
                 self.options_step,
                 self.final_step, 
                 self.loop_step]
            )
        )
        self.add_dialog(findbook)
        self.add_dialog(registration_dialog)

        self.add_dialog(
            WaterfallDialog(
                "WFDialogLogin",
                [
                    self.prompt_step,
                    self.login_step
                ]
            )
        )

        self.initial_dialog_id = "WFDialogLogin"
        
        

    async def prompt_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.begin_dialog(OAuthPrompt.__name__)

    async def login_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result:
            iduser=step_context.context.activity.from_property.id
            print("sono nel login")
            #controlla se è registrato nel database
            if DatabaseManager.user_is_registered(iduser):
                return await step_context.begin_dialog(registration_dialog.id) #se non è registrato
            await step_context.context.send_activity("Sei loggato")
            return await step_context.begin_dialog("WFDialog")
        await step_context.context.send_activity("Login was not successful please try again.")
        return await step_context.end_dialog()
  
        

    async def menu_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """if not self._luis_recognizer.is_configured:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "NOTE: LUIS is not configured. To enable all capabilities, add 'LuisAppId', 'LuisAPIKey' and "
                    "'LuisAPIHostName' to the appsettings.json file.",
                    input_hint=InputHints.ignoring_input,
                )
            )

            return await step_context.next(None)"""

        card = HeroCard(
        text ="Ciao, come posso aiutarti? ",
        buttons = [
            CardAction(
                type=ActionTypes.im_back,
                title ="Info",
                value="info"
            ),
            CardAction(
                type=ActionTypes.im_back,
                title ="Visualizza wishlist",
                value="wishlist"
            ),
            CardAction(
                type=ActionTypes.im_back,
                title ="Cerca libro",
                value="cerca"
            ),
            CardAction(
                type=ActionTypes.im_back,
                title ="Logout",
                value="logout"
            )
        ],   
        )
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                MessageFactory.attachment(CardFactory.hero_card(card))
            ),
        )
        


    async def options_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        option=step_context.result
        MESSAGE_INFO= "INFO "

        if (option=="info"):
            message_text = (
            str(step_context.options)
            if step_context.options
            else MESSAGE_INFO
            )
            prompt_message = MessageFactory.text(
                message_text)
            await step_context.context.send_activity(prompt_message)
            return await step_context.next([])
        if (option=="cerca"):
            return await step_context.begin_dialog(self.findbook_dialog_id, Book())
        if (option=="logout"): #vedi logoutdialog
            return await step_context.cancel_all_dialogs()

    
    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        message_text = "Posso fare qualcos'altro per te?"
        prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
        return await step_context.prompt(
                ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message)
                )


    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        result=step_context.result
        if result:
            return await step_context.replace_dialog("WFDialog")
        return await step_context.cancel_all_dialogs()




        
