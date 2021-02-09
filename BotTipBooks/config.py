#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "a14167e8-364e-4ad9-a762-34ebb7cbd52e")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "Progettocloud21")
    CONNECTION_NAME = os.environ.get("ConnectionName", "ConnessionePC")
    LUIS_APP_ID = os.environ.get("LuisAppId", "c9780681-5e74-4904-8ccd-d1b915bf0722")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "b91bd6d700ce4e229cc3dbdbf545f9d0")
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "luis-progettocloud.cognitiveservices.azure.com")
    KEY_AMAZON_API = os.environ.get("KeyAmazonApi", "A2E5C7D9C233454FAE27F2A0911C42A8")
    ENDPOINT_FIND_FUNCTION = os.environ.get("EndpointFindFunction", "https://bookscraping.azurewebsites.net/api/find-book")
    ENDPOINT_TEXT_ANALYSIS = os.environ.get("EndpointTextAnalysis", "https://textanalysisbottip.cognitiveservices.azure.com/")
    TEXT_KEY = os.environ.get("TextKey", "ad0fe521ef2646779cd35c06dd2cfd70")
