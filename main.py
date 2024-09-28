import os
import speech_recognition as sr
import pyttsx3
import json
from dotenv import load_dotenv
import google.generativeai as genai
import asyncio

# Load the .env file
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv('API_KEY'))

# Initialize text-to-speech engine
engine = pyttsx3.init()

# List available voices and set a female voice
voices = engine.getProperty('voices')
# Print available voices (optional for your reference)
for i, voice in enumerate(voices):
    print(f"Voice {i}: {voice.name} - {voice.languages}")
    
# Set the female voice (you may need to adjust the index based on your system's voices)
engine.setProperty('voice', voices[1].id)  # Change the index as needed

# Initialize Google Gemini Model
model = genai.GenerativeModel("gemini-1.5-flash")

# ANSI escape codes for colored printing
class Colors:
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    RED = "\033[31m"
    RESET = "\033[0m"

# Function to clean text by removing unwanted characters
def clean_text(text):
    return text.replace('#', '').replace('*', '')

# Function to speak text
def speak_text(text):
    clean = clean_text(text)
    engine.say(clean)
    engine.runAndWait()

# Modified function for speech-to-text with improved error handling
async def listen_command():
    recognizer = sr.Recognizer()
    max_attempts = 3
    for attempt in range(max_attempts):
        with sr.Microphone() as source:
            print(f"{Colors.YELLOW}Listening... (Attempt {attempt + 1}/{max_attempts}){Colors.RESET}")
            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                if attempt < max_attempts - 1:
                    print(f"{Colors.BLUE}No speech detected. Let's try again.{Colors.RESET}")
                    speak_text("I didn't hear anything. Please try again.")
                    continue
                else:
                    print(f"{Colors.RED}No speech detected after {max_attempts} attempts.{Colors.RESET}")
                    speak_text("I'm having trouble hearing you. Please check your microphone and try again later.")
                    return "timeout"

        try:
            print(f"{Colors.YELLOW}Recognizing...{Colors.RESET}")
            command = recognizer.recognize_google(audio, language="en-US")
            print(f"{Colors.CYAN}You said: {command}{Colors.RESET}")
            return command.lower()
        except sr.UnknownValueError:
            if attempt < max_attempts - 1:
                print(f"{Colors.BLUE}Sorry, I didn't catch that. Let's try again.{Colors.RESET}")
                speak_text("I didn't catch that. Please try again.")
            else:
                print(f"{Colors.RED}Failed to recognize speech after {max_attempts} attempts.{Colors.RESET}")
                speak_text("I'm having trouble understanding. Please try again later or check your microphone.")
                return "not_understood"
        except sr.RequestError as e:
            print(f"{Colors.RED}Could not request results; {e}{Colors.RESET}")
            speak_text("There was an error with the speech recognition service. Please check your network connection.")
            return "error"

# Function to generate response from the model using chat history
def generate_with_chat_history(question, chat_history):
    try:
        chat_history.append({"role": "user", "content": question})
        formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
        response = model.generate_content(formatted_history)
        chat_history.append({"role": "model", "content": response.text})

        return response.text
    except Exception as e:
        print(f"{Colors.RED}Error during response generation: {str(e)}{Colors.RESET}")
        return "I'm sorry, something went wrong while processing your request."

# Function to save chat history to a file
def save_chat_history(chat_history, filename="chat_history.json"):
    with open(filename, 'w') as file:
        json.dump(chat_history, file)

# Function to load chat history from a file
def load_chat_history(filename="chat_history.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return []  # Return an empty list if file doesn't exist

# Modified function to handle voice assistant (Lami)
async def lami_assistant():
    active_conversation = False
    chat_history = load_chat_history()
    
    # Ensure chat_history is a list
    if not isinstance(chat_history, list):
        chat_history = []

    while True:
        command = await listen_command()

        if command in ["timeout", "not_understood", "error"]:
            continue

        if "lami" in command:
            speak_text("I'm listening. What would you like to ask?")
            active_conversation = True
            continue

        if active_conversation:
            if "bye" in command or "exit" in command or "no thanks" in command:
                speak_text("Goodbye! I will wait for you to call Lami again.")
                active_conversation = False
                save_chat_history(chat_history)
                continue

            response = generate_with_chat_history(command, chat_history)

            if not response or response.strip() == "":
                print(f"{Colors.BLUE}No response generated. Please try asking again.{Colors.RESET}")
                speak_text("Sorry, I didn't get that. Could you ask again?")
                continue
            
            clean_response = clean_text(response)
            print(f"{Colors.GREEN}Lami: {clean_response}{Colors.RESET}")
            speak_text(clean_response)
        else:
            print(f"{Colors.YELLOW}Say 'Lami' to start a conversation.{Colors.RESET}")

# Start Lami assistant
if __name__ == "__main__":
    speak_text("Lami is ready to assist. Say 'Lami' to activate.")
    print(f"{Colors.MAGENTA}Starting Lami Assistant...{Colors.RESET}")
    asyncio.run(lami_assistant())  # Run the assistant with asyncio