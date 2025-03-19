# 🤖 AI Voice Agent for Lead Nurturing 🤖

## 📝 Description

This project is an AI Voice Agent designed to interact with prospects through voice conversations, collect relevant information, and improve lead segmentation and personalization. The assistant leverages pre-trained language models and speech recognition to understand user intent, extract key information, and provide helpful responses.

## 🚀 Features

1. 🧠 LLM Integration

    * Utilizes GPT and Whisper for text and voice processing.

    * Implements LangChain to manage conversation flow.

    * Loads, processes, and customizes models for personalized responses.

2. 🔤 Natural Language Processing (NLP)

    * Detects user intent (e.g., product interest, service inquiries, specific requirements).

    * Extracts key information such as name, company, needs, and estimated budget.

3. 🎙️ Voice Interaction

    * Uses automatic speech recognition (ASR) to convert spoken responses into text.

    * Implements text-to-speech (TTS) to generate voice responses.

    * Maintains conversation context across multiple interactions.

4. 🗣️ Intelligent Dialogue Flow

    * Guides the lead through a structured conversation.

    * Enriches the lead profile by integrating relevant information effectively.

5. 📊 CRM & Database Integration

    * Stores and updates lead information in a CRM or database.

    * Manages authentication, CRM API interaction, and data synchronization.

6. 🛠️ Error Handling & Ambiguity Resolution

    * Detects and corrects user input errors.

    * Requests clarification naturally when needed.

7. 🔍 Testing

    * Implements unit tests to verify system components.

## 📂 Project Structure

```bash
voice-ai-agent/
│-- pdf/                    # Pdfs from the company, to complete missing information, and save into Vector DB
│-- src/
│   ├── app.py              # Entry point, UI rendering (Streamlit), message handling
│   ├── agent.py            # LLM integration with different tools
│   ├── database.py         # Database management (Vector DB & SQL DB)
│   ├── config.py           # Configuration settings (keys, properties, paths)
│   ├── html_templates.py   # HTML templates for Streamlit
│   ├── validator.py        # Name validation using LLM
│   ├── utils.py            # Utility functions to serve different components
│-- tests/                  # Unit tests
│-- README.md               # Project documentation
```

Also, there are some folders that will be generated once the system is running:

```bash
│-- audio/                  # Save the last user and bot audio
│-- chroma/                 # The in memory vector DB, to save pdf and web information about the company
│-- chatbot_db.sqlite/      # Relational DB, to save basic user information
```
## ⚙️ Installation

### Clone the repository:
```bash
git clone https://github.com/matisanchz/voice-ai-agent.git
```
#### Go to the folder:
```bash
cd voice-ai-agent
```
### Install dependencies:
```bash
pip install -r requirements.txt
```

**IMPORTANT:** Set up environment variables in a .env file.

The .env file contains important information about the API KEYS. To run the project, you must define:

* OPENAI_API_KEY='' -> To connect with the LLM.
* TAVILY_API_KEY='' -> To search on the internet as RAG.
* UPSTASH_REDIS_REST_URL='' -> To connect with the Redis vector dabase.
* UPSTASH_REDIS_REST_TOKEN='' -> To connect with the Redis vector dabase.

Also, there are environment variables to define the URLs to scrape (in this case, they are hardcoded).

* ATOM_URL_ABOUT_US='https://atomchat.io/acerca-de-nosotros/'
* ATOM_URL_AGENT_AUTOMOTIVE='https://atomchat.io/ai-agents-para-industria-automotriz/'
* ATOM_URL_AGENT_EDUCATION='https://atomchat.io/ai-agents-para-universidades-instituciones-educativas/'
* ATOM_URL_AGENT_FINANCE='https://atomchat.io/vende-productos-fintech-con-ai-agents/'
* ATOM_URL_INTEGRATIONS_HUBSPOT='https://atomchat.io/hubspot-con-whatsapp/'
* ATOM_URL_INTEGRATIONS_TALKDESK='https://atomchat.io/talkdesk/'
* ATOM_URL_INTEGRATIONS_OTHER='https://atomchat.io/integraciones-atom/'
* ATOM_URL_SUCCESS_STORIES='https://atomchat.io/casos-de-exito/'
* ATOM_URL_PARTNERS='https://atomchat.io/partners/'
* ATOM_URL_EVENTS='https://atomchat.io/eventos/'

This information will serve to the RAG of the model.

### Run the application:
```bash
streamlit run src/app.py
```

### Run tests
Go to the folder src, and execute
```bash
cd .\src\
python -m unittest tests/test_database.py
python -m unittest tests/test_agent.py
python -m unittest tests/test_utils.py
python -m unittest tests/test_validator.py
```
## 📚 Usage

1. Complete your basic information in order to start the voice/chat assistance. The bot will guide you through the different services, features and prices from the company. 

2. You can use text or voice.

3. The assistant will collect all your information.

4. Data is stored in the database for further analysis and segmentation.

5. You can start and navigate through different sessions.

## ✅ Example:

In the example.pdf you will see a simple use case of the chatbot.
