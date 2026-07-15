# 🏥 AI Clinic Chatbot

An AI-powered virtual receptionist for medical clinics. The chatbot helps patients by answering frequently asked questions, collecting booking information, and routing requests intelligently. It is built with **Gradio** for the user interface, **OpenAI** for natural language understanding, and **n8n** for workflow automation.

---

## ✨ Features

- **Smart Intent Routing**
  - Automatically classifies patient messages into:
    - Greeting
    - FAQ
    - Appointment Booking
    - Medical Questions

- **FAQ Management**
  - Extracts keywords from the patient's message (e.g., *price*, *working hours*, *insurance*, *location*).
  - Sends the request to an **n8n Webhook**.
  - Searches a Google Sheets knowledge base and returns the most relevant answer.

- **Appointment Booking**
  - Collects the required booking information:
    - Full Name
    - Phone Number
    - Medical Specialty
    - Preferred Date & Time
  - Sends the booking data to **n8n**.
  - The workflow formats the date, stores the appointment in Google Sheets, and returns a confirmation.

- **Medical Safety**
  - Detects medical consultation requests.
  - Politely refuses to provide medical diagnoses or treatment recommendations and advises the patient to consult a doctor.

---

# ⚙️ Tech Stack

- Python
- Gradio
- OpenAI API
- n8n
- Google Sheets
- Python-dotenv

---

# 🔄 n8n Workflow

The chatbot communicates with **n8n** through a webhook.

The workflow is responsible for:

- Routing requests (FAQ or Booking)
- Searching FAQs in Google Sheets
- Filtering and aggregating relevant answers
- Checking doctor availability
- Formatting appointment dates
- Saving appointments into Google Sheets
- Returning the final response to the chatbot

## Workflow Overview

> Add your workflow image here.

```md
![n8n Workflow](images/workflow.png)
```

---

# 📂 Project Structure

```
.
├── app.py
├── requirements.txt
├── .env
├── prompts/
│   
└── README.md
```

---

# 🚀 Installation

Clone the repository

```bash
git clone <repository-url>
cd clinic-chatbot
```

Install the dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file and add:

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

Gradio will generate a local URL where you can start chatting with the assistant.

---

# 📋 Requirements

- Python 3.10+
- Gradio
- OpenAI
- python-dotenv
- n8n
- Google Sheets

---

# 📌 Notes

- FAQ data is stored in Google Sheets.
- Bookings are automatically recorded through n8n  in Google Sheets.
- Medical questions requiring diagnosis are intentionally declined for patient safety.