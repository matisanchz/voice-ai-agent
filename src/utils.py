import os
import base64
from datetime import datetime
from dotenv import load_dotenv
import openai
import streamlit as st

from html_templates import get_audio_template
from config import settings

load_dotenv()

audio_path = settings.AUDIO_PATH

def save_audio(recorded_audio, file_name):
    if not os.path.exists(audio_path):
        os.makedirs(audio_path)

    with open(audio_path+file_name, "wb") as f:
        f.write(recorded_audio)

def audio_to_text(file_name):
    with open(audio_path+file_name, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return transcript.text
    
def text_to_audio(text):
    response = openai.audio.speech.create(model="tts-1", voice="onyx", input=text)
    return response.content

def play_audio(file_name):
    with open(audio_path+file_name, "rb") as audio_file:
        audio_bytes = audio_file.read()
    base64_audio=base64.b64encode(audio_bytes).decode("utf-8")
    st.markdown(get_audio_template(base64_audio), unsafe_allow_html=True)

def get_timestamp():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

def get_countries():
    return ["Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria",
        "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan",
        "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia",
        "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo (Congo-Brazzaville)", "Costa Rica",
        "Croatia", "Cuba", "Cyprus", "Czechia (Czech Republic)", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador",
        "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini (Swaziland)", "Ethiopia", "Fiji", "Finland", "France",
        "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau",
        "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland",
        "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kuwait", "Kyrgyzstan",
        "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar",
        "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia",
        "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar (Burma)", "Namibia", "Nauru", "Nepal",
        "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway", "Oman", "Pakistan",
        "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar",
        "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia",
        "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa",
        "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Tajikistan",
        "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu",
        "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela",
        "Vietnam", "Yemen", "Zambia", "Zimbabwe"
    ]

def get_all_pdf_files():
    all_files = []
    for root, dirs, files in os.walk(settings.PDF_PATH):
        for file in files:
            all_files.append(os.path.join(root, file))
    return all_files

def get_all_urls():
    return [os.getenv("ATOM_URL_ABOUT_US"), os.getenv("ATOM_URL_AGENT_AUTOMOTIVE"), os.getenv("ATOM_URL_AGENT_EDUCATION"), 
            os.getenv("ATOM_URL_AGENT_FINANCE"), os.getenv("ATOM_URL_INTEGRATIONS_HUBSPOT"), os.getenv("ATOM_URL_INTEGRATIONS_TALKDESK"),
            os.getenv("ATOM_URL_INTEGRATIONS_OTHER"), os.getenv("ATOM_URL_SUCCESS_STORIES"), os.getenv("ATOM_URL_PARTNERS"),
            os.getenv("ATOM_URL_EVENTS")]

def get_first_msg(user):
    name, _, company, country, budget = user
    return f"""
        ¡Hola {name}, bienvenido a AtomChat.io! 👋 Soy tu asistente virtual y estoy aquí para ayudarte a conocer más sobre nuestros servicios. 📢 
        Veo que eres parte de {company} en {country} y que tu presupuesto es {budget}. Estoy aquí para guiarte y responder cualquier consulta que tengas sobre nuestros planes, funcionalidades y medios de pago.
        Si necesitas información específica o tienes alguna duda, dime en qué puedo ayudarte. ¡Estoy listo para asistirte! 😊 No dudes en utilizar el microfono, o la casilla de texto para enviar tus preguntas. 
        """