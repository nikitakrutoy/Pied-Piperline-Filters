import requests
import os

HOST = "http://localhost:5000"
ENDPOINTS = [
    # ("/summarize", "text"),
    # ("/extract_meduza", "link"),
    # ('/extract_buzzfeed', "link"),
    # ("/landmark", "image"),
    # ("/distort", "image"),
    ("/censor", "text"),
    ("/classify_text", "text"),
    ("/translate", "text"),
    ("/nlp", "text"),
    # ("/speech2text", "voice"),
]
TEXT_EXAMPLES = [
    "When it comes to romance, watching a great movie can be the perfect way for couples to pass the time and get a little closer. They're entertaining, easily shared experiences, and they tend to teach us a thing or two about each other's tastes. Not only that, but movies can also be a great excuse to get cozy next to that special someone on the couch or love seat. You can't say the same for reading a magazine, right? No one ever got married after sharing a copy of Newsweek.But some films, while they're great, are movies you should never watch with your partner. Why? Because you'll probably want to avoid arguments, general awkwardness, or even an air of sudden distrust. Nothing makes your sofa go from snuggle-central to the creepy zone quicker than these movies. The films on this list are totally worth your time…as long as you're by yourself.",
    'Michelangelo Caravaggio, Italian painter, is known for "The Calling of Saint Matthew.',
    'Chau had a plan to try and win the Sentinelese tribe’s trust, Ramsey said. He would try to go alone and be unthreatening. He would befriend them by giving them gifts. He would also use body language, since they do not speak the same language. It’s unknown what language the Sentinelese speak.According to the Post, a teenager from the Sentinelese tribe had shot an arrow at Chau, piercing his waterproof Bible, during his initial trip to the remote island.“He wanted to first get to know them a little bit; learn the language. Then eventually share the gospel to them, and translate the Bible into that language,” said Ramsey.Chau shared his idea with others, Ramsey said, noting that a “fair amount” of people knew and it wasn’t just limited to his close friends. Chau had an email list that he would regularly send updates to when he was traveling, including his plan to visit the Sentinelese, Ramsey said.“Instead of saying ‘God,’ he would say ‘dad,’ so there wouldn’t be any governmental interception,” Ramsey said. “He knew what he was doing wasn’t exactly legal.”“What I knew about these people was only through him,” Ramsey said. “I suppose I did think things would go better, not that I’m surprised that they didn’t.”Chau moved around a lot, and worked various jobs. “It’s never easy to answer to What does he do? and Where does he live? Ramsey said. Chau worked as a forest ranger, spending summers in Northern California, Ramsey said. He studied sports medicine at Oral Roberts University in Tulsa, Oklahoma.',
    "Хеллоу сука ебанная"
]

LINK_EXAMPLES = [
    "https://meduza.io/short/2018/11/24/politsiya-protiv-zheltyh-zhiletov-v-parizhe-oni-vtoruyu-nedelyu-protestuyut-protiv-tsen-na-benzin-fotografiya",
    "https://meduza.io/feature/2018/11/23/pobeg-iz-tyurmy-dannemora-kriminalnyy-serial-bena-stillera-osnovannyy-na-realnoy-istorii",
    "https://meduza.io/feature/2018/11/24/bylo-li-russkoe-ekonomicheskoe-chudo",
    "https://www.buzzfeednews.com/article/chrisgeidner/trump-transgender-military-ban-supreme-court",
    "https://www.buzzfeednews.com/article/hazelshearing/paris-protests-police-gas-prices",
    "https://www.buzzfeednews.com/article/amberjamieson/american-missionary-told-friends-years-in-advance-hed",
]


PROJECT_DIR = os.path.abspath("../")
IMAGE_EXAMPLES = [
    os.path.join(PROJECT_DIR, "pics/c.jpg"),
    os.path.join(PROJECT_DIR, "pics/telka.png"),
    os.path.join(PROJECT_DIR, "pics/iur.jpeg"),
    os.path.join(PROJECT_DIR, "pics/iu-8.jpeg"),
    os.path.join(PROJECT_DIR, "pics/maxresdefault.jpg"),
    os.path.join(PROJECT_DIR, "pics/iu-3.png"),
]


VOICE_EXAMPLES = []

TYPES_EXAMPLES = {
    "text": TEXT_EXAMPLES,
    "link": LINK_EXAMPLES,
    "image": IMAGE_EXAMPLES,
    "voice": VOICE_EXAMPLES,
}

def check_api():

    for endpoint, type in ENDPOINTS:
        examples = TYPES_EXAMPLES[type]
        for i, example in enumerate(examples):
            print(endpoint, i)
            if type == "text" or type == "link":
                res = requests.post(HOST + endpoint, json={"value": example})
                print(endpoint, type, i,)
                print(res.json())
            if type == "image":
                with open(example, "rb") as image_file:
                    image_data = image_file.read()
                    res = requests.post(HOST + endpoint, data=image_data)
                    if "distort" in endpoint:
                        with open("./endpoint" + str(i) + ".gif", "wb") as image_file:
                            image_file.write(res.content)
                            print(endpoint, type, i, "saved")
                    else:
                        print(endpoint, type, i, res.json()["value"])


check_api()