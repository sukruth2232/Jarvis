from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import os
import asyncio
import keyboard

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

classes = ["zCubwf", "hgKElc", "LTKOO SY7ric", "Z0LcW", "gsrt vk_bk FzvWsb YwPhnf", "pclqee",
           "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "05uR6d LTKOO", "vlzY6d",
           "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e",
           "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

useragent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
             '(KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36')

client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with",
    "I'm glad I could help; if you have any other questions or need further assistance"
]

messages = []
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username','Assistant')}, You're a content writer. You have to write content like a letter."}]


def GoogleSearch(Topic):
    search(Topic)
    return True


def Content(Topic):
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = Topic.replace("Content", "").strip()
    ContentByAI = ContentWriterAI(Topic)
    filename = rf"Data\{Topic.lower().replace(' ', '')}.txt"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(filename)
    return True

def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True


def PlayYoutube(query):
    playonyt(query)
    return True


def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                print("Failed to retrieve search results")
                return None

        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])
        return True


def CloseApp(app):
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False


def System(command):
    if command == "mute":
        keyboard.press_and_release("volume mute")
    elif command == "unmute":
        keyboard.press_and_release("volume unmute")
    elif command == "volume_up":
        keyboard.press_and_release("volume up")
    elif command == "volume_down":
        keyboard.press_and_release("volume down")


async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        cmd = command.lower().strip()
        if cmd.startswith("open"):
            fun = asyncio.to_thread(OpenApp, cmd.removeprefix("open").strip())
            funcs.append(fun)
        elif cmd.startswith("close"):
            fun = asyncio.to_thread(CloseApp, cmd.removeprefix("close").strip())
            funcs.append(fun)
        elif cmd.startswith("play"):
            fun = asyncio.to_thread(PlayYoutube, cmd.removeprefix("play").strip())
            funcs.append(fun)
        elif cmd.startswith("content"):
            fun = asyncio.to_thread(Content, cmd.removeprefix("content").strip())
            funcs.append(fun)
        elif cmd.startswith("google search"):
            fun = asyncio.to_thread(GoogleSearch, cmd.removeprefix("google search").strip())
            funcs.append(fun)
        elif cmd.startswith("youtube search"):
            fun = asyncio.to_thread(YouTubeSearch, cmd.removeprefix("youtube search").strip())
            funcs.append(fun)
        elif cmd.startswith("system"):
            fun = asyncio.to_thread(System, cmd.removeprefix("system").strip())
            funcs.append(fun)
        else:
            print(f"No function found for: {command}")
    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True

