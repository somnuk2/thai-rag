#!/usr/bin/env python3
"""
Unified Easy Local RAG Chat Application
Supports both Local (JSON) and Supabase (Remote) modes

Usage:
    python localrag_dual.py                    # Uses RAG_MODE from .env
    python localrag_dual.py --mode local       # Force local mode
    python localrag_dual.py --mode supabase    # Force supabase mode
    python localrag_dual.py --model mistral    # Use different model
"""

import torch
import ollama
import os
from openai import OpenAI
import argparse
import json
import hashlib
import sys
from pathlib import Path

from config import Config
from vector_store_factory import create_vector_store
from vector_store_base import VectorStore

# ANSI escape codes for colors
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'


def get_file_hash(filepath):
    """Compute MD5 hash of a file"""
    if not os.path.exists(filepath):
        return None
    with open(filepath, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def rewrite_query(user_input_json, conversation_history, ollama_model, client):
    """Rewrite query using LLM with conversation history"""
    user_input = json.loads(user_input_json)["Query"]
    context = "\n".join([f"{msg['role']}: {msg['content'][:100]}" for msg in conversation_history[-2:]])
    
    prompt = f"""Rewrite the following query by incorporating relevant context from the conversation history.
    The rewritten query should:
    - Preserve the core intent and meaning of the original query
    - Expand and clarify the query to make it more specific and informative for retrieving relevant context
    - Avoid introducing new topics or queries that deviate from the original query
    - DONT EVER ANSWER the Original query, but instead focus on rephrasing and expanding it into a new query
    
    Return ONLY the rewritten query text, without any additional formatting or explanations.
    
    Conversation History:
    {context}
    
    Original query: [{user_input}]
    
    Rewritten query: 
    """
    response = client.chat.completions.create(
        model=ollama_model,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=200,
        n=1,
        temperature=0.1,
    )
    rewritten_query = response.choices[0].message.content.strip()
    return json.dumps({"Rewritten Query": rewritten_query})


def ollama_chat(user_input, system_message, vector_store, ollama_model, conversation_history, client):
    """Main chat function using vector store"""
    conversation_history.append({"role": "user", "content": user_input})
    
    # Rewrite query if we have history
    if len(conversation_history) > 1:
        query_json = {"Query": user_input, "Rewritten Query": ""}
        rewritten_query_json = rewrite_query(json.dumps(query_json), conversation_history, ollama_model, client)
        rewritten_query_data = json.loads(rewritten_query_json)
        rewritten_query = rewritten_query_data["Rewritten Query"]
        print(PINK + "Original Query: " + user_input + RESET_COLOR)
        print(PINK + "Rewritten Query: " + rewritten_query + RESET_COLOR)
    else:
        rewritten_query = user_input
    
    # Get query embedding and search
    input_embedding = ollama.embeddings(
        model=Config.OLLAMA_EMBED_MODEL,
        prompt=rewritten_query
    )["embedding"]
    
    relevant_results = vector_store.search(input_embedding, top_k=Config.TOP_K)
    
    if relevant_results:
        context_str = "\n".join([r.get('content', r.get('text', '')) for r in relevant_results])
        print("Context Pulled from Documents: \n\n" + CYAN + context_str + RESET_COLOR)
    else:
        print(CYAN + "No relevant context found." + RESET_COLOR)
        context_str = ""
    
    # Prepare user input with context
    user_input_with_context = user_input
    if context_str:
        user_input_with_context = user_input + "\n\nRelevant Context:\n" + context_str
    
    conversation_history[-1]["content"] = user_input_with_context
    
    # Generate response
    messages = [{"role": "system", "content": system_message}, *conversation_history]
    
    response = client.chat.completions.create(
        model=ollama_model,
        messages=messages,
        max_tokens=2000,
    )
    
    conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
    return response.choices[0].message.content


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Easy Local RAG - Unified Chat")
    parser.add_argument(
        "--model",
        default=None,
        help="Chat model to use (default from config)"
    )
    parser.add_argument(
        "--mode",
        choices=["local", "supabase"],
        default=None,
        help="Storage mode: local (JSON) or supabase (remote)"
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear local cache and regenerate (local mode only)"
    )
    args = parser.parse_args()
    
    # Override mode if specified
    if args.mode:
        import os
        os.environ["RAG_MODE"] = args.mode
        # Need to reload config
        from importlib import reload
        import config
        reload(config)
        Config.validate()
    
    # Get model
    ollama_model = args.model or Config.OLLAMA_CHAT_MODEL
    
    # Print configuration
    Config.print_config()
    
    # Initialize OpenAI client for Ollama
    client = OpenAI(base_url=Config.OLLAMA_BASE_URL, api_key=Config.OLLAMA_API_KEY)
    
    # Create vector store
    try:
        vector_store = create_vector_store()
    except Exception as e:
        print(f"{PINK}❌ Error initializing vector store: {e}{RESET_COLOR}")
        sys.exit(1)
    
    # Health check
    if not vector_store.health_check():
        print(f"{PINK}❌ Vector store is not accessible{RESET_COLOR}")
        sys.exit(1)
    
    # Initialize conversation
    conversation_history = []
    system_message = "You are a helpful assistant that is an expert at extracting the most useful information from a given text. Also bring in extra relevant information to the user query from outside the given context."
    
    print(NEON_GREEN + f"Ready! (Mode: {Config.MODE}, Model: {ollama_model})" + RESET_COLOR)
    
    # Main loop
    while True:
        try:
            user_input = input(YELLOW + "Ask a query about your documents (or type 'quit' to exit): " + RESET_COLOR)
            
            if user_input.lower() == 'quit':
                print(NEON_GREEN + "Goodbye!" + RESET_COLOR)
                break
            
            if not user_input.strip():
                continue
            
            response = ollama_chat(
                user_input,
                system_message,
                vector_store,
                ollama_model,
                conversation_history,
                client
            )
            print(NEON_GREEN + "Response: \n\n" + response + RESET_COLOR)
        
        except KeyboardInterrupt:
            print(NEON_GREEN + "\nGoodbye!" + RESET_COLOR)
            break
        except Exception as e:
            print(f"{PINK}❌ Error: {e}{RESET_COLOR}")
            continue


if __name__ == "__main__":
    main()
