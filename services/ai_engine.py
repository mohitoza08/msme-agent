# MSME Sahayak - AI Engine
# Core interaction with the Groq API: builds the message list for the
# LLM and returns the generated reply.

import os
import groq
from dotenv import load_dotenv

# Load the API key from the .env file (GROQ_API_KEY=...)
load_dotenv()


def make_client(api_key=None):
    """Create a Groq client.

    Uses the caller's API key when provided (BYOK); otherwise falls back
    to the GROQ_API_KEY stored in the server's .env file.
    """
    key = api_key or os.getenv("GROQ_API_KEY")
    return groq.Groq(api_key=key)

# System prompt that defines the assistant's identity, capabilities and
# tone for the language model.
SYSTEM_PROMPT = """Tum "MSME Sahayak" ho - Indian small businesses ke liye AI assistant.

Tum yeh kaam karte ho:
1. GST calculate karo, filing dates batao, GST ke basic sawaal jawab do
2. Government schemes batao jo MSME owners ke liye hain (loans, subsidies)

Tum Hinglish me baat karte ho - Hindi aur English ka mix.
Tone: Professional but friendly, jaise koi experienced dost baat kar raha ho.

Rules:
- Step-by-step jawab do, ek saath sab mat ugal do
- Government websites ka link share karo jab relevant ho
- GST rates yaad rakho: 0% (essentials), 5% (packaged food), 12% (clothing <1000), 18% (most services), 28% (luxury)
- Agar kuch nahi pata toh seedha bolo "iska exact jawab government website pe milega"
- Small business owners ko encourage karo - unka kaam mushkil hota hai
- Bahut lamba jawab mat do - short aur crisp rakho"""


def get_ai_response(user_message: str, context: str = "", api_key: str = None, language: str = "hinglish") -> str:
    """
    Sends the user's message to the Groq API and returns the reply.

    Parameters:
        user_message (str): The user's query or statement
        context (str, optional): Additional context to include (e.g. scheme
                                data or the current GST rates)
        api_key (str, optional): User-provided Groq API key (BYOK).
                                Falls back to the server key when omitted.
        language (str, optional): Response language - "hinglish" (default)
                                or "english".

    Returns:
        str: The assistant's reply
    """
    client = make_client(api_key)

    # Build the message list that will be sent to the API
    messages = [
        # Start with the system prompt, which defines the assistant's behaviour
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    # Lock the response language. This system message comes after the base
    # prompt so it takes precedence, and it is added for BOTH languages so
    # the reply is always exclusively in the selected language.
    if language == "english":
        messages.append({
            "role": "system",
            "content": "LANGUAGE LOCK: Tum sirf aur sirf ENGLISH me reply doge. Bilkul Hindi ya Hinglish nahi - ek bhi Hindi word nahi. Clear, simple English me jawaab do."
        })
    else:
        messages.append({
            "role": "system",
            "content": "LANGUAGE LOCK: Tum sirf aur sirf HINGLISH me reply doge - Hindi aur English ka mix, jaise aam bharatiya bolte hain. Pure English me bilkul nahi likhna."
        })

    # Attach any extra context (e.g. scheme data) as a system message so the
    # model can ground its answer in the latest information
    if context:
        messages.append({
            "role": "system",
            "content": f"Extra info for this query:\n{context}"
        })

    # Append the user's message
    messages.append({"role": "user", "content": user_message})

    try:
        # Call the Groq API
        # qwen/qwen3.8-27b provides multilingual (Hinglish) responses on Groq.
        # Note: the earlier llama-3.3-70b-versatile endpoint has been retired.
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="qwen/qwen3.8-27b",
            temperature=0.7,    # 0 = deterministic, 1 = creative; 0.7 is a balanced middle ground
            max_tokens=2048,    # Maximum response length
            top_p=1,
            stream=False,       # Return the complete response at once
        )

        # Extract the reply text and return it
        return chat_completion.choices[0].message.content

    except groq.APIConnectionError:
        return "Sorry bhai, internet connection issue hai. Check karo API key sahi hai ya nahi."
    except groq.RateLimitError:
        return "Bahut saare requests ho gaye ek minute me. Thoda wait karo (1 min) phir try karo."
    except Exception as e:
        return f"Kuch gadbad ho gayi: {str(e)}"
