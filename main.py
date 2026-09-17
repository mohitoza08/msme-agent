# MSME Sahayak - Main Application
# FastAPI application entry point. All routes are defined in a single module
# to keep the implementation simple and easy to maintain.

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import os

# Import service modules
from services.ai_engine import get_ai_response
from services.gst_helper import calculate_gst, calculate_gst_exclusive, get_filing_dates, get_rate_for_item, get_all_slabs
from services.scheme_finder import find_schemes, get_all_schemes_summary, format_schemes_for_ai

# FastAPI application instance serving both the frontend and the backend
app = FastAPI(
    title="MSME Sahayak",
    description="AI-powered assistant for Indian small businesses",
    version="1.0"
)

# Serve static assets (CSS, JS, images) and HTML templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ==========================================
# Request/Response Models (Pydantic)
# Validates incoming payloads and rejects malformed requests
# ==========================================

class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""
    message: str  # User message
    context: Optional[str] = ""  # Optional pre-supplied context
    language: str = "hinglish"  # Response language: "hinglish" or "english"
    api_key: Optional[str] = None  # Bring Your Own Key: user-provided Groq key

class GSTCalcRequest(BaseModel):
    """Request model for GST calculations."""
    amount: float
    rate: float
    mode: str = "inclusive"  # "inclusive" or "exclusive"

class SchemeMatchRequest(BaseModel):
    """Request model for scheme matching."""
    investment: float = 0
    category: str = "general"
    business_type: str = "manufacturing"
    age: int = 25


# ==========================================
# Application Routes - endpoints consumed by the frontend
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the chat interface home page."""
    return templates.TemplateResponse(request, "index.html")


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint - forwards the user's message to the AI
    and returns the assistant's reply.
    """
    # Inject GST-specific context when the query mentions GST topics
    context = request.context or ""

    # Detect GST-related keywords in the user's message
    gst_keywords = ["gst", "tax", "filing", "return", "cgst", "sgst", "igst"]
    if any(keyword in request.message.lower() for keyword in gst_keywords):
        # Provide the latest GST slab and filing data as context
        slabs = get_all_slabs()
        filing = get_filing_dates()
        context += f"\n\nGST Slabs: {slabs}\nFiling Dates: {filing}"

    # Detect scheme-related keywords in the user's message
    scheme_keywords = ["scheme", "loan", "subsidy", "udyam", "mudra", "pmegp", "government"]
    if any(keyword in request.message.lower() for keyword in scheme_keywords):
        schemes = get_all_schemes_summary()
        context += f"\n\nAvailable MSME Schemes: {schemes}"

    # Generate the reply, using the user's own key when provided (BYOK)
    reply = get_ai_response(request.message, context, api_key=request.api_key, language=request.language)

    return {"reply": reply}


@app.post("/api/gst/calculate")
async def gst_calculate(request: GSTCalcRequest):
    """GST calculation endpoint."""
    if request.mode == "inclusive":
        result = calculate_gst(request.amount, request.rate)
    else:
        result = calculate_gst_exclusive(request.amount, request.rate)

    return result


@app.get("/api/gst/filing-dates")
async def gst_filing_dates():
    """Return the GST filing deadlines and penalties."""
    return get_filing_dates()


@app.get("/api/gst/rates")
async def gst_rates():
    """Return the full list of GST rate slabs."""
    return get_all_slabs()


@app.get("/api/gst/item-rate")
async def gst_item_rate(item: str):
    """Return the GST rate for a given item."""
    return get_rate_for_item(item)


@app.post("/api/schemes/find")
async def schemes_find(request: SchemeMatchRequest):
    """Find MSME schemes matching the user's profile."""
    schemes = find_schemes(
        investment=request.investment,
        category=request.category,
        business_type=request.business_type,
        age=request.age
    )

    # Build a formatted summary of the matched schemes for AI context
    formatted = format_schemes_for_ai(schemes)
    return {"schemes": schemes, "formatted": formatted}


@app.get("/api/schemes/all")
async def schemes_all():
    """Return a summary of all available MSME schemes."""
    return get_all_schemes_summary()


# ==========================================
# Run the app
# ==========================================

if __name__ == "__main__":
    import uvicorn
    # Host 0.0.0.0 exposes the app on the network (e.g. for testing from a phone)
    # Port 8000 is the default dev port
    # Reload enables automatic restarts on code changes
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
