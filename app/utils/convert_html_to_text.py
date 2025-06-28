from bs4 import BeautifulSoup

def html_to_text(html_content: str) -> str:
    """
    Converts HTML content to plain text.
    
    Args:
        html_content (str): The HTML content of an email.

    Returns:
        str: Cleaned plain text version of the email.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script and style elements
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Get text and strip leading/trailing whitespace
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)
