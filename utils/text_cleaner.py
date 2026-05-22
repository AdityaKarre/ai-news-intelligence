import re

def clean_article_text(text: str) -> str:
    """
    Sanitizes raw text content parsed from RSS descriptions or scraped web pages
    by stripping script blocks, style definitions, HTML tags, and redundant whitespace.
    
    Args:
        text (str): The raw text input.
        
    Returns:
        str: A clean, single-spaced plaintext string.
    """
    if not text:
        return ""
        
    # Remove background code blocks that mess with text parsing
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.DOTALL)
    
    # Strip any remaining standard HTML markup tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Convert all multi-spaces, tabs, and raw newlines into a uniform single space
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def filter_relevant_content(title: str, text: str, max_chars: int = 1200) -> str:
    """
    Ensures that the text block passed to the AI inference model remains highly 
    concentrated, relevant, and bounded to fit safely within token limits.
    
    Args:
        title (str): The main headline context.
        text (str): The underlying body paragraph context.
        max_chars (int): The safety cutoff envelope for character slices.
        
    Returns:
        str: The optimized string containing primary contextual details.
    """
    if not text or text.strip() == "":
        return title
        
    cleaned = clean_article_text(text)
    
    # Return a clean slice up to your target character threshold
    return cleaned[:max_chars]