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
    other_info: str = ""

def validate_input(spec: InputSpec):
    if not spec.brand or not spec.product or not spec.enterprise_size:
        raise ValueError("brand, product and enterprise_size must be provided")
    if len(spec.brand) > 120 or len(spec.product) > 120:
        raise ValueError("brand/product too long")
    if spec.budget and len(spec.budget) > 40:
        raise ValueError("budget string too long")
    if spec.enterprise_size not in ["small", "medium", "large"]:
        raise ValueError("enterprise_size must be small, medium, or large")
    if spec.other_info and len(spec.other_info) > 500:
        raise ValueError("other_info too long (max 500 characters)")

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
        
        # Handle empty or zero budget
        budget_text = ""
        if not spec.budget or spec.budget.strip() == "" or spec.budget == "0":
            budget_text = "**IMPORTANTE:** Il cliente non ha specificato un budget. Analizza il mercato e suggerisci un budget appropriato basato sulla dimensione aziendale, il prodotto e i mercati target. Includi una sezione dedicata 'Raccomandazioni di Budget' con una giustificazione dettagliata.\n\n"
        else:
            budget_text = f"con un budget totale disponibile di **{spec.budget}**.\n"
        
        # Handle multiple products for Italian
        products = [p.strip() for p in spec.product.split(',') if p.strip()]
        if len(products) > 1:
            product_text = f"i seguenti prodotti/servizi: {', '.join(products)}"
            product_analysis_text = f"""
**ANALISI PORTAFOGLIO PRODOTTI:**
- **Prodotto/Servizio Principale:** {products[0]}
- **Prodotti/Servizi Aggiuntivi:** {', '.join(products[1:])}
- **Strategia del Portafoglio:** Analizza ogni prodotto individualmente e come portafoglio coeso
- **Opportunità di Cross-selling:** Identifica sinergie tra i prodotti
- **Posizionamento di Mercato:** Come il portafoglio prodotti posiziona il brand nei mercati target
"""
        else:
            product_text = f"*{spec.product}*"
            product_analysis_text = ""
        
        user_instruction = (
            f"Ricerca e analizza le opportunità di espansione del mercato per {product_text} "
            f"sotto il brand *{spec.brand}* {budget_text}"
            f"**Dimensione Azienda:** {enterprise_size_it}\n\n"
            f"{product_analysis_text}"
            "Conduci una ricerca di mercato completa focalizzandoti su MERCATI EUROPEI E NON-EUROPEI:\n\n"
            "**ANALISI MERCATI EUROPEI:**\n"
            "- Paesi europei con maggiore potenziale (Germania, Francia, Regno Unito, Italia, Spagna, Paesi Bassi, Polonia, ecc.)\n"
            "- Ambiente normativo UE e requisiti di conformità (marcatura CE, GDPR, normative sulla sicurezza alimentare)\n"
            "- Comportamento del consumatore europeo e modelli di acquisto\n"
            "- Canali di distribuzione UE e reti di vendita al dettaglio\n"
            "- Opportunità di commercio transfrontaliero nel mercato unico UE\n"
            "- Panorama competitivo europeo e posizionamento di mercato\n"
            "- Opportunità di finanziamento UE e programmi di supporto\n\n"
            "**ANALISI MERCATI NON-EUROPEI:**\n"
            "- Mercati chiave non-europei (Nord America, Asia-Pacifico, America Latina, Medio Oriente, Africa)\n"
            "- Requisiti di ingresso nel mercato e quadri normativi fuori dall'Europa\n"
            "- Differenze culturali e comportamentali nei mercati non-europei\n"
            "- Canali di distribuzione internazionali e partnership\n"
            "- Considerazioni valutarie e rischi di cambio\n"
            "- Accordi commerciali e implicazioni tariffarie\n"
            "- Competizione locale e dinamiche di mercato\n\n"
            "**ANALISI COMPARATIVA:**\n"
            "- Identificazione e dimensionamento del mercato target (TAM, SAM, SOM) per mercati europei e non-europei\n"
            "- Analisi del panorama competitivo in tutte le regioni target\n"
            "- Confronto delle strategie di pricing e strutture dei costi\n"
            "- Tendenze tecnologiche e opportunità di innovazione a livello globale\n"
            "- Valutazione del rischio e strategie di mitigazione per l'espansione internazionale\n"
            "- Raccomandazioni di allocazione del budget tra mercati europei e non-europei\n\n"
            "Fornisci insights azionabili e raccomandazioni strategiche per un ingresso di successo nei mercati europei e non-europei.\n"
        )
    
    else:
        # Map enterprise size to English
        enterprise_size_map = {
            "small": "Small Enterprise",
            "medium": "Medium Enterprise",
            "large": "Big Enterprise"
        }
        enterprise_size_en = enterprise_size_map.get(spec.enterprise_size, spec.enterprise_size)
        
        # Handle empty or zero budget
        budget_text = ""
        if not spec.budget or spec.budget.strip() == "" or spec.budget == "0":
            budget_text = "**IMPORTANT:** The client has not specified a budget. Analyze the market and suggest an appropriate budget based on enterprise size, product, and target markets. Include a dedicated 'Budget Recommendations' section with detailed justification.\n\n"
        else:
            budget_text = f"with a total available budget of **{spec.budget}**.\n"
        
        # Handle multiple products
        products = [p.strip() for p in spec.product.split(',') if p.strip()]
        if len(products) > 1:
            product_text = f"the following products/services: {', '.join(products)}"
            product_analysis_text = f"""
**PRODUCT PORTFOLIO ANALYSIS:**
- **Primary Product/Service:** {products[0]}
- **Additional Products/Services:** {', '.join(products[1:])}
- **Portfolio Strategy:** Analyze each product individually and as a cohesive portfolio
- **Cross-selling Opportunities:** Identify synergies between products
- **Market Positioning:** How the product portfolio positions the brand in target markets
"""
        else:
            product_text = f"*{spec.product}*"
            product_analysis_text = ""
        
        user_instruction = (
            f"Research and analyze the market expansion opportunities for {product_text} "
            f"under the brand *{spec.brand}* {budget_text}"
            f"**Enterprise Size:** {enterprise_size_en}\n\n"
            f"{product_analysis_text}"
            "Conduct comprehensive market research focusing on BOTH European and non-European markets:\n\n"
            "**EUROPEAN MARKETS ANALYSIS:**\n"
            "- Target European countries with highest potential (Germany, France, UK, Italy, Spain, Netherlands, Poland, etc.)\n"
            "- EU regulatory environment and compliance requirements (CE marking, GDPR, food safety regulations)\n"
            "- European consumer behavior and purchasing patterns\n"
            "- EU distribution channels and retail networks (MANDATORY - provide detailed distribution analysis for EU countries)\n"
            "- Cross-border trade opportunities within the EU single market\n"
            "- European competitive landscape and market positioning\n"
            "- EU funding opportunities and support programs\n\n"
            "**NON-EUROPEAN MARKETS ANALYSIS:**\n"
            "- Key non-European markets (North America, Asia-Pacific, Latin America, Middle East, Africa)\n"
            "- Market entry requirements and regulatory frameworks outside Europe\n"
            "- Cultural and consumer behavior differences in non-European markets\n"
            "- International distribution channels and partnerships\n"
            "- Currency considerations and exchange rate risks\n"
            "- Trade agreements and tariff implications\n"
            "- Local competition and market dynamics\n\n"
            "**COMPARATIVE ANALYSIS:**\n"
            "- Target market identification and sizing (TAM, SAM, SOM) for both European and non-European markets\n"
            "- Competitive landscape analysis across all target regions\n"
            "- Pricing strategies and cost structures comparison\n"
            "- Technology trends and innovation opportunities globally\n"
            "- Risk assessment and mitigation strategies for international expansion\n"
            "- Budget allocation recommendations between European and non-European markets\n\n"
            "**IMPORTANT:** Ensure the Distribution Channels section includes detailed analysis for:\n"
            "- EU: Specific distribution channels, retail networks, and entry strategies for each target European country\n"
            "- North America: Distribution partnerships, retail chains, and market entry approaches\n"
            "- Asia-Pacific: Local distribution networks, cultural considerations, and partnership opportunities\n"
            "- Middle East: Modern trade groups, HORECA distributors, and market entry strategies\n"
            "- Other regions: Relevant distribution channels and market entry approaches\n\n"
            "Provide actionable insights and strategic recommendations for successful market entry in both European and non-European markets.\n"
        )
    
    # Add other information if provided (for both languages)
    if spec.other_info and spec.other_info.strip():
        if language == "it":
            other_info_section = f"""
**REQUISITI AGGIUNTIVI DEL CLIENTE:**
Il cliente ha fornito le seguenti domande specifiche o requisiti che devono essere affrontati nell'analisi:

{spec.other_info.strip()}

IMPORTANTE: Devi includere OBBLIGATORIAMENTE una sezione dedicata nel tuo report intitolata "Requisiti Aggiuntivi del Cliente" o "Altre Informazioni" che affronti specificamente questi requisiti. Questa sezione deve apparire verso la fine del tuo report, prima della conclusione.
"""
        else:
            other_info_section = f"""
**ADDITIONAL CLIENT REQUIREMENTS:**
The client has provided the following specific questions or requirements that should be addressed in the analysis:

{spec.other_info.strip()}

IMPORTANT: You MUST include a dedicated section in your report titled "Additional Client Requirements" or "Other Information" that specifically addresses these requirements. This section should appear near the end of your report, before the conclusion.
"""
        user_instruction += other_info_section

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
   - **Market Overview** (MANDATORY - provide general market insights)
   - **Target Market Analysis** (MANDATORY - include TAM, SAM, SOM estimates)
   - **Competitive Landscape** (MANDATORY - identify key competitors)
   - **Regulatory Environment** (MANDATORY - include relevant regulations)
   - **Consumer Analysis** (MANDATORY - provide consumer insights)
   - **Distribution Channels** (MANDATORY - detail distribution strategies)
   - **Financial Projections** (MANDATORY - include budget recommendations)
   - **Risk Assessment** (MANDATORY - identify key risks)
   - **Strategic Recommendations** (MANDATORY)
   - **Implementation Plan** (90-day action plan - MANDATORY)
   - **Sources & References** (MANDATORY)

3. **Data Quality Standards**
   - Provide comprehensive analysis for all sections
   - Use market research and industry knowledge to fill gaps
   - Clearly label all estimates with "(Estimate)" and reasoning
   - Include relevant insights even if specific data is limited
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

10. **Market Research Focus Areas** (MANDATORY - provide comprehensive analysis)
   - **European Markets:** Current market sizes and growth rates in key EU countries
   - **Non-European Markets:** Market potential in North America, Asia-Pacific, Latin America, Middle East, Africa
   - **Regulatory Environment:** EU regulations (CE marking, GDPR, food safety) vs. international compliance requirements
   - **Consumer Behavior:** European vs. non-European consumer patterns and cultural differences
   - **Distribution Channels:** EU single market opportunities vs. international distribution networks
   - **Competitive Positioning:** European competitors vs. global market leaders
   - **Pricing Strategies:** EU pricing structures vs. international pricing models
   - **Technology Trends:** European innovation hubs vs. global technology opportunities
   - **Trade Agreements:** EU trade benefits vs. international trade agreements and tariffs
   - **Currency Considerations:** Euro stability vs. international currency risks
"""
    
    # Use the standard chat completion API
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
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        # Return a more helpful error message
        return f"Error generating report: {str(e)}. Please try again or contact support."
