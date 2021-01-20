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
from botbuilder.core import MessageFactory, TurnContext, CardFactory
from botbuilder.schema import InputHints, SuggestedActions
from botbuilder.dialogs.choices import Choice
from flight_booking_recognizer import FlightBookingRecognizer
from .findbook_dialog import FindBookDialog
from book import Book


class MainDialog(ComponentDialog):

    def __init__(self, luis_recognizer: FlightBookingRecognizer, findbook: FindBookDialog):
        super(MainDialog, self).__init__(MainDialog.__name__)

        self._luis_recognizer = luis_recognizer
        self.findbook_dialog_id=findbook.id

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.intro_step, self.menu_step, self.options_step, self.loop_step]
            )
        )
        self.add_dialog(findbook)
        self.initial_dialog_id = "WFDialog"

    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """if not self._luis_recognizer.is_configured:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "NOTE: LUIS is not configured. To enable all capabilities, add 'LuisAppId', 'LuisAPIKey' and "
                    "'LuisAPIHostName' to the appsettings.json file.",
                    input_hint=InputHints.ignoring_input,
                )
            )

            return await step_context.next(None)"""

        WELCOME_MESSAGE = "Come posso aiutarti?\n\nSe vuoi sapere cosa posso fare per te scrivi \"menu\""
        message_text = (
            str(step_context.options)
            if step_context.options
            else WELCOME_MESSAGE
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )
        return await step_context.prompt(
            TextPrompt.__name__, PromptOptions(prompt=prompt_message)
        )
        

    async def menu_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        message=step_context.result
        if message=='menu':
            card = HeroCard(
            text ="Seleziona un'opzione: ",
            buttons = [
                CardAction(
                    type=ActionTypes.im_back,
                    title ="Info",
                    value="info"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title ="Registrazione",
                    value="registrazione"
                ),
                CardAction(
                    type=ActionTypes.im_back,
                    title ="Cerca libro",
                    value="cerca"
                ),
            ],   
        )
            return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                MessageFactory.attachment(CardFactory.hero_card(card))
            ),
        )
        else:
            message_text= (
            str(step_context.options)
            if step_context.options
            else "Input non valido")
            prompt_message = MessageFactory.text(
                message_text)
            await step_context.context.send_activity(prompt_message)
            return await step_context.replace_dialog(self.id)


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
        #if (option=="registrazione"):
         #   return await step_context.begin_dialog()


    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.replace_dialog(self.id)
        