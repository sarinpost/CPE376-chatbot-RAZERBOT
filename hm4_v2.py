import json
import sys
import re
import eliza_mod as eliza

from flask import Flask, request, jsonify
import requests
import json

wireless_mouse = [
    'BASILISK ULTIMATE $149.99',
    'BASILISK X HYPERSPEED $59.99'
]

wired_mouse = [
    'VIPER MINI $39.99',
    'DEATHADDER V2 $69.99'
]

keyboard = [
    'HUNTSMAN $99.99',
    'BLACKWIDOW ELITE $169.99'
]

headset = [
    'HAMMERHEAD $99.99',
    'NARI ULTIMATE $199.99'
]

meaning_rules = {
    "?*x hello ?*y": [
        "Hello, I'm a RAZERBOT may i help you? (e.g. help)",
        ],
    "?*x help ?*y": [
        "May I help you?\nWhat do you want to know?\ntry to type some word or sentense? (contact, shop, product, support, problem)",
        ]
    }

contact_rules = {
    "?*x contact ?*y": [
        "How do you want to contact? Address or Website?",
        ],
    "?*x email ?*y": [
        "Please don't hesitate to send us an email at feedback@razer.com",
        ],
    "?*x address ?*y": [
        "Our Thailand Office 950/136, Royal River Place, Soi Rama 3, Rama 3 Road Bangphongphang Yannawa Bangkok 10120",
        ],
    "?*x tell ?*y": [
        "Call us Canada/US 1-855-872-5233 9AM-6PM PST 7 days/week.",
        ],
    "?*x website ?*y": [
        "Please visit our website https://www.razer.com/",
        ],
}

shopping_rules = {
    "?*x new ?*y product ?*z": [
        "The newest "+wired_mouse[0]+"",
        ],
    "?*x order ?*y": [
        "You can order products or shopping via online-store https://www.razer.com/store",
        ],
    "?*x online ?*y shop ?*z": [
        "Here is the RAZER online shopping https://www.razer.com/",
        ],
    "?*x shop ?*y": [
        "Our product are mouse, Keyboard and Headset. Which product do you want to know more detail?",
        ],
    "?*x review ?*y": [
        "Our team review product at https://www.youtube.com/user/cultofrazer",
        ],
    "?*x facebook ?*y": [
        "Here is the RAZER facebook page https://www.facebook.com/razer",
        ],
    "?*x store ?*y": [
        "You can visit our online store https://www.razer.com/store",
        ],
    "?*x promotion ?*y": [
        "During covid-19 products, free delivery when buying via online shop.",
        ],
}

products_detail_rules = {
    "?*x wireless mouse ?*y": [
        "I would like to propose "+wireless_mouse[0]+" it faster than any other wireless technology available.\nI recommend "+wireless_mouse[1]+" tracking accuracy and up to 16,000 DPI.",
        ],
    "?*x wire mouse ?*y": [
        "The newest "+wired_mouse[0]+", the ultra-lightweight gaming mouse.\nThe most in this era "+wired_mouse[1]+" a new era of high-performance gaming has already taken shape.",
        ],
}

support_rules = {
    "?*x light ?*y without ?*w Synapse ?*z": [
        "Without synapse you can't control the RGB lights.",
        ],
    "?*x download ?*y Synapse ?*z": [
        "Please visit https://www.razer.com/Synapse-2 then click 'DOWNLOAD NOW' button then install Synapse on your computer.",
        ],
    "?*x config ?*y light ?*z": [
        "To adjust the RGB setting, using Razer Synapse. Download Synapse here https://www.razer.com/Synapse-2\n1. Open 'Razer Synape'\n2. Click your device picture\n3. Click 'lighting'\n4. try to custom your device",
        ],
    "?*x disable ?*y light ?*z": [
        "1. Open 'Razer Synape'\n2. Click your device picture\n3. Click 'lighting'\n4. try to custom your device",
        ],
    "?*x DPI ?*y": [
        "To adjust the DPI setting, using Razer Synapse. Download Synapse here https://www.razer.com/Synapse-2\n1. Open 'Razer Synape'\n2. Click your device picture\n3. Click 'lighting'\n4. try to custom your device"
        ],
    "?*x warranty ?*y": [
        "Every product have 5 year warranty. Please visit https://support.razer.com for checking your device.",
        ],
}

problem_rules = {
    "?*x not ?*y work ?*z": [
        "1. try to unplug and plug agian\n2. factory reset in synapse\n3. reinstall synapse",
        ],
    "?*x factory ?*y reset ?*z": [
        "1. Open 'Razer Synape'\n2. Click 'setting' at the top right corner\n3. Click 'Reset'",
        ],
    "?*x reset ?*y config ?*z": [
        "1. Open 'Razer Synape'\n2. Click 'setting' at the top right corner\n3. Click 'Reset'",
        ],
    "?*x problem with ?*z": [
        "What is your problem with ?z?",
        ],
    "?*x Synapse ?*y detect ?*z": [
        "Uninstall RAZER Synapse and then Reinstall Synapse device driver.",
        "Try another USB port.",
        "Try connecting to different computer."
        ],
    "?*x detect?*z": [
        "try to unplug and plug agian",
        ],
    "?*x replace ?*y switch ?*z": [
        "You can replace a switch with backup switch that comes with the cover box."
        "For example please see https://www.youtube.com/watch?v=ja4U75kF1Jw"
        ],
    "?*x without ?*y Synapse ?*z": [
        "Sure, every device can work without Synapse."
        ],
    "?*x disable ?*y Synapse ?*z": [
        "Left click a RAZER logo at the bottom left corner of your desktop then click 'Exit'"
        ],
    "?*w headset ?*y one side ?*z": [
        "try plugging to another computer or phone, if that doesn't work, please tell me to claim"
        ],
    "?*x double click ?*y": [
        "You should decrease your mouse double-click speed in the Control Panel. If still doesn't work please ask for claim."
        ],
    "?*x double type ?*y": [
        "Your keyboard seems to have problems. Try to replace switch."
        ],
    "?*x scroll ?*y": [
        "You should try setting your mouse wheel in the Control Panel. If still doesn't work please ask for claim."
        ],
    "?*x driver ?*y": [
        "Normally the device driver has installed by Windows. Alternatively, Synapse can help you install driver."
        ],
    "?*x problem ?*z": [
        "What is your problem? \ne.g. mouse double click, Tunning DPI, Replace keyboard switch, headset work only one side"
        ],
}

general_rules = {
    "?*x what ?*y Synapse ?*z": [
        "Synapse is Software which allow you to customize your device. It necessary to use for custom your device",
        ],
    "?*x why ?*y Synapse ?*z": [
        "Synapse is Software which allow you to customize your device. It necessary to use for custom your device",
        ],
    "?*x config ?*y": [
        "To adjust your ?y setting, using Razer Synapse. Download Synapse here https://www.razer.com/Synapse-2",
        ],
    "?*x Synapse ?*z": [
        "Synapse is Software which allow you to customize your device.",
        ],
    "?*x product ?*y": [
        "Of course! Here are our product avaiable now\n\tmouse\n\tKeyboard\n\tHeadset\nEvery product can custimze by Synapse Software.",
        ],
    "?*x support ?*y": [
        "Please visit https://support.razer.com for online support webboard.",
        ],
    "?*x software ?*y": [
        "RAZER develop software that complete your gaming experience (e.g. Synapse)",
        ],
    "?*x mouse ?*y": [
        "We have high-performance gaming mouse. What are you looking for a wired mouse or wireless mouse?",
        ],
    "?*x macro ?*y": [
        "Use synapse for setting any macro with your device",
        ],
    "?*x keyboard ?*y": [
        "There are keyboards avaiable now.\n\tThe "+keyboard[0]+" avaiable in colors Classic Black, Quartz Pink and Mercury White a keyboard that instantly up-level the way you play.\n\tI would like to propose "+keyboard[1]+" giving you speed and responsiveness like never before."
        ],
    "?*x headset ?*y": [
        "There are headsets avaiable now.\n\tThe "+headset[0]+" high-quality sound you can enjoy anywhere.\n\t"+headset[1]+" a wireless PC gaming headset equipped with intelligent haptic technology developed."
        ],
    "?*x popular ?*y": [
        "the "+wireless_mouse[0]+" Is the most popular product.",
        ],
    "?*x RAZER ?*y": [
        "RAZER is a global gaming gear manufacturing company. You can ask me about products",
        "RAZER, We are Esports sponsor of many teams in competition using video games. You can ask me about products"
        ],
    "?*x RAZERBOT ?*y": [
        "I'm a bot of razer ",
        ],
    "?*x Esports ?*y": [
        "Esports (also known as electronic sports, e-sports, or eSports) is a form of sport competition using video games.",
        "Esports often takes the form of organized, multiplayer video game competitions, particularly between professional players, individually or as teams.",
        ],
    "?*x should ?*y buy ?*z": [
        "Which product do you want? Mouse, Keyboard or Headset?",
        ],
    "?*x buy ?*y": [
        "You can buy products or shopping via online-store https://www.razer.com/store",
        ],
    "?*x bye ?*y": [
        "See you later.",
        ],
}

default_responses = [
    "Please give me more detail.",
    "Sorry I can't understand, Please type 'help'",
    ]

word_group = [
    ['not', 'no', 'don\'t', 'didn\'t', 'won\'t', 'doesn\'t'],
    ['config', 'configuration', 'control', 'custom', 'customize', 'tune', 'command', 'change', 'set'],
    ['replace', 'swap', 'modify', 'adjust'],
    ['problem', 'trouble', 'issue', 'question', 'failure', 'fail', 'fix', 'repair', 'break'],
    ['disable', 'close', 'stop', 'quit', 'pause', 'exit'],
    ['shop', 'store'],
    ['buy', 'purchase', 'pay'],
    ['hello', 'hi'],
    ['bye', 'goodbye'],
    ['esports', 'e-sport', 'esport'],
    ['address', 'location'],
    ['website', 'web'],
    ['product', 'goods'],
    ['warranty', 'claim', 'request', 'insurance'],
    ['mouse', 'mice'],
    ['download', 'install'],
    ['popular', 'favorite', 'famous', 'top'],
    ['headset', 'earphone', 'headphone'],
    ['detect', 'detection'],
    ['scroll', 'wheel'],
    ['light', 'RGB', 'brightness', 'effect', 'color'],
    ['price', 'cost', 'charges']
]

def main():
    rules_list = []
    rules = {**meaning_rules , **contact_rules, **shopping_rules, **products_detail_rules, **support_rules, **problem_rules, **general_rules}
    for pattern, transforms in rules.items():
        pattern = eliza.remove_punct(str(pattern.upper()))
        transforms = [str(t).upper() for t in transforms]
        rules_list.append((pattern, transforms))
    # print('Please ask any question or type \'help\'.')
    while True:
        inputs = input('RAZERBOT> ')
        if inputs == 'exit':
            return
        response = eliza.interact(inputs, rules_list, word_group, list(map(str.upper, default_responses)))
        print(response)
        print('\n')

rules_list = []

app = Flask(__name__)

@app.route('/')
def MainFunction():
    return 'Hello world'

@app.route('/bot', methods=['POST'])
def BotPost():
    content = request.json
    replyToken = content['events'][0]['replyToken']
    inputs = content['events'][0]['message']['text']
    # print(content['events'][0]['replyToken'])
    response = eliza.interact(inputs, rules_list, word_group, list(map(str.upper, default_responses)))
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer aXD3XA6H0hV8YheNT4wurWq3rlHZ9XkyR45mgYb1AhNEwHsczlB8JykE4jIfV0gCvmo5B8Oes4OweNVQvf3j7ADsdGYnVbFMDFJ7rmbFudf370HmNj2mZKeklwaNv9LQzJ4hP2N0wdw99XVzfaFa/AdB04t89/1O/w1cDnyilFU=' 
    }
    data = {
        'replyToken': replyToken,
        'messages': [
            {  
                "type": "text",
                "text": response
            }
        ]
    }
    dataJSON = json.dumps(data)
    r = requests.post('https://api.line.me/v2/bot/message/reply', headers=headers, data=dataJSON)
    print(inputs)
    print(response)
    return content

def main2():
    global rules_list
    rules = {**meaning_rules , **contact_rules, **shopping_rules, **products_detail_rules, **support_rules, **problem_rules, **general_rules}
    for pattern, transforms in rules.items():
        pattern = eliza.remove_punct(str(pattern.upper()))
        transforms = [str(t).upper() for t in transforms]
        rules_list.append((pattern, transforms))
    app.run()

if __name__ == '__main__':
    main()