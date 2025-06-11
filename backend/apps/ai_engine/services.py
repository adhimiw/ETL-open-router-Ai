"""
AI Engine services for OpenRouter integration and RAG implementation.
"""

import openai
# import chromadb
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from django.conf import settings
# from sentence_transformers import SentenceTransformer
import json
import time
import logging

# from .models import AIModel, EmbeddingModel, VectorStore, Conversation, Message

logger = logging.getLogger(__name__)


class OpenRouterService:
    """
    Service for interacting with OpenRouter API using DeepSeek Chat model.
    """
    
    def __init__(self):
        self.client = openai.OpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.model = settings.OPENROUTER_MODEL
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate chat completion using DeepSeek Chat model.
        """
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                extra_headers={
                    "HTTP-Referer": "https://eetl-ai-platform.com",
                    "X-Title": "EETL AI Platform",
                }
            )
            
            processing_time = time.time() - start_time
            
            if stream:
                return response
            
            result = {
                'content': response.choices[0].message.content,
                'tokens_used': response.usage.total_tokens,
                'processing_time': processing_time,
                'model': self.model,
                'finish_reason': response.choices[0].finish_reason
            }
            
            # Update model usage statistics (commented out for now)
            # try:
            #     ai_model = AIModel.objects.get(model_id=self.model)
            #     ai_model.increment_usage(response.usage.total_tokens)
            # except AIModel.DoesNotExist:
            #     logger.warning(f"AI model {self.model} not found in database")
            
            return result
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            raise Exception(f"AI service error: {str(e)}")
    
    def generate_sql_query(
        self,
        natural_language_query: str,
        table_schema: Dict[str, Any],
        sample_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate SQL query from natural language using AI.
        """
        schema_description = self._format_schema_for_ai(table_schema)
        sample_description = self._format_sample_data(sample_data) if sample_data else ""
        
        system_prompt = f"""
        You are an expert SQL query generator. Generate accurate SQL queries based on natural language requests.
        
        Table Schema:
        {schema_description}
        
        {sample_description}
        
        Rules:
        1. Generate only the SQL query, no explanations
        2. Use proper SQL syntax
        3. Handle edge cases and null values
        4. Use appropriate aggregations and filters
        5. Ensure the query is safe and doesn't modify data
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate SQL query for: {natural_language_query}"}
        ]
        
        response = self.chat_completion(messages, temperature=0.1)
        return response['content'].strip()
    
    def generate_python_code(
        self,
        natural_language_query: str,
        data_info: Dict[str, Any]
    ) -> str:
        """
        Generate Python code for data analysis.
        """
        system_prompt = f"""
        You are an expert Python data analyst. Generate Python code using pandas for data analysis tasks.
        
        Available data information:
        {json.dumps(data_info, indent=2)}
        
        Rules:
        1. Use pandas DataFrame operations
        2. Include proper error handling
        3. Generate clean, readable code
        4. Add comments for complex operations
        5. Return results in a structured format
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate Python code for: {natural_language_query}"}
        ]
        
        response = self.chat_completion(messages, temperature=0.1)
        return response['content'].strip()
    
    def analyze_data_quality(
        self,
        data_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze data quality and provide recommendations.
        """
        system_prompt = """
        You are a data quality expert. Analyze the provided data summary and identify quality issues.
        Provide specific recommendations for data cleaning and improvement.
        
        Return your analysis in JSON format with:
        - overall_score (0-100)
        - issues: list of issues with severity levels
        - recommendations: list of specific recommendations
        - summary: brief text summary
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze this data: {json.dumps(data_summary, indent=2)}"}
        ]
        
        response = self.chat_completion(messages, temperature=0.3)
        
        try:
            return json.loads(response['content'])
        except json.JSONDecodeError:
            return {
                "overall_score": 50,
                "issues": [],
                "recommendations": [],
                "summary": response['content']
            }
    
    def _format_schema_for_ai(self, schema: Dict[str, Any]) -> str:
        """Format table schema for AI consumption."""
        formatted = []
        for table_name, columns in schema.items():
            formatted.append(f"Table: {table_name}")
            for col in columns:
                formatted.append(f"  - {col['name']} ({col['type']}) - {col.get('description', '')}")
        return "\n".join(formatted)
    
    def _format_sample_data(self, sample_data: Dict[str, Any]) -> str:
        """Format sample data for AI consumption."""
        if not sample_data:
            return ""
        
        formatted = ["Sample Data:"]
        for table_name, rows in sample_data.items():
            formatted.append(f"Table: {table_name}")
            if rows:
                # Show first few rows
                for i, row in enumerate(rows[:3]):
                    formatted.append(f"  Row {i+1}: {row}")
        return "\n".join(formatted)


class EmbeddingService:
    """
    Service for generating embeddings for RAG implementation.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # self.model = SentenceTransformer(model_name)
        self.model_name = model_name
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        # Temporarily disabled - requires sentence-transformers
        raise NotImplementedError("Embedding service temporarily disabled")
    
    def generate_single_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        # Temporarily disabled - requires sentence-transformers
        raise NotImplementedError("Embedding service temporarily disabled")


class VectorStoreService:
    """
    Service for managing vector stores using ChromaDB.
    """

    def __init__(self):
        # Temporarily disabled - requires ChromaDB
        # self.client = chromadb.PersistentClient(
        #     path=settings.CHROMA_PERSIST_DIRECTORY
        # )
        # self.embedding_service = EmbeddingService()
        pass
    
    def create_collection(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]] = None,
        ids: List[str] = None
    ):
        """Create a new vector collection."""
        # Temporarily disabled - requires ChromaDB
        raise NotImplementedError("Vector store service temporarily disabled")
    
    def query_collection(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Query a vector collection."""
        # Temporarily disabled - requires ChromaDB
        raise NotImplementedError("Vector store service temporarily disabled")
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]] = None,
        ids: List[str] = None
    ):
        """Add documents to existing collection."""
        # Temporarily disabled - requires ChromaDB
        raise NotImplementedError("Vector store service temporarily disabled")


class RAGService:
    """
    Service for Retrieval-Augmented Generation.
    """
    
    def __init__(self):
        self.openrouter_service = OpenRouterService()
        # self.vector_service = VectorStoreService()
    
    def query_with_context(
        self,
        query: str,
        collection_name: str,
        conversation_history: List[Dict[str, str]] = None,
        n_context_docs: int = 3
    ) -> Dict[str, Any]:
        """
        Answer query using RAG with retrieved context.
        """
        # Temporarily disabled - requires ChromaDB
        raise NotImplementedError("RAG service temporarily disabled")
    
    def create_data_context(
        self,
        data_source_id: str,
        data_summary: Dict[str, Any],
        sample_data: pd.DataFrame = None
    ) -> str:
        """
        Create vector store collection for a data source.
        """
        # Temporarily disabled - requires ChromaDB
        raise NotImplementedError("RAG service temporarily disabled")
