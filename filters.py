# Web
import bs4
import wikipediaapi
import requests
from flask import Flask
from flask import jsonify, request
from flask import send_file
from requests.exceptions import MissingSchema

# Google APIs
from google.cloud import translate
from google.cloud import language
from google.cloud import vision
from google.cloud.language import enums
from google.cloud.language import types
from google.cloud import speech
# from google.cloud.speech import enums
# from google.cloud.speech import types
from google.api_core.exceptions import InvalidArgument

# Language tools
from pymystem3 import Mystem
from censure import Censor
from nltk.tokenize import word_tokenize
from langdetect import detect_langs

# Image tools
from PIL import Image

# System
import io
import os
import six
import hashlib 
import os
import subprocess
from filetype import filetype


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route("/hello", methods=["GET", "POST"])
def hello():
    return jsonify({"value": "Hello, World!"}), 200

@app.route("/summarize", methods=['POST'])
def summarize():
    json = request.json
    r = requests.post(
        "https://api.deepai.org/api/summarization",
        data={
            'text': json["value"],
        },
        headers={'api-key': '57812b34-4ae9-4f6a-bbaf-e5dcd2b20241'}
    )
    if "output" in r.json().keys():
        return jsonify({"value": r.json()["output"]}), 200
    else:
        return jsonify(json), 200

@app.route("/translate", methods=['POST'])
def translate_():
    json = request.json
    text = json["value"]
    translate_client = translate.Client()
    target = 'en'
    print(target)
    translation = translate_client.translate(text, target_language=target)
    return jsonify({"value": translation['translatedText']}), 200


@app.route("/extract_meduza", methods=['POST'])
def extract_meduza():
    json = request.json
    url = json["value"]
    try:
        res = requests.get(url)
    except MissingSchema:
        return jsonify({"value": "You send not url text!"}), 200
    bs = bs4.BeautifulSoup(res.text)
    title = bs.findAll("h1", attrs={"class": "RichTitle-root"})
    if title:
        title = title[0].text.replace("\xa0", " ")
    else:
        title = ''

    paragraphs = "\n".join([text.text.replace("\xa0", " ") for text in bs.findAll("p", attrs={"class": "SimpleBlock-p"})])
    if len(title) == 0 and len(paragraphs) == 0:
        return jsonify({"value": "The link is empty :("}), 200
    else:
        return jsonify({"value": title + "\n\n" + paragraphs}), 200


@app.route("/extract_buzzfeed", methods=['POST'])
def extract_buzzfeed():
    json = request.json
    url = json["value"]
    try:
        res = requests.get(url)
    except MissingSchema:
        return jsonify({"value": "Вы отпривили не url!"}), 200
    bs = bs4.BeautifulSoup(res.text)
    title = bs.findAll("h1", attrs={"class": "news-article-header__title"})
    if title:
        title = title[0].text.replace("\xa0", " ")
    else:
        title = ''
    paragraphs = "\n".join([text.text.replace("\xa0", " ") for text in bs.findAll("p")])
    if len(title) == 0 and len(paragraphs) == 0:
        return jsonify({"value": "The link is empty :("}), 200
    else:
        return jsonify({"value": title + "\n\n" + paragraphs}), 200

@app.route("/nlp", methods=['POST'])
def nlp():
    client = language.LanguageServiceClient()
    text = request.json["value"]
    # The text to analyze
    # text = u'Michelangelo Caravaggio, Italian painter, is known for "The Calling of Saint Matthew.'
    wiki_lang = detect_langs(text)[0].lang
    wiki_wiki = wikipediaapi.Wikipedia(wiki_lang)
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    # Detects the sentiment of the text
    try:
        response = client.analyze_entities(document=document)

        result = []
        for entity in response.entities:
            result.append(wiki_wiki.page(entity.name).summary)

        return jsonify({"value": "\n\n".join(result)}), 200
    except InvalidArgument:
        return jsonify({"value": "Can not find named enteties"}), 200

@app.route("/landmark", methods=['POST'])
def detect_landmarks():
    """Detects landmarks in the file."""
    client = vision.ImageAnnotatorClient()
    img = request.data


    image = vision.types.Image(content=img)

    response = client.landmark_detection(image=image)
    landmarks = response.landmark_annotations
    print('Landmarks:')

    for landmark in landmarks:
        print(landmark.description)
        for location in landmark.locations:
            lat_lng = location.lat_lng
            print('Latitude {}'.format(lat_lng.latitude))
            print('Longitude {}'.format(lat_lng.longitude))
    if landmarks:
        return jsonify({"value": landmarks[0].description}), 200
    else:
        return jsonify({"value": "Found nothing"}), 200

@app.route("/censor", methods=['POST'])     
def censor():
    text = request.json["value"]
    mystem_analyzer = Mystem()
    lang = detect_langs(text)[0].lang
    if lang not in ["ru", "en"]:
        return jsonify({"value": "Your language is not supported"}), 200
    cnsr = Censor().get(lang=lang)
    tokens = word_tokenize("".join(mystem_analyzer.lemmatize(text)))
    for i, token in enumerate(tokens):
        if not cnsr.check_word(token)['is_good']:
            tokens[i] = '*' * len(token)
    return jsonify({"value": " ".join(tokens)}), 200


@app.route("/distort", methods=['POST'])
def distort_image():
    image_data = request.data
    max_image_size = 500

    type = filetype.guess(image_data)
    ext = type.extension
    mime = type.mime
    if mime.split("/")[0] != "image":
        return "Wrong input type!", 400

    md5 = hashlib.md5()
    md5.update(image_data)
    pic_name = md5.hexdigest()
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "media") 
    image = Image.open(io.BytesIO(image_data))
    width, height = image.size
    if width > max_image_size or height > max_image_size:
        max_param = max(width, height)
        coef = max_image_size / max_param
        width, heigth = int(width * coef), int(height * coef)
        image = image.resize((width, width), Image.ANTIALIAS)
    image.save(os.path.join(path, pic_name) + f'.{ext}')

    pics = []
    width, height = image.size
    for index, ratio in enumerate(range(95, 0, -5)):
        compress_command = f'convert {pic_name}.{ext} -liquid-rescale {ratio}%x{ratio}%! {pic_name}_distorted{index}.{ext}'
        resize_command = f'convert {pic_name}_distorted{index}.{ext} -resize {width}x{height} {pic_name}_distorted{index}.{ext}'
        process = subprocess.Popen(compress_command.split(" "), stdout=subprocess.PIPE, cwd=path)
        output, error = process.communicate()
        process = subprocess.Popen(resize_command.split(" "), stdout=subprocess.PIPE, cwd=path)
        output, error = process.communicate()
        pics.append(f'{pic_name}_distorted{index}.{ext}')

    gif_command = f'convert -loop 0 -delay 15 {" ".join(pics)} {pic_name}.gif'
    process = subprocess.Popen(gif_command.split(" "), stdout=subprocess.PIPE, cwd=path)
    output, error = process.communicate()
    return send_file(os.path.join(path, f'{pic_name}.gif'))


@app.route("/classify_text", methods=['POST'])
def classify_text():
    """Classifies content categories of the provided text."""
    client = language.LanguageServiceClient()
    text = request.json["value"]
    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')
    
    document = types.Document(
        content=text.encode('utf-8'),
        type=enums.Document.Type.PLAIN_TEXT)

    def preprocess_category_name(category):
        return "#" + category[1:].replace(" & ", "And")
    try:
        categories = [preprocess_category_name(category.name) for category in client.classify_text(document).categories]
        return jsonify({"value": " ".join(categories) + '\n\n' + text}), 200
    except InvalidArgument:
        return jsonify({"value": text}), 200


@app.route("/speech2text", methods=['POST'])
def speech2text():
    client = speech.SpeechClient()
    voice_data = request.data
    audio = speech.types.RecognitionAudio(content=voice_data)
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16, 
        sample_rate_hertz=16000, 
        language_code='en-US'
    )

    response = client.recognize(config, audio)
    if response.results:
        return jsonify({"values": response.results[0].alternatives[0].transcript})
    else:
        return jsonify({"values": "Could not recognize"})





if __name__ == '__main__':
    app.run(host="0.0.0.0")
