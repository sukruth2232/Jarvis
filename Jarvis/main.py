from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessages = f'''{Username}:Hello {Assistantname},How are You?
{Assistantname}:Hello {Username},I am good,thank you.'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    File = open(r'Data\ChatLog.json', "r", encoding='utf-8')
    if len(File.read()) < 5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessages)

def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:  # Fixed typo: 'josn_data' to 'json_data'
        if entry["role"] == "user":
            formatted_chatlog += f"User:{entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant:{entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("Username", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistantname", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatOnGUI():
    File = open(TempDirectoryPath('Database.data'), "r", encoding='utf-8')
    Data = File.read()
    if len(str(Data)) > 0:
        lines = Data.split('\n')
        result = '\n'.join(lines)  # Fixed duplicate line and typo: 'json' to 'join'
        File.close()
        File = open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8')
        File.write(result)
        File.close()

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatOnGUI()

InitialExecution()

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")  # Fixed typo: extra comma
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username}:{Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)  # Fixed typo: 'Decsion' to 'Decision'
    print("")
    print(f"Decision:{Decision}")  # Fixed typo
    print("")

    G = any([i for i in Decision if i.startswith("general")])  # Fixed typo
    R = any([i for i in Decision if i.startswith("realtime")])  # Fixed typo

    Merged_query = " and ".join(  # Fixed typo: 'Mearged_query' to 'Merged_query', 'json' to 'join'
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )
    
    for queries in Decision:  # Fixed typo
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True
    
    for queries in Decision:  # Fixed typo
        if TaskExecution == False:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))  # Fixed typo
                TaskExecution = True
    
    if ImageExecution == True:
        with open(r"Frontend\Files\Imageneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")
        
        try:
            p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'],  # Fixed: 'popen' to 'Popen'
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
            subprocesses.append(p1)  # Fixed: 'subprocess' to 'subprocesses'
        
        except Exception as e:
            print(f"Error:{e}")
    
    if G and R or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))  # Fixed typo
        ShowTextToScreen(f"{Assistantname} :{Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True
    else:
        for Queries in Decision:  # Fixed typo
            if "generate" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general", " ")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}:{Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "realtime" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("realtime", " ")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}:{Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "exit" in Queries:
                QueryFinal = "okay, Bye!"  # Added space after comma
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}:{Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                SetAssistantStatus("Answering...")  # Duplicate line, consider removing
                os._exit(1)

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." in AIStatus:
                SetAssistantStatus("Available...")

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    thread1 = threading.Thread(target=FirstThread, daemon=True)  # Fixed: thread2 to thread1 for clarity
    thread1.start()
    SecondThread()