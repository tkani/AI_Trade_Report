from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()


@dataclass
class InputSpec:
    brand: str
    product: str
    budget: str
    enterprise_size: str

def validate_input(spec: InputSpec):
    if not spec.brand or not spec.product or not spec.budget or not spec.enterprise_size:
        raise ValueError("brand, product, budget and enterprise_size must be provided")
    if len(spec.brand) > 120 or len(spec.product) > 120:
        raise ValueError("brand/product too long")
    if len(spec.budget) > 40:
        raise ValueError("budget string too long")
    if spec.enterprise_size not in ["small", "medium", "large"]:
        raise ValueError("enterprise_size must be small, medium, or large")

def build_prompt(spec: InputSpec, analysis_date: Optional[str] = None, language: str = "en") -> str:
    # Language-specific prompts
    if language == "it":
        system_preamble = (
            "Sei un consulente strategico senior con oltre 30 anni di esperienza nell'espansione "
            "internazionale dei mercati, nel retail FMCG (alimentari e bevande) e nei canali di "
            "distribuzione europei. Scrivi report di consulenza professionali, concisi e basati "
            "su dati, adatti per la presentazione a un Consiglio di Amministrazione. Usa intestazioni "
            "chiare, elenchi puntati, tabelle (markdown) e includi numerici (stime TAM, SAM, SOM), "
            "rischi, mitigazioni e un piano d'azione di 90 giorni.\n\n"
            "ISTRUZIONI IMPORTANTI:\n"
            "- NON generare dati falsi, non veri o non verificabili.\n"
            "- Etichetta chiaramente tutte le stime o assunzioni come 'Stima' con ragionamento.\n"
            "- NON inventare concorrenti, dimensioni di mercato o dettagli normativi.\n"
            "- Includi solo dati da fonti pubblicamente disponibili (Eurostat, Comtrade, OECD, Statista, World Bank, UN DATA, WTO, ITA, o fonti citate).\n"
            "- NON allucinare statistiche, percentuali o tendenze.\n"
            "- Mantieni obiettività, professionalità e trasparenza in tutte le affermazioni.\n"
            "- Segnala eventuali aree dove i dati reali non sono disponibili invece di fabbricarli.\n"
        )
    else:
        system_preamble = (
            "You are a senior strategy consultant with 30+ years of experience in international "
            "market expansion, retail FMCG (food & beverage), and European distribution channels. "
            "Write concise, data-driven, professional consulting reports suitable for presentation "
            "to a Board of Directors. Use clear headings, bullet points, tables (markdown), and "
            "include numerics (TAM, SAM, SOM estimates), risks, mitigations, and a 90-day action plan.\n\n"
            "IMPORTANT INSTRUCTIONS:\n"
            "- Do NOT generate fake, false, or unverifiable data.\n"
            "- Clearly label all estimates or assumptions as 'Estimate' with reasoning.\n"
            "- Do NOT invent competitors, market sizes, or regulatory details.\n"
            "- Only include data from publicly available sources (Eurostat, Comtrade, OECD, Statista, World Bank, UN DATA, WTO, ITA, or cited sources).\n"
            "- Do NOT hallucinate statistics, percentages, or trends.\n"
            "- Maintain objectivity, professionalism, and transparency in all statements.\n"
            "- Flag any areas where real data is unavailable instead of fabricating.\n"
        )

    if language == "it":
        # Map enterprise size to Italian
        enterprise_size_map = {
            "small": "Piccola Impresa",
            "medium": "Media Impresa", 
            "large": "Grande Impresa"
        }
        enterprise_size_it = enterprise_size_map.get(spec.enterprise_size, spec.enterprise_size)
        
        user_instruction = (
            f"Ricerca e analizza le opportunità di espansione del mercato per *{spec.product}* "
            f"sotto il brand *{spec.brand}* con un budget totale disponibile di **{spec.budget}**.\n"
            f"**Dimensione Azienda:** {enterprise_size_it}\n\n"
            "Conduci una ricerca di mercato completa focalizzandoti su:\n"
            "- Identificazione e dimensionamento del mercato target (TAM, SAM, SOM)\n"
            "- Analisi del panorama competitivo\n"
            "- Requisiti normativi e di conformità\n"
            "- Comportamento del consumatore e modelli di acquisto\n"
            "- Canali di distribuzione e barriere all'ingresso\n"
            "- Strategie di pricing e strutture dei costi\n"
            "- Tendenze tecnologiche e opportunità di innovazione\n"
            "- Valutazione del rischio e strategie di mitigazione\n\n"
            "Fornisci insights azionabili e raccomandazioni strategiche per un ingresso di successo nel mercato.\n"
        )
    else:
        # Map enterprise size to English
        enterprise_size_map = {
            "small": "Small Enterprise",
            "medium": "Medium Enterprise",
            "large": "Big Enterprise"
        }
        enterprise_size_en = enterprise_size_map.get(spec.enterprise_size, spec.enterprise_size)
        
        user_instruction = (
            f"Research and analyze the market expansion opportunities for *{spec.product}* "
            f"under the brand *{spec.brand}* with a total available budget of **{spec.budget}**.\n"
            f"**Enterprise Size:** {enterprise_size_en}\n\n"
            "Conduct comprehensive market research focusing on:\n"
            "- Target market identification and sizing (TAM, SAM, SOM)\n"
            "- Competitive landscape analysis\n"
            "- Regulatory and compliance requirements\n"
            "- Consumer behavior and purchasing patterns\n"
            "- Distribution channels and entry barriers\n"
            "- Pricing strategies and cost structures\n"
            "- Technology trends and innovation opportunities\n"
            "- Risk assessment and mitigation strategies\n\n"
            "Provide actionable insights and strategic recommendations for successful market entry.\n"
        )

    if analysis_date:
        user_instruction += f"\nAnalysis Date: {analysis_date}\n"
    else:
        user_instruction += f"\nAnalysis Date: {datetime.now().strftime('%d %B %Y')}\n"

    user_instruction += (
        "\nAdditionally, return a JSON object delimited by triple backticks at the end of the response "
        "with keys: top_markets (array of 3 market ISO codes), budget_allocation (dict), "
        "tams (dict market->TAM_M), assumptions (list of strings). All assumptions must be clearly labeled.\n"
    )

    return f"{system_preamble}\n\n{user_instruction}"

def call_openai_chat(prompt: str, model="gpt-5", temperature=0.0) -> str:
    if OpenAI is None:
        raise RuntimeError("openai package not installed")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
    
    # Initialize OpenAI client with new API format
    client = OpenAI(api_key=api_key)
    
    # Research task instructions for market analysis
    research_instructions = """
You will be given a market analysis research task by a user. Your job is to produce a comprehensive 
Strategic Market Analysis Report that will help with business expansion decisions. Complete the full 
analysis with detailed research and actionable insights.

GUIDELINES:
1. **Maximize Specificity and Detail**
- Include all known user preferences and explicitly analyze key market attributes, 
  competitive landscape, and growth opportunities.
- It is of utmost importance that all details from the user are thoroughly analyzed 
  and included in the final report.

2. **Fill in Unstated But Necessary Dimensions as Open-Ended**
- If certain market attributes are essential for a meaningful analysis but the user 
  has not provided them, explicitly state that they are open-ended or default 
  to comprehensive market coverage.

3. **Avoid Unwarranted Assumptions**
- If the user has not provided a particular detail, do not invent one.
- Instead, state the lack of specification and provide analysis across all 
  relevant market dimensions.

4. **Use Professional Business Language**
- Phrase the analysis from the perspective of a senior strategy consultant 
  presenting to a Board of Directors.

5. **Tables and Structured Data**
- You must include comprehensive tables for:
  - Comparative Market Analysis (TAM, SAM, SOM by market)
  - Competitive Landscape Matrix
  - Budget Allocation Recommendations
  - Risk Assessment Matrix
  - 90-Day Action Plan with timelines and responsibilities

6. **Headers and Formatting**
- Format as a professional consulting report with clear headers:
  - Executive Summary
  - Market Analysis
  - Competitive Landscape
  - Strategic Recommendations
  - Risk Assessment
  - 90-Day Action Plan
  - Sources & Appendix

7. **Language**
- Respond in the same language as the user input, unless explicitly requested otherwise.

8. **Sources and Data Integrity**
- Prioritize official sources: Eurostat, Comtrade, OECD, Statista, World Bank, UN DATA, WTO, ITA, government databases
- For market data, prefer official industry reports and regulatory publications
- Always cite sources with publication dates
- Clearly label estimates vs. verified data
- Include recent data (2023-2025) when available

9. **Market Research Focus Areas**
- Current market sizes and growth rates
- Regulatory environment and compliance requirements
- Consumer behavior and purchasing patterns
- Distribution channels and entry barriers
- Competitive positioning and market share
- Pricing strategies and cost structures
- Technology trends and innovation opportunities
"""
    
    # Use the research task API format
    try:
        response = client.responses.create(
            model=model,
            input=prompt,
            instructions=research_instructions,
            reasoning={
                "effort": "minimal"
            }
        )
        
        # Extract text content safely
        if hasattr(response, 'output_text') and response.output_text:
            return response.output_text
        
        # Try alternative extraction methods
        if hasattr(response, 'output') and response.output:
            # Look for message content in the output
            for item in response.output:
                if hasattr(item, 'content') and item.content:
                    for content_item in item.content:
                        if hasattr(content_item, 'text') and content_item.text:
                            return content_item.text
        
        # If still no content, raise an error to trigger fallback
        raise ValueError("No text content found in response")
        
    except Exception as e:
        print(f"Research API error: {e}")
        # Fallback to regular chat completion if research API is not available
        try:
            messages = [
                {"role": "system", "content": research_instructions},
                {"role": "user", "content": prompt},
            ]
            
            api_params = {
                "model": model,
                "messages": messages,
            }
            
            # Add appropriate parameters based on model
            if model == "gpt-5":
                # GPT-5 only supports default temperature (1) and no custom token limits
                pass  # Let GPT-5 use its default settings
            else:
                api_params["temperature"] = temperature
                api_params["max_tokens"] = 4000
            
            response = client.chat.completions.create(**api_params)
            return response.choices[0].message.content
        except Exception as fallback_error:
            print(f"Fallback API error: {fallback_error}")
            # Return a default error message if all else fails
            return f"Error generating report: {str(e)}. Please try again or contact support."
