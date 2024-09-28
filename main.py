import os
import speech_recognition as sr
import pyttsx3
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load the .env file
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv('API_KEY'))

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize Google Gemini Model
model = genai.GenerativeModel("gemini-1.5-flash")

# ANSI escape codes for colored printing
class Colors:
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    RESET = "\033[0m"

# Function to clean text by removing unwanted characters
def clean_text(text):
    return text.replace('#', '').replace('*', '')

# Function to speak text
def speak_text(text):
    clean = clean_text(text)
    engine.say(clean)
    engine.runAndWait()

# Function for speech-to-text
def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"{Colors.YELLOW}Listening...{Colors.RESET}")
        audio = recognizer.listen(source)

        try:
            print(f"{Colors.YELLOW}Recognizing...{Colors.RESET}")
            command = recognizer.recognize_google(audio)
            print(f"{Colors.CYAN}You said: {command}{Colors.RESET}")
            return command.lower()
        except sr.UnknownValueError:
            return "not_understood"
        except sr.RequestError as e:
            speak_text("Could not request results, please check your network.")
            return "error"

# Function to generate response from the model using chat history
def generate_with_chat_history(question, chat_history):
    try:
        chat_history.append({"role": "user", "content": question})
        formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
        response = model.generate_content(formatted_history)
        chat_history.append({"role": "model", "content": response.text})

        # Debugging: Log response text
        print(f"{Colors.BLUE}Generated Response: {response.text}{Colors.RESET}")
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
    return []

# Function to handle voice assistant (Lami)
def lami_assistant():
    active_conversation = False
    chat_history = load_chat_history()
    lami_called = False

    while True:
        command = listen_command()

        # Check if user said "Lami" to start the assistant
        if "lami" in command:
            speak_text("I'm listening. What would you like to ask?")
            active_conversation = True
            lami_called = True

        # Once "Lami" is called, continue to listen and respond
        if active_conversation:
            question = listen_command()

            # If the bot didn't understand the speech, do not call the API
            if question == "not_understood":
                print(f"{Colors.BLUE}Sorry, I didn't catch that.{Colors.RESET}")
                continue

            if question:
                # Check for exit command
                if "bye" in question or "exit" in question:
                    speak_text("Goodbye! I will wait for you to call Lami again.")
                    active_conversation = False
                    lami_called = False
                    save_chat_history(chat_history)
                    continue

                # Generate response using the API
                response = generate_with_chat_history(question, chat_history)

                # If no response is generated, prompt user to ask again
                if not response or response.strip() == "":
                    print(f"{Colors.BLUE}No response generated. Please try asking again.{Colors.RESET}")
                    speak_text("Sorry, I didn't get that. Could you ask again?")
                    continue
                
                # Clean and print the response text
                clean_response = clean_text(response)
                print(f"{Colors.GREEN}Lami: {clean_response}{Colors.RESET}")

                # Speak the cleaned response
                speak_text(clean_response)

        # Optional: Handle other commands or actions here if needed

# Start Lami assistant
if __name__ == "__main__":
    speak_text("Lami is ready to assist. Say 'Lami' to activate.")
    print(f"{Colors.MAGENTA}Starting Lami Assistant...{Colors.RESET}")
    lami_assistant()
