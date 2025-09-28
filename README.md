# AI Trade Report Generator

A professional, multilingual AI-powered market analysis generator that creates comprehensive trade reports using OpenAI's GPT-5. Built with FastAPI and featuring a modern, mobile-responsive web interface.

## 🚀 Features

### Core Functionality

- **AI-Powered Analysis**: Uses OpenAI GPT-5 for intelligent market analysis
- **Multilingual Support**: English and Italian language options
- **Professional Reports**: Generates comprehensive HTML reports with market insights
- **PDF Export**: Download reports as PDF with professional formatting
- **Print Support**: Print-friendly report layouts
- **Mobile Responsive**: Fully optimized for desktop, tablet, and mobile devices

### User Experience

- **Language Selection Modal**: Choose language on first visit (no cookies stored)
- **Modern UI/UX**: Professional design with gradient backgrounds and animations
- **Loading Animation**: Engaging splash screen during report generation
- **Touch-Friendly**: Optimized for mobile and touch devices
- **Real-time Translation**: Dynamic UI translation based on language selection

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Modern web browser

## 🛠️ Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**

   ```bash
   git clone https://github.com/tkani/AI_Trade_Report.git
   cd AI_Trade_Report
   ```

2. **Set up environment variables**
   Copy the example environment file and add your API keys:

   ```bash
   cp .env_example .env
   # Edit .env with your actual API keys
   ```

3. **Run with Docker**

   ```bash
   # Make setup script executable
   chmod +x docker-setup.sh
   
   # Run setup (builds and starts the application)
   ./docker-setup.sh
   ```

4. **Test the application**

   ```bash
   # Make test script executable
   chmod +x docker-test.sh
   
   # Run tests
   ./docker-test.sh
   ```

### Option 2: Local Python Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/tkani/AI_Trade_Report.git
   cd AI_Trade_Report
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Copy the example environment file and add your OpenAI API key:

   ```bash
   cp .env_example .env
   ```

   Then edit `.env` and add your actual OpenAI API key:

   ```env
   OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here
   ```

4. **Run the application**

   ```bash
   uvicorn app:app --reload
   ```

5. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:8000`

6. **View FastAPI Documentation**
   - **Interactive API Docs (Swagger UI)**: `http://127.0.0.1:8000/docs`
   - **Alternative API Docs (ReDoc)**: `http://127.0.0.1:8000/redoc`
   - **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

## 📁 Project Structure

```
AI_Trade_Report/
├── app.py                      # FastAPI backend application
├── generate_prompt.py          # AI prompt generation and OpenAI integration
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── templates/
│   └── index.html              # Main frontend page
├── static/
│   ├── css/
│   │   └── style.css           # Styling and responsive design
│   └── js/
│       └── main.js             # Frontend JavaScript functionality
└── reports/                    # Generated report storage directory
```

## 🎯 Usage

### Docker Usage (Recommended)

1. **Start the application**

   ```bash
   # Using Docker Compose
   docker-compose up -d
   
   # Or using the setup script
   ./docker-setup.sh
   ```

2. **Open your browser**

   Navigate to `http://localhost:8000`

3. **Useful Docker Commands**

   ```bash
   # View logs
   docker-compose logs -f
   
   # Stop application
   docker-compose down
   
   # Restart application
   docker-compose restart
   
   # Test email functionality
   docker-compose exec ai-trade-report python test_hosted_email.py
   
   # Test OpenAI API
   docker-compose exec ai-trade-report python test_openai_api.py
   
   # Run all tests
   ./docker-test.sh
   ```

### Local Python Usage

1. **Start the application**

   ```bash
   python run_server.py
   ```

2. **Open your browser**

   Navigate to `http://127.0.0.1:8000`

### Application Usage

### 1. Language Selection

- On first visit, select your preferred language (English/Italian)
- Language preference is not stored (no cookies)
- UI and generated reports will be in the selected language

### 2. Generate Report

1. Enter your **Brand Name**
2. Describe your **Product/Service**
3. Specify your **Investment Budget**
4. Select **AI Model** (GPT-5 by default)
5. Click **Generate Report**

### 3. View and Download

- Report opens in a new page with professional formatting
- Use **Print** button to print the report
- Use **Download PDF** button to save as PDF
- Reports are fully mobile-responsive

## 🔧 Technical Details

### Backend (FastAPI)

- **Framework**: FastAPI with Jinja2Templates
- **AI Integration**: OpenAI GPT-5 API
- **Report Generation**: HTML with embedded CSS and JavaScript
- **File Handling**: Static file serving and report storage

### Frontend

- **HTML5**: Semantic markup with accessibility features
- **CSS3**: Modern styling with Flexbox and Grid
- **JavaScript**: jQuery for AJAX and DOM manipulation
- **Responsive Design**: Mobile-first approach with media queries

### AI Integration

- **Model**: OpenAI GPT-5 (latest generation)
- **API Pattern**: Uses `client.responses.create` for research tasks
- **Prompt Engineering**: Structured prompts for professional reports
- **Error Handling**: Robust fallback mechanisms

## 🤖 OpenAI Integration Details

### How It Works

#### 1. **API Configuration**

The application uses OpenAI's latest GPT-5 model through the Research API pattern:

```python
# Uses client.responses.create for research tasks
response = client.responses.create(
    model="gpt-5",
    input=user_input,
    instructions=system_instructions
)
```

#### 2. **Prompt Engineering Strategy**

The system uses a sophisticated two-part prompt structure:

**System Preamble** (English/Italian):

- Establishes the AI as a senior strategy consultant with 30+ years experience
- Sets professional tone and expertise level
- Defines output format requirements (headings, tables, bullet points)
- Emphasizes data integrity and transparency

**User Instruction** (Dynamic):

- Incorporates user's brand, product, and budget information
- Requests specific report structure and analysis
- Includes current date for temporal context
- Asks for JSON metadata with market recommendations

#### 3. **Output Processing**

The AI generates comprehensive reports that include:

- **Executive Summary**: Key findings and strategic recommendations
- **Market Analysis**: TAM, SAM, SOM estimates with clear labeling
- **Competitive Landscape**: Industry analysis and positioning
- **Strategic Recommendations**: Actionable business advice
- **Investment Breakdown**: Budget allocation suggestions
- **Risk Assessment**: Potential challenges and mitigation strategies
- **90-Day Action Plan**: Immediate next steps
- **Sources & Appendix**: Data sources and assumptions

#### 4. **Content Transformation**

The raw AI output is processed through a markdown-to-HTML converter that:

- Converts markdown headers to HTML headings
- Transforms tables to responsive HTML tables
- Converts lists to properly formatted HTML lists
- Applies professional styling and mobile responsiveness
- Adds interactive elements (print, PDF download)

#### 5. **Multilingual Support**

- **English**: Full professional business language
- **Italian**: Complete translation of UI and report content
- **Dynamic Translation**: Language selection affects both UI and AI prompts
- **Cultural Adaptation**: Prompts adapted for different business cultures

### API Key Setup

1. **Get OpenAI API Key**:

   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Sign up or log in to your account
   - Create a new API key
   - Copy the key (starts with `sk-proj-`)

2. **Configure Environment**:

   ```bash
   # Copy the example file
   cp .env_example .env

   # Edit .env and add your key
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```

3. **Verify Setup**:
   - Start the application: `uvicorn app:app --reload`
   - Generate a test report to verify API connectivity

### Cost Considerations

- **GPT-5 Pricing**: Check current pricing at [OpenAI Pricing](https://openai.com/pricing)
- **Token Usage**: Reports typically use 2000-4000 tokens
- **Rate Limits**: Respect OpenAI's rate limits for your plan
- **Monitoring**: Check your usage in the OpenAI dashboard

### Error Handling

The system includes robust error handling:

- **API Failures**: Graceful fallback with user-friendly messages
- **Rate Limits**: Automatic retry with exponential backoff
- **Invalid Keys**: Clear error messages for configuration issues
- **Network Issues**: Timeout handling and retry logic

## 📱 Mobile Responsiveness

### Breakpoints

- **Desktop**: 1200px and above
- **Tablet**: 768px - 1199px
- **Mobile**: 480px - 767px
- **Small Mobile**: Below 480px

### Mobile Features

- Touch-friendly button sizes (minimum 44px)
- Horizontal scrolling for tables
- Optimized typography and spacing
- Landscape orientation support
- Swipe-friendly navigation

## 🌐 Multilingual Support

### Supported Languages

- **English** (default)
- **Italian** (Italiano)

### Translation Coverage

- Complete UI translation
- Report content generation
- Form labels and placeholders
- Error messages and notifications
- Print and download buttons

## 📊 Report Features

### Report Structure

- **Executive Summary**: Key findings and recommendations
- **Market Analysis**: Comprehensive market insights
- **Competitive Landscape**: Industry analysis
- **Strategic Recommendations**: Actionable business advice
- **Investment Breakdown**: Budget allocation suggestions
- **Risk Assessment**: Potential challenges and mitigations

### Report Formatting

- Professional typography with Inter font family
- Responsive tables with horizontal scrolling
- Color-coded sections and highlights
- Print-optimized layouts
- PDF generation with proper page breaks

## 🔒 Security & Privacy

- **No Data Storage**: Reports are generated on-demand
- **No Cookies**: Language preference not persisted
- **API Security**: OpenAI API key stored in environment variables
- **Input Validation**: Server-side validation of all inputs

## 🚀 Deployment

### Local Development

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment

1. Set up a production WSGI server (e.g., Gunicorn)
2. Configure reverse proxy (e.g., Nginx)
3. Set up SSL certificates
4. Configure environment variables
5. Set up monitoring and logging

## 📝 API Endpoints

### Main Routes

- `GET /` - Main application page
- `POST /generate` - Generate AI report
- `GET /download/{filename}` - Download generated report

## 📚 FastAPI Documentation

### Interactive API Documentation

FastAPI automatically generates interactive API documentation:

#### 1. **Swagger UI** (Recommended)

- **URL**: `http://127.0.0.1:8000/docs`
- **Features**:
  - Interactive API testing
  - Request/response examples
  - Schema validation
  - Try-it-out functionality
  - Authentication testing

#### 2. **ReDoc** (Alternative)

- **URL**: `http://127.0.0.1:8000/redoc`
- **Features**:
  - Clean, readable documentation
  - Better for reading and understanding
  - Schema-focused view
  - Print-friendly format

#### 3. **OpenAPI Schema**

- **URL**: `http://127.0.0.1:8000/openapi.json`
- **Features**:
  - Raw OpenAPI 3.0 specification
  - Machine-readable format
  - Integration with other tools
  - API client generation

### Using the Interactive Docs

1. **Start the application**:

   ```bash
   uvicorn app:app --reload
   ```

2. **Open Swagger UI**:

   - Navigate to `http://127.0.0.1:8000/docs`
   - You'll see all available endpoints

3. **Test the API**:

   - Click on any endpoint to expand it
   - Click "Try it out" button
   - Fill in the required parameters
   - Click "Execute" to test the endpoint
   - View the response in real-time

4. **Example API Test**:
   - **Endpoint**: `POST /generate`
   - **Parameters**:
     ```json
     {
       "brand": "Test Brand",
       "product": "Test Product",
       "budget": "€100,000",
       "ai_model": "gpt-5",
       "language": "en"
     }
     ```

### API Response Examples

#### Successful Report Generation

```json
{
  "status": "success",
  "redirect_url": "/reports/report_20241204_143022.html"
}
```

#### Error Response

```json
{
  "status": "error",
  "message": "OpenAI API key not configured"
}
```

### Request Format

```json
{
  "brand": "Your Brand Name",
  "product": "Product/Service Description",
  "budget": "Investment Budget",
  "ai_model": "gpt-5",
  "language": "en"
}
```

### Response Format

```json
{
  "status": "success",
  "redirect_url": "/reports/report_filename.html"
}
```

## 🛠️ Development

### Adding New Languages

1. Update `translations` object in `static/js/main.js`
2. Add language options to `templates/index.html`
3. Update `build_prompt` function in `generate_prompt.py`
4. Add translations to `create_html_document` in `app.py`

### Customizing Report Format

1. Modify `create_html_document` function in `app.py`
2. Update CSS styles in the embedded `<style>` block
3. Adjust mobile responsive breakpoints as needed

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**: Ensure `.env` file exists with valid API key
2. **PDF Generation Issues**: Check browser console for JavaScript errors
3. **Mobile Display Problems**: Clear browser cache and test on different devices
4. **Language Not Changing**: Hard refresh the page (Ctrl+F5)

### Debug Mode

Enable debug logging by setting environment variable:

```bash
export DEBUG=1
uvicorn app:app --reload
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support, email support@example.com or create an issue in the GitHub repository.

## 🙏 Acknowledgments

- OpenAI for providing the GPT-5 API
- FastAPI team for the excellent web framework
- The open-source community for various libraries and tools

---

**Built with ❤️ for professional market analysis**
