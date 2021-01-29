#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "17137490-920c-4719-9d01-735c8358cb03")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "qFu_H-~0cImI9u_yP5PwoU07941LBMx465")
    CONNECTION_NAME = os.environ.get("ConnectionName", "NuovaConnessione")
    LUIS_APP_ID = os.environ.get("LuisAppId", "c9780681-5e74-4904-8ccd-d1b915bf0722")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "b91bd6d700ce4e229cc3dbdbf545f9d0")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "luis-progettocloud.cognitiveservices.azure.com")
