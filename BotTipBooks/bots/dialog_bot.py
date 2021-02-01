# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, ConversationState, UserState, TurnContext
from botbuilder.dialogs import Dialog
from helpers.dialog_helper import DialogHelper
import os
import json
from typing import List
from botbuilder.schema import Attachment, ChannelAccount, ConversationReference
from bean import User
from botbuilder.dialogs.dialog_set import DialogSet


class DialogBot(ActivityHandler):
    def __init__(self, conversation_state: ConversationState,user_state: UserState, dialog: Dialog):
        if conversation_state is None:
            raise Exception("[DialogBot]: Missing parameter. conversation_state is required")
        if user_state is None:
            raise Exception("[DialogBot]: Missing parameter. user_state is required")
        if dialog is None:
            raise Exception("[DialogBot]: Missing parameter. dialog is required")
        
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog
    

    
    async def on_members_added_activity(self, members_added: List[ChannelAccount], turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                #welcome_card = self.create_adaptive_card_attachment()
                #response = MessageFactory.attachment(welcome_card)
                #await turn_context.send_activity(response)
                await DialogHelper.run_dialog(self.dialog,turn_context, self.conversation_state.create_property("DialogState"))


    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        # Save any state changes that might have occurred during the turn.
        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)

    async def on_message_activity(self, turn_context: TurnContext):
        await DialogHelper.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property("DialogState"),
        )
    
    # Load attachment from file.
    def create_adaptive_card_attachment(self):
        relative_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(relative_path, "../cards/welcomeCard.json")
        with open(path) as in_file:
            card = json.load(in_file)

        return Attachment(
            content_type="application/vnd.microsoft.card.adaptive", content=card
        )
    
