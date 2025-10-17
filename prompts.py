from phi3 import load_phi3, get_phi3_inference

model, tokenizer = load_phi3()

system_prompt = '''
You are an intelligent assistant designed to answer user questions using relevant context provided from a retrieval-augmented generation (RAG) system. 

You will receive multiple text chunks as reference material. Your task is to generate a coherent, factual, and concise answer to the user query based solely on these chunks. 

Do not hallucinate information. Only use the information present in the chunks. If the chunks do not contain the answer, indicate that the information is insufficient rather than guessing. 

Always cite the relevant chunks if needed and structure the answer in a readable, clear manner. Your goal is to provide the best possible answer to the user's question using the retrieved context.

'''

def generate_user_prompt(rag_results, user_query):
    """
    Generates a structured user prompt for an LLM using retrieved RAG chunks.

    Args:
        rag_results (List[Dict]): List of dicts containing retrieved chunks.
            Each dict must have a 'text' key with the chunk text.
        user_query (str): The original user query.

    Returns:
        str: A structured prompt ready to send to the LLM.
    """

    prompt_lines = [f"User Query:\n{user_query}\n", "Reference Material (Chunks):"]
    
    for i, chunk in enumerate(rag_results, start=1):
        text = chunk.get("text", "").strip()
        # Optional: truncate extremely long chunks if needed
        prompt_lines.append(f"Chunk {i}: {text}")
    
    prompt_lines.append("\nBased on the above chunks, provide a complete answer to the user query.")
    
    user_prompt = "\n".join(prompt_lines)
    return user_prompt

def generate_llm_response(system_prompt: str, user_prompt: str):
    """
    Generate a response from Phi-3 using a given system and user prompt.

    Args:
        system_prompt (str): The instruction prompt describing the model's role and behavior.
        user_prompt (str): The actual input or question to answer.

    Returns:
        str: The model's generated response.
    """
    # Prepare conversation history
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # Load model and tokenizer
    

    # Get inference
    response = get_phi3_inference(messages, model, tokenizer)

    # Optionally print for debug
    print("\n=== MODEL RESPONSE ===\n")
    print(response)
    print("\n======================\n")

    return response

if __name__ == '__main__' : 

    user_prompt = generate_user_prompt(rag_results, user_query)
    response = generate_llm_response(system_prompt, user_prompt)