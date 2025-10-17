import faiss
import numpy as np
import os

from get_data import fetch_html, extract_text_from_html
from text_utils import chunk_text, get_embeddings

def save_faiss_index(index, file_path="faiss_index.idx"):
    """Persist the FAISS index to disk."""
    faiss.write_index(index, file_path)
    print(f"✅ FAISS index saved to {os.path.abspath(file_path)}")


def load_faiss_index(file_path="faiss_index.idx", dimension=384):
    """Load FAISS index from disk if it exists, otherwise create a new one."""
    if os.path.exists(file_path):
        index = faiss.read_index(file_path)
        print(f"✅ Loaded FAISS index from {os.path.abspath(file_path)}")
    else:
        index = faiss.IndexFlatL2(dimension)
        print("⚠️ No existing index found. Created a new one.")
    return index

def create_faiss_index(embeddings, ids=None, dimension=384):
    """
    Create a new FAISS index and add embeddings.

    Args:
        embeddings (np.ndarray): Array of shape (num_chunks, embedding_dim)
        ids (np.ndarray or List[int], optional): Array of integer IDs corresponding to embeddings.
        dimension (int): Dimension of embeddings (default=384 for MiniLM).

    Returns:
        faiss.IndexIDMap: FAISS index with added embeddings.
    """
    if embeddings is None or len(embeddings) == 0:
        raise ValueError("Embeddings array is empty.")

    # Create a flat L2 index
    index = faiss.IndexIDMap(faiss.IndexFlatL2(dimension))

    # If no IDs provided, use sequential integers
    if ids is None:
        ids = np.arange(len(embeddings))

    embeddings = np.array(embeddings).astype('float32')
    ids = np.array(ids).astype('int64')

    index.add_with_ids(embeddings, ids)

    save_faiss_index(index)
    return index


def add_embeddings_to_index(index, embeddings, ids):
    """
    Add new embeddings to an existing FAISS index.

    Args:
        index (faiss.IndexIDMap): Existing FAISS index.
        embeddings (np.ndarray or List[List[float]]): New embeddings to add.
        ids (List[int] or np.ndarray): Corresponding IDs for embeddings.

    Returns:
        None
    """
    embeddings = np.array(embeddings).astype('float32')
    ids = np.array(ids).astype('int64')
    index.add_with_ids(embeddings, ids)


def search_faiss_index(index, query_embedding, top_k=5):
    """
    Search the FAISS index for the closest embeddings.

    Args:
        index (faiss.IndexIDMap): FAISS index.
        query_embedding (np.ndarray or List[float]): Single embedding to search.
        top_k (int): Number of nearest neighbors to return.

    Returns:
        List[Tuple[int, float]]: List of (id, distance) of top_k closest embeddings.
    """
    query_embedding = np.array(query_embedding).astype('float32').reshape(1, -1)
    distances, indices = index.search(query_embedding, top_k)

    # Return as list of tuples (id, distance)
    results = [(int(idx), float(dist)) for idx, dist in zip(indices[0], distances[0])]
    return results

# Example usage
if __name__ == "__main__":
    # Dummy embeddings
    url = "https://medium.com/@explorer_shwetabh/deepfake-detection-part-2-understanding-lora-based-moe-adapter-architecture-813acbf9b345"
    html = fetch_html(url)
    if html:
        content = extract_text_from_html(html)
        # print(content)  # print first 500 characters

    chunks = chunk_text(content, chunk_size=1000, chunk_overlap=100)
    print(f"Number of chunks: {len(chunks)}")
    embeddings = get_embeddings(chunks)

    # embeddings = np.random.rand(10, 384).astype('float32')
    ids = np.arange(embeddings.shape[0])

    # Create index
    index = create_faiss_index(embeddings, ids)

    # Add new embeddings
    # new_embeddings = np.random.rand(3, 384).astype('float32')
    # new_ids = [10, 11, 12]
    # add_embeddings_to_index(index, new_embeddings, new_ids)

    query = 'some random text here'
    
    # Search
    query_embeddings = get_embeddings([query])
    results = search_faiss_index(index, query_embeddings, top_k=5)
    print(results)  # [(id, distance), ...]
    breakpoint()