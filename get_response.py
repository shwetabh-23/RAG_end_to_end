from get_closest_chunks import query_rag_pipeline
from prompts import generate_user_prompt, generate_llm_response, system_prompt
FAISS_FILE = "faiss_index.idx"

def get_response(query) : 
    rag_results = query_rag_pipeline(query, FAISS_FILE)

    user_prompt = generate_user_prompt(rag_results, query)
    response = generate_llm_response(system_prompt, user_prompt)

    return response

if __name__ == '__main__' : 

    query = 'what is a DaViT architecture?'
    FAISS_FILE = "faiss_index.idx"

    get_response(query)