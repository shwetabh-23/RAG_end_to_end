from text_utils import get_embeddings
from faiss_utils import load_faiss_index, search_faiss_index
from data.data_utils import get_chunks_from_db

def query_rag_pipeline(query, FAISS_FILE, top_k=5, EMBED_DIM=384):
    """
    Inputs:
        conn: SQLite connection
        query: user query string
        FAISS_FILE: path to saved FAISS index
        top_k: number of closest vectors to retrieve
    Returns:
        List of dicts with chunk_index, text, snippet, distance
    """

    # 1. Embed query
    query_embedding = get_embeddings([query])

    # 2. Load FAISS index
    index = load_faiss_index(FAISS_FILE, dimension=EMBED_DIM)

    # 3. Search closest embeddings
    results = search_faiss_index(index, query_embedding, top_k=5)
    faiss_indices = [i[0] for i in results]

    relevant_chunks = get_chunks_from_db(faiss_indices)
    return relevant_chunks

if __name__ == '__main__' : 

    query = 'some random query'
    FAISS_FILE = "faiss_index.idx"
    query_rag_pipeline(query, FAISS_FILE)

    user_prompt = generate_user_prompt(rag_results, user_query)
    response = generate_llm_response(system_prompt, user_prompt)