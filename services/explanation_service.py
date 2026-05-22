import os
from dotenv import load_dotenv
from groq import Groq

# Safely load application environment parameters
load_dotenv()

# Initialize the centralized Groq engine using the Llama-3.1-8b-instant model
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

def generate_explanation(title: str, article_text: str) -> str:
    """
    Analyzes raw news content and extracts an ultra-short, highly accessible 
    summary detailing exactly what happened and its bottom-line impact.
    
    Args:
        title (str): The primary article headline.
        article_text (str): Pre-processed and cleaned plaintext content body.
        
    Returns:
        str: A clean, single-paragraph explanation restricted to 2-3 sentences.
    """
    if not article_text or article_text.strip() == "":
        return "No sufficient context available to compute a live operational summary."

    prompt = f"""You are an expert News Intelligence Analyst. 
Analyze the following headline and content, then provide an ultra-short, crisp summary.

Format your response strictly into a single paragraph containing exactly 2 to 3 concise sentences:
- Sentence 1: The core factual event (Exactly what happened).
- Sentence 2-3: The immediate bottom line (Why it matters or the direct takeaway).

CRITICAL RULES:
- Do NOT include any headings, side headings, markdown titles, or bullet points.
- Keep it incredibly brief so the user can quickly grasp the headline's core meaning in one glance.
- Do NOT use robotic text like "This news is testament to..." or "In a major development...".
- Max 3 sentences total.

News Title: {title}
Article Content: {article_text}
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.25,  # Low temperature ensures highly predictable, deterministic summaries
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI summary processing temporary intermission: {str(e)}"


def generate_deep_context(title: str, article_text: str) -> str:
    """
    Constructs a sophisticated, narrative background analysis exploring 
    the underlying trends, market implications, and upcoming roadblocks.
    
    Args:
        title (str): The primary article headline.
        article_text (str): Pre-processed and cleaned plaintext content body.
        
    Returns:
        str: A continuous narrative block structured into exactly 3 paragraphs.
    """
    if not article_text or article_text.strip() == "":
        return "No sufficient contextual baseline found to derive historical analytics."

    prompt = f"""You are an elite, versatile News Intelligence Analyst.
Provide a comprehensive background analysis of the news development provided below. 

Write exactly 3 distinct, analytical paragraphs exploring entirely different structural angles of the story:
- Paragraph 1 (The Foundation): What historical milestones, past decisions, or broader underlying industry/regional trends built the foundation for this news?
- Paragraph 2 (The Structural Impact): What are the concrete strategic, financial, operational, or industry-wide implications? How does this alter the current landscape?
- Paragraph 3 (The Road Ahead): What are the immediate next steps, execution risks, bottlenecks, or future competitive challenges the involved parties face?

CRITICAL RULES FOR LEGIBILITY:
- Do NOT use any headings, subheadings, labels, or bold side headings. 
- Do NOT number the paragraphs or use bullet points. 
- Do NOT mention the category, domain, or field of the news explicitly (e.g., do NOT say "In the field of sports..." or "Looking at the finance domain..."). Just naturally write about the subject matter using its appropriate professional vocabulary.
- Write as a completely continuous, smooth, professional narrative.

News Title: {title}
Article Content: {article_text}
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.45,  # Slightly higher temperature grants the narrative professional fluidity
            max_tokens=750
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Deep analytics pipeline compilation issue: {str(e)}"