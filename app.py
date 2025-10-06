from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import os
from datetime import datetime
from dotenv import load_dotenv
import subprocess
import tempfile
import re
import asyncio
import threading
from typing import Dict
from jose import JWTError, jwt
from sqlalchemy.orm import Session

# Load environment variables from .env file
load_dotenv()

from generate_prompt import InputSpec, build_prompt, call_openai_chat
from database.models import User, ProductTerm, Report, get_db, create_tables
from auth.auth import get_current_user, verify_token
from auth.auth_routes import router as auth_router

# App will be initialized later with lifespan

# Job status tracking for async report generation
job_status: Dict[str, Dict] = {}
job_lock = threading.Lock()

# These will be configured after app initialization

# Create database tables
create_tables()

# Add lifespan context manager for proper startup/shutdown handling
from contextlib import asynccontextmanager
import asyncio
import signal
import sys

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    try:
        create_tables()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    yield
    
    # Shutdown
    print("Application shutting down...")
    try:
        # Cancel any pending tasks
        tasks = [task for task in asyncio.all_tasks() if not task.done()]
        if tasks:
            print(f"Cancelling {len(tasks)} pending tasks...")
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        print(f"Error during shutdown: {e}")

# Initialize app with lifespan
app = FastAPI(
    title="AI Trade Report", 
    description="Professional AI-powered market analysis generator",
    lifespan=lifespan
)

# Configure request timeout
import asyncio
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # Set a 15-minute timeout for all requests
            return await asyncio.wait_for(call_next(request), timeout=900)
        except asyncio.TimeoutError:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=504,
                content={"status": "error", "message": "Request timeout. Please try again."}
            )

app.add_middleware(TimeoutMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include authentication routes
app.include_router(auth_router)

os.makedirs("reports", exist_ok=True)

# Security scheme
security = HTTPBearer(auto_error=False)

def generate_report_background(job_id: str, brand: str, product: str, budget: str, enterprise_size: str, other_info: str, ai_model: str, language: str, user_id: int):
    """Background task for report generation"""
    try:
        with job_lock:
            job_status[job_id] = {"status": "processing", "progress": 0}
        
        # Update progress
        with job_lock:
            job_status[job_id]["progress"] = 25
        
        # Build prompt
        spec = InputSpec(brand=brand.strip(), product=product.strip(), budget=budget.strip(), enterprise_size=enterprise_size.strip(), other_info=other_info.strip())
        prompt_text = build_prompt(spec, analysis_date=datetime.now().strftime("%d %B %Y"), language=language)
        
        # Update progress
        with job_lock:
            job_status[job_id]["progress"] = 50
        
        # Generate report text
        if ai_model != "none" and ai_model != "undefined":
            report_text = call_openai_chat(prompt_text, model=ai_model)
        else:
            if ai_model == "undefined":
                report_text = call_openai_chat(prompt_text, model="gpt-5")
            else:
                report_text = prompt_text
        
        # Ensure report_text is not None and not empty
        if report_text is None or report_text.strip() == "":
            report_text = f"""# AI Trade Report - {brand}

**Error:** Unable to generate report content. Please try again.

## Troubleshooting

If you continue to experience issues, please:
1. Check your internet connection
2. Verify your OpenAI API key is valid
3. Try again in a few minutes
4. Contact support if the problem persists

---
*Report generated on {datetime.now().strftime('%d %B %Y')}*"""
        
        # Update progress
        with job_lock:
            job_status[job_id]["progress"] = 75
        
        # Generate filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename_txt = f"reports/report_{user_id}_{timestamp}.txt"
        report_filename_pdf = f"report_{user_id}_{timestamp}"
        
        # Save text version
        with open(report_filename_txt, "w", encoding="utf-8") as f:
            f.write(report_text)
        
        # Create HTML version
        form_data = {
            'brand': brand,
            'product': product,
            'budget': budget,
            'enterprise_size': enterprise_size,
            'other_info': other_info
        }
        html_path = create_html_report(report_text, report_filename_pdf, language, form_data)
        actual_filename = f"{report_filename_pdf}.html"
        
        # Update job status to completed
        with job_lock:
            form_data_params = f"?brand={brand}&product={product}&budget={budget}&enterprise_size={enterprise_size}"
            job_status[job_id] = {
                "status": "completed",
                "progress": 100,
                "redirect_url": f"/report/{actual_filename}{form_data_params}",
                "report_name": actual_filename
            }
            
    except Exception as e:
        # Update job status to error
        with job_lock:
            job_status[job_id] = {
                "status": "error",
                "progress": 0,
                "error": str(e)
            }

def create_html_report(content: str, filename: str, language: str = "en", form_data: dict = None) -> str:
    """Create an HTML report from text content"""
    html_path = f"reports/{filename}.html"
    
    # Create HTML content
    html_content = create_html_document(content, language, form_data)
    
    # Write HTML file
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path

def create_html_document(content: str, language: str = "en", form_data: dict = None) -> str:
    """Convert text content to HTML format"""
    
    # Language-specific translations
    translations = {
        "en": {
            "title": "AI Trade Report - Professional Market Analysis",
            "report_title": "AI Trade Report",
            "report_overview": "Report Overview",
            "generated_by": "Generated by:",
            "ai_powered": "AI-Powered Market Research",
            "date": "Date:",
            "report_type": "Report Type:",
            "comprehensive_analysis": "Comprehensive Market Analysis",
            "footer_text1": "This report was generated using AI-powered market research technology.",
            "footer_text2": "For questions or additional analysis, please contact your research team.",
            "print": "Print",
            "download_pdf": "Download PDF",
            "save": "Save",
            "return_home": "Home",
            "saved_reports_title": "Your Saved Reports",
            "saved_reports_subtitle": "Access and manage your previously generated reports",
            "saved_reports_nav": "Saved Reports",
            "no_reports_title": "No Saved Reports Yet",
            "no_reports_description": "Generate your first report to see it saved here for easy access."
        },
        "it": {
            "title": "AI Trade Report - Analisi di Mercato Professionale",
            "report_title": "AI Trade Report",
            "report_overview": "Panoramica del Report",
            "generated_by": "Generato da:",
            "ai_powered": "Ricerca di Mercato basata su AI",
            "date": "Data:",
            "report_type": "Tipo di Report:",
            "comprehensive_analysis": "Analisi di Mercato Completa",
            "footer_text1": "Questo report è stato generato utilizzando tecnologia di ricerca di mercato basata su AI.",
            "footer_text2": "Per domande o analisi aggiuntive, contatta il tuo team di ricerca.",
            "print": "Stampa",
            "download_pdf": "Scarica PDF",
            "save": "Salva",
            "return_home": "Home",
            "saved_reports_title": "I Tuoi Report Salvati",
            "saved_reports_subtitle": "Accedi e gestisci i tuoi report generati in precedenza",
            "saved_reports_nav": "Report Salvati",
            "no_reports_title": "Nessun Report Salvato Ancora",
            "no_reports_description": "Genera il tuo primo report per vederlo salvato qui per un accesso facile."
        }
    }
    
    t = translations.get(language, translations["en"])
    
    # Escape HTML special characters
    def escape_html(text):
        special_chars = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;'
        }
        for char, replacement in special_chars.items():
            text = text.replace(char, replacement)
        return text
    
    # Start HTML document
    html = """<!DOCTYPE html>
<html lang=""" + language + """>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>""" + t['title'] + """</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <style>
        html, body {
            font-family: 'Times New Roman', serif;
            font-size: 12pt;
            line-height: 1.5;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            color: #333;
            width: 100%;
            min-width: 100%;
            box-sizing: border-box;
        }
        .container {
            width: 100vw;
            min-width: 100%;
            margin: 0;
            background: white;
            padding: 40px;
            border-radius: 0;
            box-shadow: none;
            box-sizing: border-box;
        }
        h1 {
            color: #2c3e50;
            font-weight: bold;
            font-size: 18pt;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        h2 {
            color: #34495e;
            font-weight: bold;
            font-size: 16pt;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
            margin-top: 30px;
            margin-bottom: 20px;
        }
        h3 {
            color: #2c3e50;
            font-weight: bold;
            font-size: 14pt;
            margin-top: 25px;
            margin-bottom: 15px;
        }
        h4 {
            color: #7f8c8d;
            font-weight: bold;
            font-size: 12pt;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        p {
            margin-bottom: 15px;
            text-align: justify;
        }
        ul, ol {
            margin-bottom: 15px;
            padding-left: 30px;
            line-height: 1.5;
        }
        li {
            margin-bottom: 8px;
            line-height: 1.5;
        }
        /* Professional bullet points */
        ul li {
            list-style-type: disc;
            margin-left: 20px;
        }
        ul ul li {
            list-style-type: circle;
        }
        ul ul ul li {
            list-style-type: square;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        tr:hover {
            background-color: #e8f4f8;
        }
        .highlight {
            background-color: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }
        .summary-box {
            background-color: #d4edda;
            padding: 20px;
            border-left: 4px solid #28a745;
            margin: 20px 0;
            border-radius: 4px;
        }
        .warning-box {
            background-color: #f8d7da;
            padding: 15px;
            border-left: 4px solid #dc3545;
            margin: 20px 0;
            border-radius: 4px;
        }
        .code-block {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            margin: 15px 0;
            overflow-x: auto;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }
        /* Professional Report Header */
        .report-header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            padding: 1rem 0;
        }
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .header-brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-weight: 700;
            font-size: 1.25rem;
            color: #1f2937;
        }
        .header-brand .brand-icon {
            font-size: 1.5rem;
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .header-actions {
            display: flex;
            gap: 0.75rem;
        }
        .action-btn {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.75rem;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        .action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .action-btn:active {
            transform: translateY(0);
        }
        .action-btn.print {
            background: linear-gradient(135deg, #10b981, #059669);
        }
        .action-btn.pdf {
            background: linear-gradient(135deg, #ef4444, #dc2626);
        }
        
        /* Hide download button on mobile devices */
        @media (max-width: 768px) {
            .action-btn.pdf {
                display: none !important;
            }
        }
        .action-btn.save {
            background: linear-gradient(135deg, #8b5cf6, #7c3aed);
        }
        .action-btn.home {
            background: linear-gradient(135deg, #f59e0b, #d97706);
        }
        .btn-icon {
            font-size: 1rem;
        }
        .btn-text {
            font-size: 0.875rem;
        }
        
        /* Report Title Section */
        .report-title-section {
            text-align: center;
            margin-bottom: 2rem;
            padding-top: 6rem;
        }
        .title-underline {
            width: 100px;
            height: 4px;
            background: linear-gradient(90deg, #2563eb, #7c3aed);
            margin: 1rem auto 0;
            border-radius: 2px;
        }
        
        /* Enhanced Summary Box */
        .summary-box {
            background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
            border: 1px solid #bae6fd;
            border-radius: 1rem;
            padding: 1.5rem;
            margin: 2rem 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .summary-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
            font-weight: 600;
            color: #0369a1;
            font-size: 1.125rem;
        }
        .summary-icon {
            font-size: 1.25rem;
        }
        .summary-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }
        .summary-item {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }
        .item-label {
            font-size: 0.875rem;
            font-weight: 500;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .item-value {
            font-size: 1rem;
            font-weight: 600;
            color: #1e293b;
        }
                 @media print {
             body { 
                 background-color: white !important; 
                 color: black !important;
                 font-size: 12pt;
                 line-height: 1.4;
                 margin: 0 !important;
                 padding: 0 !important;
                 width: 100% !important;
             }
             .container { 
                 box-shadow: none !important; 
                 background: white !important;
                 padding: 20px !important;
                 margin: 0 !important;
                 width: 100% !important;
                 min-width: 100% !important;
                 max-width: none !important;
                 box-sizing: border-box !important;
                 height: auto !important;
                 min-height: 100vh !important;
             }
             .report-header { display: none !important; }
             .action-buttons { display: none !important; }
             h1, h2, h3, h4 { 
                 color: black !important; 
                 page-break-after: avoid;
                 page-break-inside: avoid;
             }
             table { 
                 page-break-inside: avoid; 
                 border-collapse: collapse !important;
             }
             .summary-box, .highlight, .warning-box {
                 background: #f8f9fa !important;
                 border: 1px solid #ddd !important;
                 color: black !important;
                 page-break-inside: avoid;
             }
             p, li {
                 page-break-inside: avoid;
                 orphans: 3;
                 widows: 3;
             }
             .footer {
                 page-break-inside: avoid;
             }
             .report-logos {
                 page-break-inside: avoid;
                 margin: 15px 0 !important;
                 padding: 10px !important;
                 background: #f8f9fa !important;
                 border: 1px solid #dee2e6 !important;
             }
             .report-logos img {
                 height: 35px !important;
                 opacity: 0.9 !important;
             }
         }
        /* ===== MOBILE RESPONSIVE DESIGN ===== */
        @media (max-width: 1200px) {
            .header-content {
                padding: 0 1.5rem;
            }
            .container {
                padding: 30px;
            }
        }
        
        @media (max-width: 768px) {
            /* Mobile Header */
            .report-header {
                padding: 0.75rem 0;
            }
            .header-content {
                padding: 0 1rem;
                flex-direction: column;
                gap: 0.75rem;
                align-items: center;
            }
            .header-brand {
                font-size: 1.125rem;
            }
            .header-actions {
                width: 100%;
                justify-content: center;
                gap: 0.5rem;
                flex-wrap: wrap;
            }
            .action-btn {
                padding: 0.5rem 0.75rem;
                font-size: 0.75rem;
                flex: 1;
                max-width: 120px;
                display: flex;
                align-items: center;
                gap: 0.375rem;
            }
            .btn-text {
                font-size: 0.8125rem;
                display: inline !important;
            }
            
            /* Mobile Container */
            .container {
                padding: 20px 15px;
                margin-top: 120px; /* Account for taller mobile header */
            }
            
            /* Mobile Typography */
            h1 {
                font-size: 1.75rem;
                margin-bottom: 20px;
            }
            h2 {
                font-size: 1.375rem;
                margin-top: 25px;
                margin-bottom: 15px;
            }
            h3 {
                font-size: 1.125rem;
                margin-top: 20px;
                margin-bottom: 12px;
            }
            h4 {
                font-size: 1rem;
                margin-top: 15px;
                margin-bottom: 8px;
            }
            p {
                font-size: 0.9375rem;
                line-height: 1.6;
                margin-bottom: 12px;
            }
            
            /* Mobile Tables */
            table {
                font-size: 0.875rem;
                margin: 15px 0;
                display: block;
                overflow-x: auto;
                white-space: nowrap;
                -webkit-overflow-scrolling: touch;
            }
            th, td {
                padding: 8px 6px;
                min-width: 80px;
            }
            th {
                font-size: 0.8125rem;
            }
            
            /* Mobile Lists */
            ul, ol {
                padding-left: 20px;
                margin-bottom: 12px;
            }
            li {
                font-size: 0.9375rem;
                margin-bottom: 6px;
                line-height: 1.5;
            }
            
            /* Mobile Boxes */
            .summary-box, .highlight, .warning-box {
                padding: 15px;
                margin: 15px 0;
                border-radius: 8px;
            }
            .summary-content {
                grid-template-columns: 1fr;
                gap: 0.75rem;
            }
            .summary-item {
                padding: 8px 0;
            }
            .item-label {
                font-size: 0.8125rem;
            }
            .item-value {
                font-size: 0.9375rem;
            }
            
            /* Mobile Code Blocks */
            .code-block {
                padding: 12px;
                font-size: 0.8125rem;
                margin: 12px 0;
                border-radius: 6px;
            }
            
            /* Mobile Footer */
            .footer {
                margin-top: 30px;
                padding-top: 15px;
                font-size: 0.8125rem;
            }
        }
        
        @media (max-width: 480px) {
            /* Extra Small Mobile */
            .container {
                padding: 15px 10px;
                margin-top: 140px;
            }
            
            .header-content {
                padding: 0 0.75rem;
            }
            .header-brand {
                font-size: 1rem;
            }
            .action-btn {
                padding: 0.375rem 0.5rem;
                font-size: 0.6875rem;
                max-width: 100px;
                display: flex;
                align-items: center;
                gap: 0.25rem;
            }
            .btn-text {
                font-size: 0.75rem;
                display: inline !important;
            }
            
            h1 {
                font-size: 1.5rem;
            }
            h2 {
                font-size: 1.25rem;
            }
            h3 {
                font-size: 1.0625rem;
            }
            
            table {
                font-size: 0.8125rem;
            }
            th, td {
                padding: 6px 4px;
                min-width: 70px;
            }
            
            .summary-box, .highlight, .warning-box {
                padding: 12px;
                margin: 12px 0;
            }
            
            .code-block {
                padding: 10px;
                font-size: 0.75rem;
            }
        }
        
        /* Mobile Print Optimizations */
        @media print and (max-width: 768px) {
            .container {
                padding: 15px !important;
                margin: 0 !important;
                width: 100% !important;
            }
            h1, h2, h3, h4 {
                page-break-after: avoid;
                font-size: 1.2em;
            }
            table {
                font-size: 0.8em;
                page-break-inside: avoid;
            }
            .summary-box, .highlight, .warning-box {
                page-break-inside: avoid;
                margin: 10px 0;
            }
        }
        @media screen {
            body {
                margin: 0;
                padding: 0;
            }
        }
        
        /* Saved Reports Section Styles */
        .saved-reports-section {
            padding: 2rem 0;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            min-height: 400px;
        }
        
        .saved-reports-card {
            background: white;
            border-radius: 1rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            padding: 2rem;
            margin: 0 auto;
            max-width: 1200px;
        }
        
        .saved-reports-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .saved-reports-title {
            font-size: 1.75rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .title-icon {
            font-size: 1.5rem;
        }
        
        .saved-reports-subtitle {
            color: #64748b;
            font-size: 1rem;
            margin: 0;
        }
        
        .saved-reports-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .saved-report-item {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 0.75rem;
            padding: 1.5rem;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        
        .saved-report-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            border-color: #3b82f6;
        }
        
        .saved-report-item::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        }
        
        .report-item-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
        }
        
        .report-item-title {
            font-size: 1.125rem;
            font-weight: 600;
            color: #1e293b;
            margin: 0;
            line-height: 1.4;
        }
        
        .report-item-date {
            font-size: 0.875rem;
            color: #64748b;
            white-space: nowrap;
        }
        
        .report-item-details {
            margin-bottom: 1rem;
        }
        
        .report-detail-row {
            display: flex;
            align-items: center;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
        }
        
        .report-detail-label {
            font-weight: 500;
            color: #475569;
            min-width: 80px;
            margin-right: 0.5rem;
        }
        
        .report-detail-value {
            color: #1e293b;
            flex: 1;
        }
        
        .report-item-actions {
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        
        .report-action-btn {
            flex: 1;
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 0.5rem;
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.375rem;
        }
        
        .report-action-btn.primary {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
        }
        
        .report-action-btn.primary:hover {
            background: linear-gradient(135deg, #2563eb, #1e40af);
            transform: translateY(-1px);
        }
        
        .report-action-btn.secondary {
            background: #f1f5f9;
            color: #475569;
            border: 1px solid #e2e8f0;
        }
        
        .report-action-btn.secondary:hover {
            background: #e2e8f0;
            border-color: #cbd5e1;
        }
        
        .no-reports-message {
            text-align: center;
            padding: 3rem 2rem;
            color: #64748b;
        }
        
        .no-reports-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .no-reports-message h3 {
            font-size: 1.25rem;
            font-weight: 600;
            color: #475569;
            margin-bottom: 0.5rem;
        }
        
        .no-reports-message p {
            font-size: 1rem;
            margin: 0;
        }
        
        .saved-reports-toggle {
            background: none;
            border: none;
            color: inherit;
            font-size: inherit;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            transition: all 0.2s ease;
        }
        
        .saved-reports-toggle:hover {
            background: rgba(59, 130, 246, 0.1);
            color: #3b82f6;
        }
        
        .saved-reports-toggle.active {
            background: rgba(59, 130, 246, 0.15);
            color: #3b82f6;
        }
        
        .nav-icon {
            font-size: 1rem;
        }
        
        /* Mobile Responsive for Saved Reports */
        @media (max-width: 768px) {
            .saved-reports-list {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
            
            .saved-report-item {
                padding: 1rem;
            }
            
            .report-item-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 0.5rem;
            }
            
            .report-item-actions {
                flex-direction: column;
            }
            
            .saved-reports-card {
                padding: 1.5rem;
                margin: 0 1rem;
            }
            
        .saved-reports-title {
            font-size: 1.5rem;
        }
    }
    
    /* Loading and Error States */
    .loading-reports {
        text-align: center;
        padding: 2rem;
        color: #64748b;
        font-size: 1rem;
    }
    
        .error-message {
        text-align: center;
        padding: 2rem;
        color: #dc2626;
        font-size: 1rem;
        }

        /* Custom styles for Bootstrap modal enhancements */
        .modal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .modal-header .btn-close {
            filter: invert(1);
        }

        .sortable {
            cursor: pointer;
            user-select: none;
        }

        .sortable:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }

        .sort-indicator {
            margin-left: 8px;
            opacity: 0.5;
            transition: all 0.2s ease;
        }

        .sortable.asc .sort-indicator {
            opacity: 1;
            transform: rotate(180deg);
        }

        .sortable.desc .sort-indicator {
            opacity: 1;
        }

        /* Custom Navbar Styles */
        .navbar {
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 0.75rem 0;
        }

        .navbar-brand {
            font-size: 1.5rem;
            color: #333 !important;
        }

        .navbar-brand .brand-logo-img {
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .navbar-nav .btn {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s ease;
            padding: 0.5rem 1rem;
        }

        .navbar-nav .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        .navbar-nav .btn-outline-primary:hover {
            background-color: #0d6efd;
            border-color: #0d6efd;
        }

        .navbar-nav .btn-outline-secondary:hover {
            background-color: #6c757d;
            border-color: #6c757d;
        }

        .navbar-nav .btn-outline-danger:hover {
            background-color: #dc3545;
            border-color: #dc3545;
        }

        /* Responsive navbar */
        @media (max-width: 768px) {
            .navbar-brand {
                font-size: 1.25rem;
            }
            
            .navbar-nav .btn {
                margin-bottom: 0.5rem;
                width: 100%;
            }
            
            .navbar-nav {
                margin-top: 1rem;
            }
        }

        /* Scrollable Table Styles */
        .table-responsive {
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }

        .table-responsive::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        .table-responsive::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }

        .table-responsive::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 4px;
        }

        .table-responsive::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }

        .sticky-top {
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .table th {
            white-space: nowrap;
            font-weight: 600;
        }

        .table td {
            vertical-align: middle;
        }
    </style>
</head>
<body>
    <!-- Professional Report Header -->
    <header class="report-header">
        <div class="header-content">
            <div class="header-brand">
                <img src="/static/logo_trade_on_chain.png" alt="AI Trade Report" class="brand-logo" style="height: 32px; width: auto; margin-right: 12px;">
                <img src="/static/logo2.png" alt="AI Trade Report" class="brand-logo" style="height: 32px; width: auto; margin-right: 12px;">
                <span class="brand-text">AI Trade Report</span>
            </div>
            <div class="header-actions">
                <button class="action-btn save" onclick="saveReport()">
                    <span class="btn-icon">💾</span>
                    <span class="btn-text">""" + t['save'] + """</span>
                </button>
                <button class="action-btn home" onclick="returnToMain()">
                    <span class="btn-icon">🏠</span>
                    <span class="btn-text">""" + t['return_home'] + """</span>
                </button>
                <button class="action-btn print" onclick="window.print()">
                    <span class="btn-icon">🖨️</span>
                    <span class="btn-text">""" + t['print'] + """</span>
                </button>
                <button class="action-btn pdf" onclick="downloadPDF()">
                    <span class="btn-icon">📄</span>
                    <span class="btn-text">""" + t['download_pdf'] + """</span>
                </button>
            </div>
        </div>
    </header>
    
    <div class="container" id="report-content">
        <div class="report-title-section">
            <h1>""" + t['report_title'] + """</h1>
            <div class="title-underline"></div>
        </div>
        <div class="summary-box">
            <div class="summary-header">
                <span class="summary-icon">📋</span>
                <span class="summary-title">""" + t['report_overview'] + """</span>
            </div>
            <div class="report-logos" style="text-align: center; margin: 20px 0; padding: 15px; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 8px; border: 1px solid #e2e8f0;">
                <div style="display: flex; justify-content: center; align-items: center; gap: 20px; flex-wrap: wrap;">
                    <img src="/static/logo2.png" alt="AI Trade Report" style="height: 40px; width: auto; border-radius: 9px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                </div>
                <div style="margin-top: 10px; font-size: 0.9em; color: #64748b; font-weight: 500;">
                    Professional Market Analysis • Powered by AI Technology
                </div>
            </div>
            <div class="summary-content">
                <div class="summary-item">
                    <span class="item-label">""" + t['generated_by'] + """</span>
                    <span class="item-value">""" + t['ai_powered'] + """</span>
                </div>
                <div class="summary-item">
                    <span class="item-label">""" + t['date'] + """</span>
                    <span class="item-value">""" + datetime.now().strftime('%d %B %Y') + """</span>
                </div>
                <div class="summary-item">
                    <span class="item-label">""" + t['report_type'] + """</span>
                    <span class="item-value">""" + t['comprehensive_analysis'] + """</span>
                </div>"""
    
    # Add form data if available
    if form_data:
        print(f"DEBUG: Adding form data to HTML: {form_data}")
        html += """
                <div class="summary-item">
                    <span class="item-label">Brand Name</span>
                    <span class="item-value">""" + form_data.get('brand', 'N/A') + """</span>
                </div>
                <div class="summary-item">
                    <span class="item-label">Product/Service</span>
                    <span class="item-value">""" + form_data.get('product', 'N/A') + """</span>
                </div>
                <div class="summary-item">
                    <span class="item-label">Investment Budget</span>
                    <span class="item-value">""" + form_data.get('budget', 'N/A') + """</span>
                </div>
                <div class="summary-item">
                    <span class="item-label">Enterprise Size</span>
                    <span class="item-value">""" + form_data.get('enterprise_size', 'N/A') + """</span>
                </div>"""
        
        # Add other information if provided
        if form_data.get('other_info') and form_data.get('other_info').strip():
            html += """
                <div class="summary-item">
                    <span class="item-label">Other Information</span>
                    <span class="item-value">""" + form_data.get('other_info', 'N/A') + """</span>
                </div>"""
        
        # Add hidden form data for JavaScript to extract
        html += f"""
        <script>
        // Store form data for save function
        window.formData = {{
            brand: '{form_data.get('brand', '')}',
            product: '{form_data.get('product', '')}',
            budget: '{form_data.get('budget', '')}',
            enterprise_size: '{form_data.get('enterprise_size', '')}',
            other_info: '{form_data.get('other_info', '')}'
        }};
        console.log('Form data stored:', window.formData);
        </script>"""
    else:
        print("DEBUG: No form data provided to HTML generation")
    
    html += """
            </div>
        </div>
"""
    
    # Process content line by line
    lines = content.split('\n')
    in_table = False
    in_list = False
    list_type = 'ul'
    
    for line in lines:
        line = line.strip()
        
        if not line:
            if in_table:
                # End table
                html += "        </table>\n"
                in_table = False
            elif in_list:
                # End list
                html += f"        </{list_type}>\n"
                in_list = False
            else:
                html += "        <br>\n"
            continue
        
        # Handle different line types
        if line.startswith('# '):
            # Main title
            title = escape_html(line[2:])
            html += f"        <h1>{title}</h1>\n"
        elif line.startswith('## '):
            # Section heading
            title = escape_html(line[3:])
            html += f"        <h2>{title}</h2>\n"
        elif line.startswith('### '):
            # Subsection heading
            title = escape_html(line[4:])
            html += f"        <h3>{title}</h3>\n"
        elif line.startswith('#### '):
            # Sub-subsection heading
            title = escape_html(line[5:])
            html += f"        <h4>{title}</h4>\n"
        elif line.startswith('|') and '|' in line[1:]:
            # Table row
            if not in_table:
                # Start table
                html += "        <table>\n"
                in_table = True
            
            # Process table row
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            escaped_cells = [escape_html(cell) for cell in cells]
            
            # Check if this is a header row (contains dashes or is the first row)
            if any('---' in cell or '--' in cell for cell in cells) or not any('---' in prev_line for prev_line in lines if '|' in prev_line):
                html += "            <tr>\n"
                for cell in escaped_cells:
                    html += f"                <th>{cell}</th>\n"
                html += "            </tr>\n"
            else:
                html += "            <tr>\n"
                for cell in escaped_cells:
                    html += f"                <td>{cell}</td>\n"
                html += "            </tr>\n"
        elif line.startswith('- ') or line.startswith('* '):
            # Bullet point
            if not in_list:
                html += "        <ul>\n"
                in_list = True
                list_type = 'ul'
            text = escape_html(line[2:])
            html += f"            <li>{text}</li>\n"
        elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. ') or line.startswith('4. ') or line.startswith('5. '):
            # Numbered list
            if not in_list:
                html += "        <ol>\n"
                in_list = True
                list_type = 'ol'
            text = escape_html(line[3:])
            html += f"            <li>{text}</li>\n"
        elif line.startswith('**') and line.endswith('**'):
            # Bold text
            text = escape_html(line[2:-2])
            html += f"        <p><strong>{text}</strong></p>\n"
        elif line.startswith('```'):
            # Code block
            if line == '```':
                html += "        <div class=\"code-block\">\n"
            else:
                html += f"        <div class=\"code-block\">\n            {escape_html(line[3:])}\n"
        elif line.endswith('```'):
            # End code block
            html += "        </div>\n"
        elif line.startswith('> '):
            # Quote/note
            text = escape_html(line[2:])
            html += f"        <div class=\"highlight\">{text}</div>\n"
        else:
            # Regular paragraph
            if line:
                text = escape_html(line)
                html += f"        <p>{text}</p>\n"
    
    # Close any open tags
    if in_table:
        html += "        </table>\n"
    if in_list:
        html += f"        </{list_type}>\n"
    
    # Add Other Information section if provided and not already in content
    if form_data and form_data.get('other_info') and form_data.get('other_info').strip():
        other_info_content = form_data.get('other_info', '').strip()
        # Check if Other Information section already exists in content
        content_lower = content.lower()
        if not any(keyword in content_lower for keyword in ['other information', 'additional client requirements', 'altre informazioni', 'requisiti aggiuntivi']):
            # Add fallback Other Information section
            if language == "it":
                html += f"""
        <h2>Altre Informazioni</h2>
        <p>Il cliente ha fornito le seguenti informazioni aggiuntive che devono essere considerate nell'analisi:</p>
        <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 15px 0;">
            <p style="margin: 0; font-style: italic;">"{other_info_content}"</p>
        </div>
        <p>Queste informazioni dovrebbero essere integrate nell'analisi di mercato e nelle raccomandazioni strategiche.</p>
"""
            else:
                html += f"""
        <h2>Other Information</h2>
        <p>The client has provided the following additional information that should be considered in the analysis:</p>
        <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 15px 0;">
            <p style="margin: 0; font-style: italic;">"{other_info_content}"</p>
        </div>
        <p>This information should be integrated into the market analysis and strategic recommendations.</p>
"""
    
    # End HTML document
    html += """        <div class="footer">
            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: center; align-items: center; gap: 15px; margin-bottom: 15px;">
                    <img src="/static/logo_trade_on_chain.png" alt="TradeOnChain" style="height: 30px; width: auto; opacity: 0.8; border-radius: 9px;">
                    <span style="font-size: 1.1em; color: #1e293b; font-weight: 600;">TradeOnChain</span>
                </div>
                <div style="font-size: 0.85em; color: #94a3b8; font-weight: 500; margin-bottom: 10px;">
                    AI Trade Report • Professional Market Analysis
                </div>
            </div>
            <p>""" + t['footer_text1'] + """</p>
            <p>""" + t['footer_text2'] + """</p>
        </div>
    </div>
    
    <script>
        // Define the function immediately when script loads
        function downloadPDF() {
            const element = document.getElementById('report-content');
            
            // Show loading state
            const btn = event.target;
            const originalText = btn.innerHTML;
            btn.innerHTML = '⏳ Generating PDF...';
            btn.disabled = true;
           
           // Wait for fonts and images to load
           setTimeout(function() {
               // First, ensure the element is visible and has content
               if (!element || element.offsetHeight === 0 || element.offsetWidth === 0) {
                   alert('Report content not found. Please refresh the page and try again.');
                   btn.innerHTML = originalText;
                   btn.disabled = false;
                   return;
               }
               
               // Ensure the element is visible and has content
               const rect = element.getBoundingClientRect();
               if (rect.width === 0 || rect.height === 0) {
                   alert('Report content is not visible. Please scroll to the report and try again.');
                   btn.innerHTML = originalText;
                   btn.disabled = false;
                   return;
               }
               
               // Force a reflow to ensure content is rendered
               element.style.display = 'none';
               element.offsetHeight; // Trigger reflow
               element.style.display = 'block';
               
               // Ensure all content is visible and expanded
               element.style.height = 'auto';
               element.style.minHeight = '100vh';
               element.style.overflow = 'visible';
               
               // Wait a bit more for any dynamic content to render
               setTimeout(function() {
               
               const opt = {
                   margin: [0.5, 0.5, 0.5, 0.5],
                   filename: 'AI_Trade_Report.pdf',
                   image: { type: 'jpeg', quality: 0.98 },
                   html2canvas: { 
                       scale: 1.2,
                       useCORS: true,
                       allowTaint: true,
                       backgroundColor: '#ffffff',
                       logging: false,
                       letterRendering: true,
                       width: element.scrollWidth,
                       height: element.scrollHeight,
                       scrollX: 0,
                       scrollY: 0,
                       windowWidth: element.scrollWidth,
                       windowHeight: element.scrollHeight
                   },
                   jsPDF: { 
                       unit: 'in', 
                       format: 'a4', 
                       orientation: 'portrait',
                       compress: true
                   },
                   pagebreak: { mode: ['css', 'legacy'] }
               };
              
              // Debug: Log element dimensions
              console.log('Element dimensions:', {
                  width: element.offsetWidth,
                  height: element.offsetHeight,
                  scrollWidth: element.scrollWidth,
                  scrollHeight: element.scrollHeight,
                  rect: element.getBoundingClientRect()
              });
              
              // Try the main PDF generation
              html2pdf().set(opt).from(element).save().then(function() {
                  btn.innerHTML = originalText;
                  btn.disabled = false;
              }).catch(function(error) {
                  console.error('PDF generation failed:', error);
                  
                  // Fallback: Try with simpler options
                  const simpleOpt = {
                      margin: 0.5,
                      filename: 'AI_Trade_Report.pdf',
                      image: { type: 'jpeg', quality: 0.8 },
                      html2canvas: { 
                          scale: 1,
                          backgroundColor: '#ffffff',
                          width: element.scrollWidth,
                          height: element.scrollHeight,
                          useCORS: true,
                          scrollX: 0,
                          scrollY: 0
                      },
                      jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
                  };
                  
                  html2pdf().set(simpleOpt).from(element).save().then(function() {
                      btn.innerHTML = originalText;
                      btn.disabled = false;
                  }).catch(function(fallbackError) {
                      console.error('Fallback PDF generation also failed:', fallbackError);
                      alert('PDF generation failed. Please use the Print button and save as PDF from your browser instead.');
                      btn.innerHTML = originalText;
                      btn.disabled = false;
                  });
              });
          }, 500);
      }, 1000);
  }
  
  // Also make it available on window object
  window.downloadPDF = downloadPDF;
  
  // Save report function
  // Track if report is saved
  let isReportSaved = false;
  
  function saveReport() {
      console.log('Save report function called');
      
      const btn = event.target.closest('.action-btn');
      if (!btn) {
          console.error('Save button not found');
          return;
      }
      
      // Check if already saved
      if (isReportSaved) {
          btn.innerHTML = '✅ Already Saved';
          btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
          btn.disabled = true;
          
          setTimeout(() => {
              btn.innerHTML = '💾 Save';
              btn.style.background = 'linear-gradient(135deg, #8b5cf6, #7c3aed)';
              btn.disabled = false;
          }, 2000);
          return;
      }
      
      const originalText = btn.innerHTML;
      
      // Show loading state
      btn.innerHTML = '⏳ Saving...';
      btn.disabled = true;
      
      try {
          // Get report data
          const reportTitle = document.querySelector('h1')?.textContent || 'AI Trade Report';
          const reportContent = document.getElementById('report-content')?.innerHTML || '';
          const currentUrl = window.location.pathname;
          const filename = currentUrl.split('/').pop() || 'unknown_report.html';
          
          console.log('Report data extracted:', {
              title: reportTitle,
              filename: filename,
              contentLength: reportContent.length
          });
          
          // Extract form data from embedded JavaScript variable
          let brand = 'Unknown Brand';
          let product = 'Unknown Product';
          let budget = 'Unknown Budget';
          let enterpriseSize = 'Unknown Size';
          
          // Try to get from embedded form data first
          if (window.formData) {
              console.log('Found window.formData:', window.formData);
              brand = window.formData.brand || 'Unknown Brand';
              product = window.formData.product || 'Unknown Product';
              budget = window.formData.budget || 'Unknown Budget';
              enterpriseSize = window.formData.enterprise_size || 'Unknown Size';
              console.log('Extracted form data from embedded variable:', { brand, product, budget, enterpriseSize });
          } else {
              console.log('No window.formData found, trying URL parameters...');
              // Fallback to URL parameters
              const urlParams = new URLSearchParams(window.location.search);
              console.log('Current URL:', window.location.href);
              console.log('URL search params:', window.location.search);
              console.log('URL params object:', Object.fromEntries(urlParams));
              
              brand = urlParams.get('brand') || 'Unknown Brand';
              product = urlParams.get('product') || 'Unknown Product';
              budget = urlParams.get('budget') || 'Unknown Budget';
              enterpriseSize = urlParams.get('enterprise_size') || 'Unknown Size';
              
              console.log('Extracted form data from URL (fallback):', { brand, product, budget, enterpriseSize });
          }
          
          // Prepare data for API
          const reportData = {
              title: reportTitle,
              brand: brand,
              product: product,
              budget: budget,
              enterprise_size: enterpriseSize,
              ai_model: 'gpt-5',
              language: 'en',
              content: reportContent,
              file_path: filename
          };
          
          console.log('Sending data to API:', reportData);
          console.log('Final data being sent:', {
              title: reportData.title,
              brand: reportData.brand,
              product: reportData.product,
              budget: reportData.budget,
              enterprise_size: reportData.enterprise_size
          });
          
          // Send to database
          fetch('/save-report', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify(reportData)
          })
          .then(response => {
              console.log('API response status:', response.status);
              if (!response.ok) {
                  throw new Error(`HTTP error! status: ${response.status}`);
              }
              return response.json();
          })
          .then(data => {
              console.log('API response data:', data);
              if (data.status === 'success') {
                  isReportSaved = true; // Mark as saved
                  btn.innerHTML = '✅ Saved!';
                  btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
                  
                  setTimeout(() => {
                      btn.innerHTML = '💾 Save';
                      btn.style.background = 'linear-gradient(135deg, #8b5cf6, #7c3aed)';
                      btn.disabled = false;
                  }, 2000);
              } else {
                  throw new Error(data.message || 'Failed to save report');
              }
          })
          .catch(error => {
              console.error('Error saving report:', error);
              btn.innerHTML = '❌ Error';
              btn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
              
              setTimeout(() => {
                  btn.innerHTML = originalText;
                  btn.style.background = 'linear-gradient(135deg, #8b5cf6, #7c3aed)';
                  btn.disabled = false;
              }, 3000);
          });
      } catch (error) {
          console.error('Error in saveReport function:', error);
          btn.innerHTML = '❌ Error';
          btn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
          
          setTimeout(() => {
              btn.innerHTML = originalText;
              btn.style.background = 'linear-gradient(135deg, #8b5cf6, #7c3aed)';
              btn.disabled = false;
          }, 3000);
      }
  }
  
  // Return to main page function
  function returnToMain() {
      if (isReportSaved) {
          // If report is saved, go directly without warning
          window.location.href = '/';
      } else {
          // If not saved, show warning
          if (confirm('Are you sure you want to return to the main page? Your current report will be lost.')) {
              window.location.href = '/';
          }
      }
  }
  
  // Make functions available globally
  window.saveReport = saveReport;
  window.returnToMain = returnToMain;
 
          // Hide header when printing
  window.addEventListener('beforeprint', function() {
      const header = document.querySelector('.report-header');
      if (header) header.style.display = 'none';
  });
  
  window.addEventListener('afterprint', function() {
      const header = document.querySelector('.report-header');
      if (header) header.style.display = 'block';
  });
  
  // Ensure function is available when DOM is ready
  document.addEventListener('DOMContentLoaded', function() {
      // Function should be available now
      if (typeof downloadPDF === 'function') {
          console.log('downloadPDF function is ready');
      } else {
          console.error('downloadPDF function not properly defined');
      }
  });
  
  // Also try to make it available immediately
  if (typeof downloadPDF === 'function') {
      console.log('downloadPDF function loaded successfully');
  }
    </script>
</body>
</html>"""
    
    return html

def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    """Get current user from cookie token"""
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            return user
    except:
        return None
    return None

@app.get("/", response_class=HTMLResponse)
def home(request: Request, current_user: User = Depends(get_current_user_from_cookie)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request, "user": current_user})

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0", "service": "AI Trade Report"}

@app.get("/status")
def status_check():
    """Check server status and configuration"""
    return {
        "status": "healthy", 
        "version": "1.0.0", 
        "service": "AI Trade Report",
        "timeout_settings": {
            "client_timeout": "15 minutes",
            "server_timeout": "15 minutes",
            "keep_alive": "30 seconds"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/debug/db")
def debug_database(db: Session = Depends(get_db)):
    """Debug endpoint to check database status"""
    try:
        reports = db.query(Report).all()
        return {
            "status": "success",
            "total_reports": len(reports),
            "reports": [
                {
                    "id": r.id,
                    "title": r.title,
                    "is_saved": r.is_saved,
                    "created_at": r.created_at.isoformat() if r.created_at else None
                } for r in reports
            ]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/test-save")
async def test_save_report(report_data: dict, db: Session = Depends(get_db)):
    """Test endpoint to save report without authentication"""
    try:
        # Create a test report
        test_report = Report(
            user_id=1,  # Use a test user ID
            title=report_data.get("title", "Test Report"),
            brand=report_data.get("brand", "Test Brand"),
            product=report_data.get("product", "Test Product"),
            budget=report_data.get("budget", "Test Budget"),
            enterprise_size=report_data.get("enterprise_size", "Test Size"),
            ai_model=report_data.get("ai_model", "gpt-5"),
            language=report_data.get("language", "en"),
            content=report_data.get("content", "Test content"),
            file_path=report_data.get("file_path", "test.html"),
            is_saved=True
        )
        
        db.add(test_report)
        db.commit()
        db.refresh(test_report)
        
        return JSONResponse({
            "status": "success",
            "message": "Test report saved successfully",
            "report_id": test_report.id
        })
        
    except Exception as e:
        print(f"Error in test save: {e}")
        db.rollback()
        return JSONResponse({
            "status": "error",
            "message": f"Failed to save test report: {str(e)}"
        }, status_code=500)

@app.get("/debug/select2")
def debug_select2(request: Request):
    """Debug endpoint to test Select2 functionality"""
    return templates.TemplateResponse("debug_select2.html", {"request": request})

@app.get("/test-save")
def test_save_page():
    """Test page for save functionality"""
    with open("test_save.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/debug/auth")
def debug_auth(current_user: User = Depends(get_current_user_from_cookie)):
    """Debug endpoint to check authentication status"""
    if current_user:
        return {
            "status": "authenticated",
            "user_id": current_user.id,
            "user_name": f"{current_user.name} {current_user.surname}",
            "user_email": current_user.email
        }
    else:
        return {
            "status": "not_authenticated",
            "message": "User not logged in"
        }

@app.get("/api/search-terms")
def search_terms(q: str = "", limit: int = 20, db: Session = Depends(get_db)):
    """Search for product terms"""
    if not q or len(q) < 2:
        return {"terms": []}
    
    # Search for terms that contain the query string (case insensitive)
    terms = db.query(ProductTerm).filter(
        ProductTerm.term.ilike(f"%{q}%")
    ).limit(limit).all()
    
    return {
        "terms": [
            {
                "id": term.id,
                "term": term.term,
                "description": term.description,
                "category": term.category
            }
            for term in terms
        ]
    }

@app.get("/api/select2-terms")
def select2_terms(q: str = "", page: int = 1, per_page: int = 20, db: Session = Depends(get_db)):
    """Search for product terms in Select2 format"""
    if not q or len(q) < 2:
        return {"results": [], "pagination": {"more": False}}
    
    # Calculate offset for pagination
    offset = (page - 1) * per_page
    
    # Search for terms that contain the query string (case insensitive)
    terms_query = db.query(ProductTerm).filter(
        ProductTerm.term.ilike(f"%{q}%")
    )
    
    # Get total count for pagination
    total_count = terms_query.count()
    
    # Get paginated results
    terms = terms_query.offset(offset).limit(per_page + 1).all()
    
    # Check if there are more results
    has_more = len(terms) > per_page
    if has_more:
        terms = terms[:per_page]
    
    return {
        "results": [
            {
                "id": term.term,  # Use term as ID for Select2
                "text": term.term,
                "description": term.description,
                "category": term.category
            }
            for term in terms
        ],
        "pagination": {
            "more": has_more
        }
    }

@app.post("/generate", response_class=JSONResponse)
async def generate_report(
    request: Request,
    brand: str = Form(...),
    product: str = Form(...),
    budget: str = Form(""),
    enterprise_size: str = Form(...),
    other_info: str = Form(""),
    ai_model: str = Form("gpt-5"),
    language: str = Form("en"),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    if not current_user:
        return JSONResponse({"status": "error", "message": "Authentication required. Please log in to generate reports."}, status_code=401)
    
    try:
        # Debug: Log received values
        print(f"DEBUG: Received brand: '{brand}'")
        print(f"DEBUG: Received product: '{product}'")
        print(f"DEBUG: Received budget: '{budget}'")
        print(f"DEBUG: Received enterprise_size: '{enterprise_size}'")
        print(f"DEBUG: Received other_info: '{other_info}'")
        
        # Build prompt
        spec = InputSpec(brand=brand.strip(), product=product.strip(), budget=budget.strip(), enterprise_size=enterprise_size.strip(), other_info=other_info.strip())
        prompt_text = build_prompt(spec, analysis_date=datetime.now().strftime("%d %B %Y"), language=language)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        user_id = current_user.id
        report_filename_txt = f"reports/report_{user_id}_{timestamp}.txt"
        report_filename_pdf = f"report_{user_id}_{timestamp}"

        # Debug: Log the received AI model
        print(f"DEBUG: Received ai_model: '{ai_model}'")
        
        # Generate report with timeout
        try:
            print(f"DEBUG: Starting report generation at {datetime.now()}")
            if ai_model != "none" and ai_model != "undefined":
                print(f"DEBUG: Generating report with AI model: {ai_model}")
                print(f"DEBUG: Prompt length: {len(prompt_text)} characters")
                report_text = call_openai_chat(prompt_text, model=ai_model)
                print(f"DEBUG: AI generation completed successfully at {datetime.now()}")
                print(f"DEBUG: Generated report length: {len(report_text) if report_text else 0} characters")
            else:
                if ai_model == "undefined":
                    print("DEBUG: AI model was 'undefined', using gpt-5 as fallback")
                    report_text = call_openai_chat(prompt_text, model="gpt-5")
                else:
                    print("DEBUG: Using prompt text as fallback")
                    report_text = prompt_text
        except Exception as ai_error:
            print(f"AI generation error: {ai_error}")
            # Provide a more informative fallback
            # Handle multiple products in error message
            products = [p.strip() for p in product.split(',') if p.strip()]
            if len(products) > 1:
                product_list = "\n".join([f"- {p}" for p in products])
                product_section = f"### Products/Services:\n{product_list}"
            else:
                product_section = f"### Product: {product}"
            
            report_text = f"""# AI Trade Report - {brand}

**Note:** AI generation encountered an error: {str(ai_error)}

## Market Analysis

This is a basic market analysis template. For a full AI-generated report, please try again or contact support.

{product_section}
### Brand: {brand}
### Enterprise Size: {enterprise_size}
### Budget: {budget if budget else 'Not specified'}

## Analysis

The AI system encountered an error during report generation. This could be due to:
- High server load
- Network connectivity issues
- API rate limiting

Please try generating the report again in a few minutes.

## Next Steps

1. Verify your internet connection
2. Try again with the same parameters
3. If the issue persists, contact support

---
*Report generated on {datetime.now().strftime('%d %B %Y')}*"""

        # Ensure report_text is not None and not empty
        if report_text is None or report_text.strip() == "":
            # Handle multiple products in empty report message
            products = [p.strip() for p in product.split(',') if p.strip()]
            if len(products) > 1:
                product_list = "\n".join([f"- {p}" for p in products])
                product_section = f"## Products/Services:\n{product_list}"
            else:
                product_section = f"## Product: {product}"
            
            report_text = f"""# AI Trade Report - {brand}

**Error:** Unable to generate report content. Please try again.

{product_section}
## Brand: {brand}
## Enterprise Size: {enterprise_size}
## Budget: {budget if budget else 'Not specified'}

## Troubleshooting

If you continue to experience issues, please:
1. Check your internet connection
2. Verify your OpenAI API key is valid
3. Try again in a few minutes
4. Contact support if the problem persists

---
*Report generated on {datetime.now().strftime('%d %B %Y')}*"""

        # Save text version
        with open(report_filename_txt, "w", encoding="utf-8") as f:
            f.write(report_text)

        # Create HTML version
        form_data = {
            'brand': brand,
            'product': product,
            'budget': budget,
            'enterprise_size': enterprise_size,
            'other_info': other_info
        }
        html_path = create_html_report(report_text, report_filename_pdf, language, form_data)
        actual_filename = f"{report_filename_pdf}.html"

        # Save report metadata to database
        try:
            print(f"DEBUG: Saving report to database with form data:")
            print(f"  Brand: '{brand}'")
            print(f"  Product: '{product}'")
            print(f"  Budget: '{budget}'")
            print(f"  Enterprise Size: '{enterprise_size}'")
            
            report_record = Report(
                user_id=user_id,
                title=f"AI Trade Report - {brand}",
                brand=brand,
                product=product,
                budget=budget,
                enterprise_size=enterprise_size,
                ai_model=ai_model,
                language=language,
                content=report_text,  # Store the text content
                file_path=actual_filename,
                is_saved=False  # Not saved by user yet
            )
            db.add(report_record)
            db.commit()
            db.refresh(report_record)
            print(f"DEBUG: Report saved successfully with ID: {report_record.id}")
        except Exception as e:
            print(f"Warning: Could not save report metadata to database: {e}")

        # Return JSON with redirect URL for AJAX handling, including form data
        form_data_params = f"?brand={brand}&product={product}&budget={budget}&enterprise_size={enterprise_size}"
        return JSONResponse({
            "status": "success",
            "redirect_url": f"/report/{actual_filename}{form_data_params}",
            "report_name": actual_filename
        })
        
    except Exception as e:
        print(f"Error generating report: {e}")
        return HTMLResponse(f"<h1>Error generating report: {str(e)}</h1>", status_code=500)

@app.get("/job-status/{job_id}")
def get_job_status(job_id: str):
    """Get the status of a report generation job"""
    with job_lock:
        if job_id in job_status:
            return job_status[job_id]
        else:
            return {"status": "not_found", "message": "Job not found"}

@app.get("/report/{filename}")
def view_report(filename: str):
    filepath = os.path.join("reports", filename)
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type="text/html")
    return {"status": "error", "message": "Report not found"}

@app.get("/download/{filename}")
def download_report(filename: str):
    filepath = os.path.join("reports", filename)
    if os.path.exists(filepath):
        # Determine media type based on file extension
        if filename.endswith('.html'):
            media_type = "text/html"
        elif filename.endswith('.pdf'):
            media_type = "application/pdf"
        elif filename.endswith('.txt'):
            media_type = "text/plain"
        else:
            media_type = "application/octet-stream"
        
        return FileResponse(filepath, media_type=media_type, filename=filename)
    return {"status": "error", "message": "File not found"}

@app.post("/save-report")
async def save_report_to_db(
    request: Request,
    report_data: dict,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Save report to database"""
    try:
        print(f"Save report request received. User: {current_user}")
        print(f"Report data: {report_data}")
        
        if not current_user:
            print("No authenticated user found")
            return JSONResponse({"status": "error", "message": "Authentication required"}, status_code=401)
        
        # Extract report data with validation
        title = report_data.get("title", "AI Trade Report")
        brand = report_data.get("brand", "")
        product = report_data.get("product", "")
        budget = report_data.get("budget", "")
        enterprise_size = report_data.get("enterprise_size", "")
        ai_model = report_data.get("ai_model", "gpt-5")
        language = report_data.get("language", "en")
        content = report_data.get("content", "")
        file_path = report_data.get("file_path", "")
        
        print(f"Extracted data - Title: {title}, Brand: {brand}, Product: {product}")
        
        # Validate required fields
        if not title or not content:
            return JSONResponse({
                "status": "error",
                "message": "Title and content are required"
            }, status_code=400)
        
        # Create new report record
        new_report = Report(
            user_id=current_user.id,
            title=title[:500],  # Limit title length
            brand=brand[:200],  # Limit brand length
            product=product[:500],  # Limit product length
            budget=budget[:100],  # Limit budget length
            enterprise_size=enterprise_size[:50],  # Limit size length
            ai_model=ai_model[:100],  # Limit model length
            language=language[:10],  # Limit language length
            content=content,  # Content can be large
            file_path=file_path[:500],  # Limit file path length
            is_saved=True
        )
        
        print(f"Creating report for user {current_user.id}")
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        
        print(f"Report saved successfully with ID: {new_report.id}")
        
        return JSONResponse({
            "status": "success",
            "message": "Report saved successfully",
            "report_id": new_report.id
        })
        
    except Exception as e:
        print(f"Error saving report: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return JSONResponse({
            "status": "error",
            "message": f"Failed to save report: {str(e)}"
        }, status_code=500)

@app.get("/my-reports")
async def get_user_reports(
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Get user's saved reports"""
    try:
        if not current_user:
            return JSONResponse({"status": "error", "message": "Authentication required"}, status_code=401)
        
        reports = db.query(Report).filter(
            Report.user_id == current_user.id,
            Report.is_saved == True
        ).order_by(Report.created_at.desc()).all()
        
        # Ensure all required fields are present
        reports_data = []
        for report in reports:
            try:
                reports_data.append({
                    "id": report.id,
                    "title": report.title or "Untitled Report",
                    "brand": report.brand or "Unknown Brand",
                    "product": report.product or "Unknown Product",
                    "budget": report.budget or "Unknown Budget",
                    "enterprise_size": report.enterprise_size or "Unknown Size",
                    "ai_model": report.ai_model or "gpt-5",
                    "language": report.language or "en",
                    "created_at": report.created_at.isoformat() if report.created_at else "",
                    "file_path": report.file_path or ""
                })
            except Exception as e:
                print(f"Error processing report {report.id}: {e}")
                continue
        
        return JSONResponse({
            "status": "success",
            "reports": reports_data
        })
        
    except Exception as e:
        print(f"Error fetching user reports: {e}")
        return JSONResponse({
            "status": "error",
            "message": f"Failed to fetch reports: {str(e)}"
        }, status_code=500)

@app.delete("/delete-report/{report_id}")
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Delete a saved report"""
    try:
        if not current_user:
            return JSONResponse({"status": "error", "message": "Authentication required"}, status_code=401)
        
        # Validate report_id
        if not isinstance(report_id, int) or report_id <= 0:
            return JSONResponse({
                "status": "error",
                "message": "Invalid report ID"
            }, status_code=400)
        
        # Find the report
        report = db.query(Report).filter(
            Report.id == report_id,
            Report.user_id == current_user.id,
            Report.is_saved == True
        ).first()
        
        if not report:
            return JSONResponse({
                "status": "error",
                "message": "Report not found or you don't have permission to delete it"
            }, status_code=404)
        
        # Delete the report
        db.delete(report)
        db.commit()
        
        return JSONResponse({
            "status": "success",
            "message": "Report deleted successfully"
        })
        
    except Exception as e:
        print(f"Error deleting report {report_id}: {e}")
        db.rollback()
        return JSONResponse({
            "status": "error",
            "message": f"Failed to delete report: {str(e)}"
        }, status_code=500)
