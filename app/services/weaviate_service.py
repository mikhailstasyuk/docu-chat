import os
import weaviate
from weaviate.client import WeaviateClient, ConnectionParams
# --- FIX: Import Property and DataType directly ---
from weaviate.collections.classes.config import Configure, Property, DataType
from weaviate.util import generate_uuid5
from openai import AsyncOpenAI
from typing import List

# Constants
WEAVIATE_CLASS_NAME = "DocumentChunk"

class WeaviateService:
    """
    Service for interacting with the Weaviate vector database using the v4 client.
    """
    def __init__(self):
        """
        Initializes the Weaviate and OpenAI clients.
        """
        self.weaviate_client = WeaviateClient(
            connection_params=ConnectionParams.from_params(
                http_host="weaviate", http_port=8080, http_secure=False,
                grpc_host="weaviate", grpc_port=50051, grpc_secure=False,
            )
        )
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = "text-embedding-ada-002"

    # --- ADD connect() and close() methods for lifespan management ---
    def connect(self):
        """Connects to the Weaviate instance."""
        self.weaviate_client.connect()
        self._setup_schema() # Setup schema after connecting

    def close(self):
        """Closes the connection to the Weaviate instance."""
        self.weaviate_client.close()

    def _setup_schema(self):
        """
        Ensures the required collection exists in Weaviate.
        """
        collections = self.weaviate_client.collections.list_all()
        collection_names = [c.name for c in collections]

        if WEAVIATE_CLASS_NAME not in collection_names:
            self.weaviate_client.collections.create(
                name=WEAVIATE_CLASS_NAME,
                description="A chunk of text from an uploaded document.",
                vectorizer_config=Configure.Vectorizer.none(),
                # --- FIX: Use the imported Property and DataType classes ---
                properties=[
                    Property(name="text", data_type=DataType.TEXT),
                    Property(name="document_id", data_type=DataType.TEXT),
                ]
            )
            print(f"Collection '{WEAVIATE_CLASS_NAME}' created.")

    async def _get_embedding(self, text: str) -> List[float]:
        # ... (rest of the method is unchanged)
        response = await self.openai_client.embeddings.create(
            input=[text.replace("\n", " ")], model=self.embedding_model
        )
        return response.data[0].embedding

    async def store_chunks(self, document_id: str, chunks: List[str]) -> int:
        # ... (rest of the method is unchanged)
        collection = self.weaviate_client.collections.get(WEAVIATE_CLASS_NAME)
        objects_to_insert = []
        for chunk in chunks:
            embedding = await self._get_embedding(chunk)
            properties = {"text": chunk, "document_id": document_id}
            objects_to_insert.append(
                weaviate.collections.classes.data.DataObject(
                    properties=properties, vector=embedding, uuid=generate_uuid5(properties)
                )
            )
        with collection.batch.dynamic() as batch:
            for obj in objects_to_insert:
                batch.add_object(properties=obj.properties, vector=obj.vector, uuid=obj.uuid)
        return len(objects_to_insert)

    async def query_chunks(self, query: str, top_k: int = 3) -> List[str]:
        # ... (rest of the method is unchanged)
        query_embedding = await self._get_embedding(query)
        collection = self.weaviate_client.collections.get(WEAVIATE_CLASS_NAME)
        response = collection.query.near_vector(
            near_vector=query_embedding, limit=top_k, return_properties=["text"]
        )
        return [item.properties["text"] for item in response.objects]