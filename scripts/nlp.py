# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

import wikipediaapi
from langdetect import detect_langs

# Instantiates a client
client = language.LanguageServiceClient()

# The text to analyze
text = u'Michelangelo Caravaggio, Italian painter, is known for "The Calling of Saint Matthew.'
wiki_lang = detect_langs(text)[0].lang
wiki_wiki = wikipediaapi.Wikipedia(wiki_lang)
document = types.Document(
    content=text,
    type=enums.Document.Type.PLAIN_TEXT)

# Detects the sentiment of the text
response = client.analyze_entities(document=document)

result = []
for entity in response.entities:
    result.append(wiki_wiki.page(entity.name).summary)

print("\n\n".join(result))

# print('Text: {}'.format(text))
# print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))
