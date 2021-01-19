# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount
from welcome_user_state import WelcomeUserState
from botbuilder.core import (
    ActivityHandler,
    TurnContext,
    UserState,
    CardFactory,
    MessageFactory,
)
from botbuilder.schema import (
    ChannelAccount,
    HeroCard,
    CardImage,
    CardAction,
    ActionTypes,
)

class MyBot(ActivityHandler):
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.

    def __init__(self,user_state:UserState):
        if user_state is None:
            raise TypeError("Parametri mancanti user_state è richiesto, ma non è stato fornito")
        self._user_state = user_state
        self._user_state_accessor = self._user_state.create_property("WelcomeUserState")
        self.WELCOME_MESSAGE = "Ciao sono BookTipsBot, sono un bot che ti offre supporto all'acquisto dei libri di cui sei interessato,ecc..."
        self.PATTERN_MESSAGE ="""Ecco cosa posso fare per te: \n - Posso cercare un libro, prova a chiedermi trova guida galattica per gli autostoppisti \n - Posso confrontare i prezzi, prova a chiedermi confronta prezzi guida galattica per gli autostoppisti \n- Posso autenticarti e farti accedere alla tua wishlist \n- Puoi chiedermi informazioni aggiuntive scrivendo info
        """
        

    async def on_message_activity(self, turn_context: TurnContext):
        welcome_user_state = await self._user_state_accessor.get(turn_context, WelcomeUserState)
        if not welcome_user_state.did_welcome_user:
            welcome_user_state.did_welcome_user = True

            await turn_context.send_activity("Se vedi questo messaggio è la prima volta che accedi al bot")
            name = turn_context.activity.from_property.name
            #Qua va usato luis per capire gli intent
            text = turn_context.activity.text.lower()
            if text in ("info"):
                await self.send_intro_card(turn_context)
            else:
                turn_context.send_activity("Non ho capito cosa mi stai chiedendo")
    
    async def send_intro_card(self, turn_context:TurnContext):
        card = HeroCard(
            title="Benvenuto in BotTipsBook",
            text ="Sono un bot che riesce a: fornirti informazioni sui libri, ti guido verso nuovi acquisto, ti consento di creare una wishlist e di monitorare i libri all'interno",
            buttons = [
                CardAction(
                    type=ActionTypes.im_back,
                    title ="Provami",
                    value="cliccato"
                )
            ],
            
        )
        return await turn_context.send_activity(MessageFactory.attachment(CardFactory.hero_card(card)))
    

    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(self.WELCOME_MESSAGE)
                await turn_context.send_activity(self.PATTERN_MESSAGE)
    
    async def on_turn(self,turn_context:TurnContext):
        await super().on_turn(turn_context)
        await self._user_state.save_changes(turn_context)