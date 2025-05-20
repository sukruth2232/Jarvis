import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import mtranslate as mt

# Load language preference from .env
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage") or "en"

# HTML for voice input
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript + " ";
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            if (recognition) {
                recognition.stop();
                // Do not clear output
            }
        }
    </script>
</body>
</html>'''

# Inject selected language into HTML
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Save HTML file
os.makedirs("Data", exist_ok=True)
with open(r"Data\Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Setup Chrome options
current_dir = os.getcwd()
Link = f"{current_dir}/Data/Voice.html"

chrome_options = Options()
user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/89.0.142.86 Safari/537.36")
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")

# Remove --headless if not working with microphone access
# chrome_options.add_argument("--headless=new")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Setup assistant status file path
TempDirPath = rf"{current_dir}/Frontend/Files"
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

def QueryModifer(Query):
    new_query = Query.lower().strip()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can"]

    if any(word in new_query for word in question_words):
        if new_query[-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if new_query[-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

def SpeechRecognition(timeout=15):
    driver.get("file:///" + Link)
    driver.find_element(By.ID, "start").click()

    start_time = time.time()

    while True:
        try:
            Text = driver.find_element(By.ID, "output").text.strip()

            if Text:
                driver.find_element(By.ID, "end").click()

                if "en" in InputLanguage.lower():
                    return QueryModifer(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifer(UniversalTranslator(Text))

            # Timeout after X seconds
            if time.time() - start_time > timeout:
                driver.find_element(By.ID, "end").click()
                return "Speech timeout."

            time.sleep(1)

        except Exception as e:
            print("Error in recognition loop:", e)
            time.sleep(1)

if __name__ == "__main__":
    try:
        while True:
            Text = SpeechRecognition()
            print( Text)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        driver.quit()
