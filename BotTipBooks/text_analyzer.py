from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from typing import List


class TextAnalyzer:
    def __init__(self):
        self.client = self.authenticate_client()


    def authenticate_client(self):
        ta_credential = AzureKeyCredential("ad0fe521ef2646779cd35c06dd2cfd70")
        text_analytics_client = TextAnalyticsClient(
                endpoint="https://textanalysisbottip.cognitiveservices.azure.com/", 
                credential=ta_credential)
        return text_analytics_client


    def sentiment_analysis(self, list: List):
        results=[]
        response = self.client.analyze_sentiment(documents=list)
        for result in response:
            if result.sentiment == "negative" and result.confidence_scores.negative>=0.8:
                results.append(result.sentiment)
            elif result.sentiment == "positive" or result.sentiment == "neutral":
                results.append(result.sentiment)
        
        n_positive=0
        n_negative=0
        n_neutral=0
        for res in results:
            if res=="positive":
                n_positive+=1
            elif res=="negative":
                n_negative+=1
            elif res=="neutral":
                n_neutral+=1
        dic={"positive": n_positive,
            "negative": n_negative,
            "neutral": n_neutral
        }

        negative_sentences = []

        for res in response:
            for i, sentence in enumerate(res.sentences):
                if sentence.sentiment == "negative" and sentence.confidence_scores.negative>=0.9:
                    negative_sentences.append(sentence.text)
                    print(sentence)
        return dic, negative_sentences
            
