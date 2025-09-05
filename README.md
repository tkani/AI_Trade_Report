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
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application**
   ```bash
   uvicorn app:app --reload
   ```

5. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:8000`

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
