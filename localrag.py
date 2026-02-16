import torch
import ollama
import os
from openai import OpenAI
import argparse
import json
import hashlib

# ANSI escape codes for colors
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

# Function to compute MD5 hash of a file
def get_file_hash(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()

# Function to get relevant context from the vault based on user input
def get_relevant_context(rewritten_input, vault_embeddings, vault_content, top_k=3):
    if vault_embeddings.nelement() == 0:
        return []
    input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"]
    cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
    top_k = min(top_k, len(cos_scores))
    top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
    relevant_context = [vault_content[idx].strip() for idx in top_indices]
    return relevant_context

def rewrite_query(user_input_json, conversation_history, ollama_model, client):
    user_input = json.loads(user_input_json)["Query"]
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-2:]])
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
   
def ollama_chat(user_input, system_message, vault_embeddings, vault_content, ollama_model, conversation_history, client):
    conversation_history.append({"role": "user", "content": user_input})
    
    if len(conversation_history) > 1:
        query_json = {"Query": user_input, "Rewritten Query": ""}
        rewritten_query_json = rewrite_query(json.dumps(query_json), conversation_history, ollama_model, client)
        rewritten_query_data = json.loads(rewritten_query_json)
        rewritten_query = rewritten_query_data["Rewritten Query"]
        print(PINK + "Original Query: " + user_input + RESET_COLOR)
        print(PINK + "Rewritten Query: " + rewritten_query + RESET_COLOR)
    else:
        rewritten_query = user_input
    
    relevant_context = get_relevant_context(rewritten_query, vault_embeddings, vault_content)
    if relevant_context:
        context_str = "\n".join(relevant_context)
        print("Context Pulled from Documents: \n\n" + CYAN + context_str + RESET_COLOR)
    else:
        print(CYAN + "No relevant context found." + RESET_COLOR)
    
    user_input_with_context = user_input
    if relevant_context:
        user_input_with_context = user_input + "\n\nRelevant Context:\n" + context_str
    
    conversation_history[-1]["content"] = user_input_with_context
    
    messages = [{"role": "system", "content": system_message}, *conversation_history]
    
    response = client.chat.completions.create(
        model=ollama_model,
        messages=messages,
        max_tokens=2000,
    )
    
    conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
    return response.choices[0].message.content

def main():
    parser = argparse.ArgumentParser(description="Ollama Chat with Embedding Cache")
    parser.add_argument("--model", default="llama3", help="Ollama model to use (default: llama3)")
    parser.add_argument("--clear-cache", action="store_true", help="Clear the embeddings cache and regenerate")
    args = parser.parse_args()

    client = OpenAI(base_url='http://localhost:11434/v1', api_key='llama3')

    vault_path = "vault.txt"
    cache_path = "vault_embeddings_cache.json"
    
    print(NEON_GREEN + "Loading vault content..." + RESET_COLOR)
    vault_content = []
    if os.path.exists(vault_path):
        with open(vault_path, "r", encoding='utf-8') as vault_file:
            vault_content = vault_file.readlines()
    
    vault_hash = get_file_hash(vault_path)
    vault_embeddings = []
    
    # Check if cache exists and is valid
    use_cache = False
    if not args.clear_cache and os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
            if cache_data.get("hash") == vault_hash:
                print(NEON_GREEN + "Loading embeddings from cache..." + RESET_COLOR)
                vault_embeddings = cache_data.get("embeddings", [])
                use_cache = True
    
    if not use_cache:
        print(NEON_GREEN + "Generating new embeddings for the vault content..." + RESET_COLOR)
        for content in vault_content:
            response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
            vault_embeddings.append(response["embedding"])
        
        # Save to cache
        print(NEON_GREEN + "Saving embeddings to cache..." + RESET_COLOR)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"hash": vault_hash, "embeddings": vault_embeddings}, f)

    vault_embeddings_tensor = torch.tensor(vault_embeddings)
    
    conversation_history = []
    system_message = "You are a helpful assistant that is an expert at extracting the most useful information from a given text. Also bring in extra relevant infromation to the user query from outside the given context."

    print(NEON_GREEN + "Ready! (Using model: " + args.model + ")" + RESET_COLOR)

    while True:
        user_input = input(YELLOW + "Ask a query about your documents (or type 'quit' to exit): " + RESET_COLOR)
        if user_input.lower() == 'quit':
            break
        
        response = ollama_chat(user_input, system_message, vault_embeddings_tensor, vault_content, args.model, conversation_history, client)
        print(NEON_GREEN + "Response: \n\n" + response + RESET_COLOR)

if __name__ == "__main__":
    main()
