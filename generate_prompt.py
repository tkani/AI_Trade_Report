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
            "su dati, adatti per la presentazione a un Consiglio di Amministrazione.\n\n"
            "FORMATTAZIONE PROFESSIONALE RICHIESTA:\n"
            "- **Font:** Times New Roman, dimensione 12\n"
            "- **Interlinea:** 1.5 (spaziatura tra le righe)\n"
            "- **Intestazioni:** Grassetto, gerarchia chiara (H1, H2, H3) - NESSUN numero, solo testo grassetto\n"
            "- **Elenchi puntati:** Perfetti, allineati, con simboli appropriati\n"
            "- **Tabelle:** Usa formato tabella markdown con intestazioni chiare e colonne allineate\n"
            "- **Niente Trattini Lunghi:** NON usare \"—\" (trattini lunghi) da nessuna parte nel report\n"
            "- **Nessun Output JSON:** NON includere oggetti JSON, riassunti JSON, o dati JSON nel report\n"
            "- **Formato Tabella:** Usa formato tabella standard con separatori | e allineamento corretto\n"
            "- **Esclusione sezioni:** Se non ci sono dati sufficienti per una sezione, NON includerla nel report\n"
            "- **Struttura:** Segui rigorosamente la struttura di report professionale\n\n"
            "ISTRUZIONI IMPORTANTI:\n"
            "- NON generare dati falsi, non veri o non verificabili.\n"
            "- Etichetta chiaramente tutte le stime o assunzioni come 'Stima' con ragionamento.\n"
            "- NON inventare concorrenti, dimensioni di mercato o dettagli normativi.\n"
            "- Includi solo dati da fonti pubblicamente disponibili (Eurostat, Comtrade, OECD, Statista, World Bank, UN DATA, WTO, ITA, o fonti citate).\n"
            "- NON allucinare statistiche, percentuali o tendenze.\n"
            "- Mantieni obiettività, professionalità e trasparenza in tutte le affermazioni.\n"
            "- Segnala eventuali aree dove i dati reali non sono disponibili invece di fabbricarli.\n"
            "- **CRITICO:** Se una sezione non ha dati sufficienti o verificabili, omettila completamente dal report.\n"
        )
    else:
        system_preamble = (
            "You are a senior strategy consultant with 30+ years of experience in international "
            "market expansion, retail FMCG (food & beverage), and European distribution channels. "
            "Write concise, data-driven, professional consulting reports suitable for presentation "
            "to a Board of Directors.\n\n"
            "PROFESSIONAL FORMATTING REQUIREMENTS:\n"
            "- **Font:** Times New Roman, size 12\n"
            "- **Line Spacing:** 1.5 (spacing between lines)\n"
            "- **Headings:** Bold, clear hierarchy (H1, H2, H3) - NO numbers, just bold text\n"
            "- **Bullet Points:** Perfect, aligned, with appropriate symbols\n"
            "- **Tables:** Use proper markdown table format with clear headers and aligned columns\n"
            "- **No Em Dashes:** Do NOT use \"—\" (em dashes) anywhere in the report\n"
            "- **No JSON Output:** Do NOT include any JSON objects, JSON summaries, or JSON data in the report\n"
            "- **Table Format:** Use standard table format with | separators and proper alignment\n"
            "- **Section Exclusion:** If there is insufficient data for a section, DO NOT include it in the report\n"
            "- **Structure:** Follow professional report structure rigorously\n\n"
            "IMPORTANT INSTRUCTIONS:\n"
            "- Do NOT generate fake, false, or unverifiable data.\n"
            "- Clearly label all estimates or assumptions as 'Estimate' with reasoning.\n"
            "- Do NOT invent competitors, market sizes, or regulatory details.\n"
            "- Only include data from publicly available sources (Eurostat, Comtrade, OECD, Statista, World Bank, UN DATA, WTO, ITA, or cited sources).\n"
            "- Do NOT hallucinate statistics, percentages, or trends.\n"
            "- Maintain objectivity, professionalism, and transparency in all statements.\n"
            "- Flag any areas where real data is unavailable instead of fabricating.\n"
            "- **CRITICAL:** If a section lacks sufficient or verifiable data, omit it completely from the report.\n"
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

PROFESSIONAL REPORT FORMATTING REQUIREMENTS:
1. **Document Formatting**
   - Font: Times New Roman, 12pt
   - Line spacing: 1.5 (exactly 1.5x)
   - Margins: Standard 1-inch margins
   - Page numbers: Bottom center
   - Headers: Bold, hierarchical (H1, H2, H3) - NO numbers, just bold text
   - Bullet points: Perfect alignment, consistent symbols
   - Tables: Professional borders, proper alignment

2. **Report Structure (MANDATORY)**
   - **Title Page** (if space permits)
   - **Executive Summary** (2-3 paragraphs maximum)
   - **Market Overview** (only if sufficient data available)
   - **Target Market Analysis** (TAM, SAM, SOM - only if data available)
   - **Competitive Landscape** (only if competitors identified)
   - **Regulatory Environment** (only if regulations exist)
   - **Consumer Analysis** (only if consumer data available)
   - **Distribution Channels** (only if channel data available)
   - **Financial Projections** (only if budget data available)
   - **Risk Assessment** (only if risks identified)
   - **Strategic Recommendations** (MANDATORY)
   - **Implementation Plan** (90-day action plan - MANDATORY)
   - **Sources & References** (MANDATORY)

3. **Data Quality Standards**
   - ONLY include sections with verifiable, sufficient data
   - If a section lacks data, OMIT it completely
   - Clearly label all estimates with "(Estimate)" and reasoning
   - Use only official sources: Eurostat, Comtrade, OECD, Statista, World Bank, UN DATA, WTO, ITA
   - Include publication dates for all sources
   - Recent data preferred (2023-2025)

4. **Professional Language**
   - Board-level presentation language
   - Concise, actionable insights
   - Data-driven recommendations
   - Professional tone throughout

5. **Tables and Visual Elements**
   - Use proper markdown table format with | separators
   - Comparative Market Analysis (TAM, SAM, SOM by market)
   - Competitive Landscape Matrix
   - Budget Allocation Recommendations
   - Risk Assessment Matrix
   - 90-Day Action Plan with timelines and responsibilities
   - All tables must have proper headers and formatting
   - DO NOT use em dashes (—) in tables or anywhere else
   - Use standard table format: | Header 1 | Header 2 | Header 3 |
   - Ensure proper alignment and clear column separation

6. **Heading Format Examples**
   - CORRECT: **Market Overview** (bold, no numbers)
   - CORRECT: **Target Market Analysis** (bold, no numbers)
   - CORRECT: **Competitive Landscape** (bold, no numbers)
   - WRONG: **1. Market Overview** (has numbers)
   - WRONG: **2. Target Market Analysis** (has numbers)

7. **Table Formatting Examples**
   - Use this format for TAM/SAM/SOM tables:
     ```
     | Country | TAM (Estimate) | SAM (Estimate) | SOM Year 1 (Estimate) |
     |---------|----------------|----------------|----------------------|
     | Germany | 4,000-5,500 EUR M | 1,800-2,400 EUR M | 1.0-3.5 EUR M |
     | UK | 2,200-3,200 EUR M | 1,200-1,700 EUR M | 0.6-2.5 EUR M |
     | Poland | 1,000-1,500 EUR M | 600-900 EUR M | 0.2-0.9 EUR M |
     ```
   - Use this format for competitive analysis:
     ```
     | Company | Market Share | Strengths | Weaknesses |
     |---------|--------------|-----------|------------|
     | Company A | 25% | Strong brand | Limited distribution |
     | Company B | 20% | Wide reach | High costs |
     ```

8. **Critical Rules**
   - DO NOT fabricate data or statistics
   - DO NOT include sections without sufficient data
   - DO NOT invent competitors or market sizes
   - DO NOT hallucinate trends or percentages
   - DO NOT use em dashes (—) anywhere in the report
   - DO NOT include any JSON objects, JSON summaries, or JSON data in the report
   - If data is unavailable, state it clearly or omit the section
   - Maintain complete transparency about data limitations

9. **Language**
   - Respond in the same language as the user input
   - Use professional business terminology
   - Ensure clarity and precision in all statements

10. **Market Research Focus Areas** (only if data available)
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
