import requests
from bs4 import BeautifulSoup

def fetch_html(url, timeout=10):
    """
    Fetch the HTML content of a URL.

    Args:
        url (str): The URL to fetch.
        timeout (int): Request timeout in seconds.

    Returns:
        str: Raw HTML content of the page.

    Raises:
        requests.RequestException: If the request fails.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raise error for bad status codes
        return response.text
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch URL {url}: {e}")
        return None

def extract_text_from_html(html):
    """
    Extract clean text content from HTML using BeautifulSoup.

    Args:
        html (str): Raw HTML content.

    Returns:
        str: Cleaned, readable text.
    """
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted tags
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "iframe"]):
        tag.decompose()

    # Extract text from remaining HTML
    text = soup.get_text(separator=" ", strip=True)

    # Normalize spaces
    text = " ".join(text.split())

    return text

# Example usage
if __name__ == "__main__":
    url = "https://medium.com/@explorer_shwetabh/deepfake-detection-part-2-understanding-lora-based-moe-adapter-architecture-813acbf9b345"
    html = fetch_html(url)
    if html:
        content = extract_text_from_html(html)
        print(content)  # print first 500 characters
