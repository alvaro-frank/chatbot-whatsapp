# Chatbot WhatsApp

A production-grade Virtual Assistant project that automates customer service requests via WhatsApp. It implements **LLM-based Intent Recognition** using **Groq (Llama 3)** within a Flask architecture, complete with a React dashboard for "Human-in-the-Loop" validation and specific simulation commands.

This project demonstrates a complete automated flow: from receiving messages via the **WhatsApp Business API**, analyzing content with Generative AI, to managing requests via a dedicated **Frontend** and deploying via **Docker**.

## 📂 Project Structure
```
├── src/
│   ├── app/
│   │   ├── commands/        # Simulation Logic (Command Pattern)
│   │   ├── controllers/     # Webhook & API Endpoints
│   │   ├── services/        # AI, WhatsApp & Request Services
│   │   ├── models.py        # Database Schema (SQLAlchemy)
│   │   └── run.py           # Application Entrypoint
│   ├── frontend/            # React + TypeScript Dashboard
│   │   ├── src/
│   │   │   ├── components/  # UI Components (RequestCard)
│   │   │   └── hooks/       # State Management hooks
│   │   └── vite.config.ts   # Frontend Build Config
├── tests/                   # Unit and Integration tests
├── docker-compose.yml       # Docker services configuration
├── Dockerfile               # Backend Image definition
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

## 🛠️ Setup & Requirements

This project uses `docker-compose` for orchestration and `npm` for the frontend build.

1. **Clone the repository**
```
git clone https://github.com/alvaro-frank/chatbot-whatsapp.git
cd chatbot-whatsapp
```

2. **Environment Variables**: Create a `.env` file in the root directory based on the requirements.
```
ACCESS_TOKEN=your_meta_access_token
GROQ_API_KEY=your_groq_api_key
PHONE_NUMBER_ID=your_phone_id
VERIFY_TOKEN=your_custom_webhook_token
...
```

## ⚡ Quick Start
To run the **full end-to-end stack** (Backend API + Frontend Dashboard + Database) in one go:
```
docker-compose up --build
```

Access the Dashboard at `http://localhost:8001` and the API at `http://localhost:8000`.

## 🏃 Usage

You can run individual components or specific tasks.

1. **Running the Bot**

Start the Flask backend which handles the Webhook and AI processing.
```
pip install -r requirements.txt
python run.py
```

The server will listen on port `8000` for incoming webhook events from Meta.

2. **Dashboard Interface**

Launch the React Dashboard to view and moderate incoming requests (Human-in-the-Loop).
```
cd frontend
npm install
npm run dev
```

You can interact with the requests:

| Action | Purpose |
|------------|-------------------------------------------|
| Approve | Confirms the AI-generated response and sends it to the user via WhatsApp. |
| Reject | Cancels the request and notifies the user. |
| Edit | Modify the AI draft before sending. |
| Simulate | View the backend simulation result (JSON) for the request (Flip Card). |

3. **Testing**

Ensure the AI logic, parsers, and service integration are valid.
```
# Run all unit tests
pytest

# Run specific service tests
pytest tests/unit/test_ai_service.py
```

## 🧠 Methodology

**AI & Intent Recognition**

The system uses a structured prompt engineering approach to process natural language:

1. **Language Detection**: Identifies the user's language (PT, EN, ES) to maintain conversation context.
2. **Intent Classification**: Categorizes input into business intents (e.g., `alterar_nif`, `alterar_morada`).
3. **Entity Extraction**: Isolates specific values (tax number, addresses) from the unstructured text.

**Human-in-the-loop Architecture**

To ensure safety and accuracy in a CRM context, the bot does not reply instantly. Instead, it follows a rigorous flow:

1. **Reception**: Message is received and saved as `PENDING`.
2. **Drafting**: The AI generates a `response_draft` and simulates the business operation (Command Pattern).
3. **Validation**: An agent reviews the request on the Dashboard.
4. **Execution**: Upon approval or rejection, the `WhatsAppService` delivers the final message.

## 🐳 Docker Support

This project is fully containerized to facilitate deployment and isolation.

**Prequisites**
- `Docker` and `Docker Compose` installed.

**How to Run**

1. **Build and Start Services**: The command below builds both the Flask backend and the React frontend.
```
docker-compose up --build
```

2. **Backend Logs**: To monitor the AI processing and Webhook events.
```
docker-compose logs -f chatbot
```

3. **Frontend Logs**: To monitor the Dashboard requests.
```
docker-compose logs -f chatbot-frontend
```

4. **Interactive Shell**: To access the database or run scripts inside the container.
```
docker-compose exec chatbot bash
```

## 🔌 API Usage

This section details the JSON payloads exchanged between the four main components of the system: **Meta (WhatsApp)**, **Backend (Flask)**, and **Dashboard (React)**.

1. **Meta Webhook -> Backend (Incoming messages)**

When a user sends a message, Meta sends a POST request to the `/webhook` endpoint. The system parses this nested structure into an internal DTO.

**Endpoint** `POST /webhook` **Payload**:
```
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "1092837465",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "1555029384",
              "phone_number_id": "1029384756"
            },
            "contacts": [
              {
                "profile": { "name": "João Silva" },
                "wa_id": "351912345678"
              }
            ],
            "messages": [
              {
                "from": "351912345678",
                "id": "wamid.HBgLM...",
                "timestamp": "1678889999",
                "type": "text",
                "text": { "body": "I would like to change my tax number to 266414563" }
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

2. **Backend -> Dashboard**

The Dashboard polls the API to show pending requests that need human validation ("Human-in-the-Loop").

**Endpoint** `GET /admin/requests/?status=PENDING` **Response**:
```
[
  {
    "id": 42,
    "wa_id": "351912345678",
    "sender_name": "João Silva",
    "message_body": "I would like to change my tax number to 266414563",
    "received_at": "2023-10-27T14:30:00Z",
    "status": "PENDING",
    "ai_analysis": {
      "intent": "alterar_nif",
      "extracted_entities": { "nif": "266414563" },
      "confidence": 0.98
    },
    "response_draft": "I confirm the change of the Tax Identification Number to 266414563."
  }
]
```

3. **Dashboard -> Backend**

The human agent can edit the response and when clicks "Approve", the Dashboard sends the final text to be sent to the user.

**Endpoint** `POST /admin/requests/{id}/approve` **Payload**:
```
{
  "response_text": "Hello Peter, I confirm the change of the Tax Identification Number to 266414563."
}
```

4. **Backend -> Meta API (Outgoing messages)**

Finally, the `WhatsAppService` executes the API call to Meta to deliver the approved message to the user's phone.

**Target** `https://graph.facebook.com/v24.0/{phone_number_id}/messages` **Payload**:
```
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "351912345678",
  "type": "text",
  "text": {
    "preview_url": false,
    "body": "Hello Peter, I confirm the change of the Tax Identification Number to 266414563."
  }
}
```
