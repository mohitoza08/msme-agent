# MSME Sahayak - AI Engine
# Ye file project ka main brain hai - Groq API se connect hota hai
# Groq ek free LLM provider hai jo Meta ka Llama model use karta hai

import os
import groq
from dotenv import load_dotenv

# .env file se API key load karo
# .env me likha hota hai: GROQ_API_KEY=tumhari_key
load_dotenv()

# Groq client banao - ye API se baat karega
client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

# Ye sabse important part hai - System Prompt
# Isme AI ko batata hai ki wo kaun hai aur kya karega
# Jaise hum kisi naye employee ko samjhate hain na, waise hi
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


def get_ai_response(user_message: str, context: str = "") -> str:
    """
    Ye function user ka message Groq API ko bhejta hai aur jawab laata hai.

    Parameters:
        user_message (str): Jo user ne bola
        context (str, optional): Agar koi extra info deni ho toh
                                (jaise scheme data ya GST rates)

    Returns:
        str: AI ka jawab
    """
    # Messages ka list banao - ye API ko jayega
    messages = [
        # Pehle system prompt daalo - ye AI ki personality set karta hai
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    # Agar context hai (jaise scheme data), toh system message me daal do
    # Isse AI ko extra info mil jaati hai jawab dene ke liye
    if context:
        messages.append({
            "role": "system",
            "content": f"Extra info for this query:\n{context}"
        })

    # User ka message daalo
    messages.append({"role": "user", "content": user_message})

    try:
        # Groq API ko call karo
        # llama-3.3-70b-versatile = Meta ka 70B parameter model
        # Ye fast hai (280 tokens/sec) aur smart bhi
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.7,    # 0 = boring/rigid, 1 = creative/random, 0.7 = balanced
            max_tokens=2048,    # Maximum characters in response
            top_p=1,
            stream=False,       # False = pura response ek saath, True = word by word
        )

        # Response me se sirf text nikal ke return karo
        return chat_completion.choices[0].message.content

    except groq.APIConnectionError:
        return "Sorry bhai, internet connection issue hai. Check karo API key sahi hai ya nahi."
    except groq.RateLimitError:
        return "Bahut saare requests ho gaye ek minute me. Thoda wait karo (1 min) phir try karo."
    except Exception as e:
        return f"Kuch gadbad ho gayi: {str(e)}"
