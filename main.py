import os
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
import google.generativeai as genai

# Load the .env file
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv('API_KEY'))

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set up memory details
memory = """
My name is Muhammed Sajad PP. I'm a multifaceted professional with expertise in backend development, video editing, photography, web design, SEO, and machine learning. I am the founder and CEO of Grovix Lab.
"""

# Initialize Google Gemini Model
model = genai.GenerativeModel("gemini-1.5-flash")

# ANSI escape codes for colored printing
class Colors:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    RESET = "\033[0m"

# Function to speak text
def speak_text(text):
    # Remove unwanted characters before speaking
    clean_text = text.replace('#', '').replace('*', '')
    engine.say(clean_text)
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
            print(f"{Colors.BLUE}Sorry, I didn't catch that.{Colors.RESET}")
        except sr.RequestError as e:
            speak_text("Could not request results, please check your network.")
        return ""

# Function to generate response from the model using chat history
def generate_with_memory(question, chat_history):
    # Add the current question to the chat history
    chat_history.append({"role": "user", "content": question})

    # Format the chat history for the model
    formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])

    # Generate the response from the model
    response = model.generate_content(formatted_history)
    
    # Add the model's response to the chat history
    chat_history.append({"role": "model", "content": response.text})

    return response.text

# Function to handle voice assistant (Lami)
def lami_assistant():
    active_conversation = False
    chat_history = []  # Initialize chat history

    while True:
        command = listen_command()

        if "lami" in command:
            speak_text("I'm listening. What would you like to ask?")
            active_conversation = True
            
            while active_conversation:
                question = listen_command()

                if question:
                    # Check for exit command
                    if "bye" in question or "exit" in question:
                        speak_text("Goodbye! I will wait for you to call Lami again.")
                        active_conversation = False
                    else:
                        # Generate response from the model based on question and chat history
                        response = generate_with_memory(question, chat_history)
                        # print(f"{Colors.GREEN}Lami's Response: {response}{Colors.RESET}")
                        speak_text(response)

        # Optional: Handle other commands or actions here if needed

# Start Lami assistant
if __name__ == "__main__":
    speak_text("Lami is ready to assist. Say 'Lami' to activate.")
    print(f"{Colors.MAGENTA}Starting Lami Assistant...{Colors.RESET}")
    lami_assistant()
