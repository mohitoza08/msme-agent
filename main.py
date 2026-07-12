# MSME Sahayak - Main Application
# Ye file FastAPI app hai - sab routes ek jagah
# Simple rakhna hai - ek file me sab samajh aata hai

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import os

# Services import karo
from services.ai_engine import get_ai_response
from services.gst_helper import calculate_gst, calculate_gst_exclusive, get_filing_dates, get_rate_for_item, get_all_slabs
from services.scheme_finder import find_schemes, get_all_schemes_summary, format_schemes_for_ai

# FastAPI app banao
# Ye web server hai jo frontend aur backend dono handle karega
app = FastAPI(
    title="MSME Sahayak",
    description="AI-powered assistant for Indian small businesses",
    version="1.0"
)

# Static files aur templates setup karo
# Static = CSS, JS, images
# Templates = HTML files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ==========================================
# Request/Response Models (Pydantic)
# Ye data validate karta hai - galat data aaye toh error dega
# ==========================================

class ChatRequest(BaseModel):
    """Chat ke liye request model"""
    message: str  # User ne kya bola
    context: Optional[str] = ""  # Agar extra info ho toh

class GSTCalcRequest(BaseModel):
    """GST calculate karne ke liye"""
    amount: float
    rate: float
    mode: str = "inclusive"  # "inclusive" ya "exclusive"

class SchemeMatchRequest(BaseModel):
    """Scheme match karne ke liye"""
    investment: float = 0
    category: str = "general"
    business_type: str = "manufacturing"
    age: int = 25


# ==========================================
# Routes - Ye URLs hai jo frontend call karega
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page - chat interface dikhega"""
    return templates.TemplateResponse(request, "index.html")


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint - user ka message AI ko bhejta hai
    Aur AI ka jawab return karta hai
    """
    # Agar user GST ke baare me puch raha hai, toh extra context do
    context = request.context or ""

    # GST related keywords check karo
    gst_keywords = ["gst", "tax", "filing", "return", "cgst", "sgst", "igst"]
    if any(keyword in request.message.lower() for keyword in gst_keywords):
        # GST ka latest data context me daal do
        slabs = get_all_slabs()
        filing = get_filing_dates()
        context += f"\n\nGST Slabs: {slabs}\nFiling Dates: {filing}"

    # Scheme related keywords check karo
    scheme_keywords = ["scheme", "loan", "subsidy", "udyam", "mudra", "pmegp", "government"]
    if any(keyword in request.message.lower() for keyword in scheme_keywords):
        schemes = get_all_schemes_summary()
        context += f"\n\nAvailable MSME Schemes: {schemes}"

    # AI se jawab lo
    reply = get_ai_response(request.message, context)

    return {"reply": reply}


@app.post("/api/gst/calculate")
async def gst_calculate(request: GSTCalcRequest):
    """GST calculation endpoint"""
    if request.mode == "inclusive":
        result = calculate_gst(request.amount, request.rate)
    else:
        result = calculate_gst_exclusive(request.amount, request.rate)

    return result


@app.get("/api/gst/filing-dates")
async def gst_filing_dates():
    """GST filing dates return karo"""
    return get_filing_dates()


@app.get("/api/gst/rates")
async def gst_rates():
    """Saare GST rates return karo"""
    return get_all_slabs()


@app.get("/api/gst/item-rate")
async def gst_item_rate(item: str):
    """Item ka GST rate dhundho"""
    return get_rate_for_item(item)


@app.post("/api/schemes/find")
async def schemes_find(request: SchemeMatchRequest):
    """User ki profile ke basis pe schemes dhundho"""
    schemes = find_schemes(
        investment=request.investment,
        category=request.category,
        business_type=request.business_type,
        age=request.age
    )

    # Scheme details ke saath formatted output
    formatted = format_schemes_for_ai(schemes)
    return {"schemes": schemes, "formatted": formatted}


@app.get("/api/schemes/all")
async def schemes_all():
    """Saare schemes ka summary"""
    return get_all_schemes_summary()


# ==========================================
# Run the app
# ==========================================

if __name__ == "__main__":
    import uvicorn
    # Host: 0.0.0.0 = network pe bhi accessible hoga (phone se test karne ke liye)
    # Port: 8000 = standard port
    # Reload: True = code change karo toh automatically restart hoga
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
