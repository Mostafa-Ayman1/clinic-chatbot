# 🏥 AI Clinic Chatbot

An AI-powered virtual receptionist for medical clinics that answers patient questions, manages appointment bookings, and routes requests using an AI Router. The application is built with **Gradio**, **OpenAI**, **n8n**, and **Google Sheets**.

---

## ✨ Features

- 🤖 **AI Router (Design Pattern)**
  - Uses an AI Router Agent to classify each patient message and forward it to the appropriate agent:
    - Greeting Agent
    - FAQ Agent
    - Booking Agent
    - Medical Safety Agent

- 📚 **FAQ Agent**
  - Extracts keywords from the patient's message.
  - Retrieves the most relevant answer from a Google Sheets knowledge base through **n8n**.

- 📅 **Booking Agent**
  - Collects:
    - Full Name
    - Phone Number
    - Medical Specialty
    - Preferred Date & Time
  - Sends the booking request to **n8n**, which formats the date and stores the appointment in Google Sheets.

- 🩺 **Medical Safety**
  - Detects requests for medical diagnosis or treatment.
  - Politely declines and advises the patient to consult a healthcare professional.

---

## 🧠 Architecture

The chatbot follows an **AI Router Design Pattern**.

Instead of handling every request with a single prompt, an AI Router first determines the user's intent, then forwards the conversation to the most suitable specialized agent.

```text
                User Message
                     │
                     ▼
             AI Router Agent
                     │
     ┌───────────────┼───────────────┐───────────────┐
     ▼               ▼               ▼               ▼
 Greeting        FAQ Agent      Booking Agent   Medical Safety
```

This modular architecture makes the system easier to maintain, extend, and scale.

---

## ⚙️ Tech Stack

- Python
- Gradio
- OpenAI API
- n8n
- Google Sheets
- python-dotenv

---

## 🔄 n8n Workflow

The chatbot communicates with **n8n** through a webhook.

The workflow is responsible for:

- Searching FAQs in Google Sheets
- Checking doctor availability
- Formatting appointment dates
- Saving bookings
- Returning the final response


---

## 📂 Project Structure

```text
.
├── main.py
├── prompts.py
├── agents.py
├── config.py
├── .env
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

Clone the repository

```bash
git clone [<repository-url>](https://github.com/Mostafa-Ayman1/clinic-chatbot.git)
cd clinic-chatbot
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
OPENAI_API_KEY=
OPENAI_API_BASE=
OPENAI_MODEL=
N8N_WEBHOOK=
```

Run the application

```bash
python main.py
```

Gradio will generate a local URL to start chatting with the assistant.

---

## 📋 Requirements

- Python 3.10+
- Gradio
- OpenAI
- n8n
- Google Sheets

---

## 📌 Notes

- FAQ data is managed in Google Sheets.
- Appointment bookings are processed automatically through n8n.
- Medical diagnosis and treatment recommendations are intentionally not provided for patient safety.
