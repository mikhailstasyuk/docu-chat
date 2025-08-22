import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv

load_dotenv()

from .schemas import IngestResponse, ChatRequest, ChatResponse, HealthResponse
from .services.document_processor import DocumentProcessor
from .services.weaviate_service import WeaviateService
from .services.rag_service import RAGService
from .services.chat_manager import ChatManager

# --- Service Instantiation (Singletons) ---
document_processor = DocumentProcessor()
weaviate_service = WeaviateService()
rag_service = RAGService(weaviate_service)
chat_manager = ChatManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's lifespan events.
    Connects to Weaviate on startup and closes the connection on shutdown.
    """
    print("Application startup: Connecting to Weaviate...")
    try:
        weaviate_service.connect()
        print("Successfully connected to Weaviate.")
    except Exception as e:
        # This will prevent the app from starting if connection fails
        raise RuntimeError(f"Failed to connect to Weaviate on startup: {e}")
    
    yield  # The application is now running
    
    print("Application shutdown: Closing Weaviate connection...")
    weaviate_service.close()
    print("Weaviate connection closed.")

# --- Application Setup ---
app = FastAPI(
    title="Docu-Chat RAG Microservice",
    description="An API for chatting with your text documents.",
    version="1.0.0",
    lifespan=lifespan  # Attach the lifespan manager
)

# --- API Endpoints ---

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return {"status": "ok"}

@app.post("/ingest", response_model=IngestResponse, tags=["Document Management"])
async def ingest_document(file: UploadFile = File(..., description="A .txt file to be processed.")):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .txt files are accepted.")
    try:
        contents = await file.read()
        text = contents.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {e}")
    document_id = str(uuid.uuid4())
    chunks = document_processor.chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="The document appears to be empty.")
    chunks_stored = await weaviate_service.store_chunks(document_id, chunks)
    return {
        "message": "Document ingested successfully.",
        "document_id": document_id,
        "chunks_stored": chunks_stored
    }

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_with_document(request: ChatRequest):
    history = chat_manager.get_history(request.session_id)
    answer, retrieved_context = await rag_service.get_answer(request.question, history)
    chat_manager.add_to_history(request.session_id, request.question, answer)
    return {
        "session_id": request.session_id,
        "answer": answer,
        "retrieved_context": retrieved_context
    }