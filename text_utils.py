from langchain.text_splitter import RecursiveCharacterTextSplitter
from get_data import fetch_html, extract_text_from_html
from sentence_transformers import SentenceTransformer

# Initialize the model once
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')


def chunk_text(text, chunk_size=500, chunk_overlap=50):
    """
    Split text into chunks using LangChain's RecursiveCharacterTextSplitter.

    Args:
        text (str): The input text to split.
        chunk_size (int): Maximum size of each chunk (in characters/tokens).
        chunk_overlap (int): Number of overlapping characters between chunks.

    Returns:
        List[str]: List of text chunks.
    """
    if not text:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )

    chunks = splitter.split_text(text)
    return chunks

def get_embeddings(chunks):
    """
    Convert a list of text chunks into embeddings using MiniLM.

    Args:
        chunks (List[str]): List of text chunks.

    Returns:
        List[List[float]]: List of embeddings corresponding to each chunk.
    """
    if not chunks:
        return []

    embeddings = embedding_model.encode(chunks, convert_to_numpy=True, show_progress_bar=True)
    return embeddings

# Example usage
if __name__ == "__main__":

    url = "https://medium.com/@explorer_shwetabh/deepfake-detection-part-2-understanding-lora-based-moe-adapter-architecture-813acbf9b345"
    html = fetch_html(url)
    if html:
        content = extract_text_from_html(html)
        # print(content)  # print first 500 characters

    chunks = chunk_text(content, chunk_size=1000, chunk_overlap=100)
    print(f"Number of chunks: {len(chunks)}")
    embeddings = get_embeddings(chunks)
    # print(chunks[:2])  # print first 2 chunks
    breakpoint()
