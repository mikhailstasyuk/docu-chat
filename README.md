
# Docu-Chat RAG Microservice

This project is a self-contained microservice that allows you to upload a `.txt` document and ask questions about its content. It uses a Retrieval-Augmented Generation (RAG) architecture to ensure answers are grounded in the provided document.

The stack includes:
*   **FastAPI** for the web server
*   **Weaviate** as the vector database
*   **OpenAI API** for text embeddings and chat completion
*   **Docker** for containerization and easy setup

## Prerequisites

*   [Docker](https://www.docker.com/get-started) and Docker Compose
*   An OpenAI API Key

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd docu-chat
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file by copying the example file.
    ```bash
    cp .env.example .env
    ```
    Open the new `.env` file and add your OpenAI API key:
    ```
    OPENAI_API_KEY="sk-..."
    ```

## Running the Service

Build and run the application and the Weaviate database with a single command from the project's root directory:

```bash
docker compose build
docker compose up
```

The API will be available at `http://localhost:8000`.

## Usage

You can interact with the API using any HTTP client like `curl` or Postman.

### 1. Ingest a Document

First, upload a `.txt` file to the `/ingest` endpoint. This will process the document and store it for querying.

**Create a sample file `test.txt`:**```
The capital of France is Paris. Paris is known for the Eiffel Tower.
```

**Send the request:**
```bash
curl -X POST -F "file=@test.txt" http://localhost:8000/ingest
```

**Expected Success Response:**
```json
{
  "message": "Document ingested successfully.",
  "document_id": "some-unique-uuid",
  "chunks_stored": 1
}
```

### 2. Chat with the Document

Now, ask questions about the document using the `/chat` endpoint. Use a `session_id` to maintain conversation history.

#### Example 1: Question with an answer in the document

**Send the request:**
```bash
curl -X POST http://localhost:8000/chat \
-H "Content-Type: application/json" \
-d '{
    "session_id": "session-123",
    "question": "What is the capital of France?"
}'
```

**Expected Success Response:**
```json
{
  "session_id": "session-123",
  "answer": "The capital of France is Paris.",
  "retrieved_context": true
}
```

#### Example 2: Question without an answer in the document

This demonstrates the guardrail that prevents the model from using its general knowledge.

**Send the request:**
```bash
curl -X POST http://localhost:8000/chat \
-H "Content-Type: application/json" \
-d '{
    "session_id": "session-123",
    "question": "What is the capital of Germany?"
}'
```

**Expected Guardrail Response:**
```json
{
  "session_id": "session-123",
  "answer": "I do not have enough information to answer that.",
  "retrieved_context": true
}
```
*(Note: `retrieved_context` may still be `true` if the query vector was close to some text, but the LLM correctly followed its instructions to not answer.)*

## API Documentation

Once the service is running, interactive API documentation (provided by Swagger UI) is available at:

**[http://localhost:8000/docs](http://localhost:8000/docs)**

You can test all endpoints directly from your browser using this interface.

## Stopping the Service

To stop and remove the containers, press `Ctrl+C` in the terminal where `docker-compose` is running, and then run:

```bash
docker compose down
```