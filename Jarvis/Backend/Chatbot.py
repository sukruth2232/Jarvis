import json
import datetime
from dotenv import dotenv_values
from groq import Groq

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

messages = []
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [{"role": "system", "content": System}]

# Try loading the chat log
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = json.load(f)
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        json.dump([], f)

# Realtime info function
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this realtime information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour}:{minute}:{second}\n"
    return data

# Modify the chatbot's response
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Main chatbot function
def ChatBot(query):
    try:
        # Load existing messages
        try:
            with open(r"Data\ChatLog.json", "r") as f:
                messages = json.load(f)
        except FileNotFoundError:
            messages = []

        # Append the user's query
        messages.append({"role": "user", "content": query})

        # Create the chat completion with streaming enabled
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "user", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1.0,
            stream=True  # Enable streaming
        )

        # Initialize the answer
        answer = ""

        # Iterate over the streamed response
        for chunk in completion:
            if hasattr(chunk, 'choices') and chunk.choices:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    answer += delta.content

        # Clean up the answer
        answer = answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": answer})

        # Save the updated messages
        with open(r"Data\ChatLog.json", "w") as f:
            json.dump(messages, f, indent=4)

        return AnswerModifier(answer)

    except Exception as e:
        print(f"[ERROR] {e}")
        return "Sorry, an error occurred. Please check the console for details."

# Main loop
if __name__ == "__main__":
    print("Chatbot is now ready! Please type your query and press Enter.")
    while True:
        user_input = input("Enter Your Question: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        else:
            response = ChatBot(user_input)
            print(f"Jarvis: {response}")
