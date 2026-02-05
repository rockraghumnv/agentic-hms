# Personalized AI Healthcare Assistant Chatbot

A hospital-based healthcare chatbot that provides personalized medical guidance by analyzing patient medical history. Features autonomous health monitoring, predictive wellness alerts, and explainable AI.

## 🏥 Features

- **Medical Document Explainer**: Upload medical reports (images), get explanations in Kannada or Simple English
- **Personalized Health Answers**: AI analyzes your medical history for context-aware responses
- **Smart Health Timeline**: Visual timeline of your health journey with pattern detection
- **Predictive Wellness Alerts**: Proactive screening suggestions and medication refill reminders
- **Autonomous Appointment Booking**: Auto-detects severe conditions and suggests doctor appointments
- **Explainable AI**: See exactly how AI arrived at each response

## 🛠️ Tech Stack

**Frontend**: HTML, CSS, JavaScript  
**Backend**: FastAPI, Python  
**AI**: Gemini-2.5-flash with Vision API  
**Vector DB**: ChromaDB  
**Architecture**: MCP (Model Context Protocol) Client/Server  
**Agents**: Agent Development Kit (ADK)

## 📋 Prerequisites

- Python 3.9 or higher
- Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))
- 2GB free disk space

## 🚀 Quick Start

### 1. Clone and Setup

```powershell
# Navigate to project directory
cd e:\srp

# Run setup script (Windows PowerShell)
.\setup.sh

# Or manually:
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure Environment

```powershell
# Copy example environment file
copy .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_actual_key_here
```

### 3. Run the Application

```powershell
# Make sure venv is activated
venv\Scripts\Activate.ps1

# Start backend server
python backend/main.py

# Open browser to:
# http://localhost:8000
```

## 📁 Project Structure

```
srp/
├── backend/              # FastAPI backend
│   ├── main.py          # Main API server
│   ├── gemini_vision.py # OCR processing
│   ├── chat_handler.py  # Chat logic
│   └── vector_store.py  # ChromaDB interface
├── frontend/            # HTML/CSS/JS UI
│   ├── upload.html      # Document upload portal
│   └── chatbot.html     # Chat interface
├── agents/              # Autonomous agents
│   └── health_monitor_agent.py
├── mcp/                 # MCP server/client
│   ├── server.py
│   └── client.py
├── tests/               # Automated tests
└── requirements.txt     # Python dependencies
```

## 📊 Phase Implementation Status

- [ ] Phase 1: Project setup & environment ✅
- [ ] Phase 2: Upload portal with Gemini Vision OCR
- [ ] Phase 3: ChromaDB storage & Gemini parser
- [ ] Phase 4: Chatbot interface with medical Q&A
- [ ] Phase 5: Explainable AI transparency feature
- [ ] Phase 6: MCP server & client architecture
- [ ] Phase 7: Autonomous appointment booking
- [ ] Phase 8: Health timeline visualization
- [ ] Phase 9: Autonomous health monitoring agent

## 🧪 Testing

```powershell
# Run automated tests
pytest tests/ -v

# Run specific phase tests
pytest tests/test_phase1.py -v
```

## 🔒 Privacy & Security

- All medical data stored locally in ChromaDB
- No data sent to external servers except Gemini API for processing
- Unique patient IDs for secure access
- Consent required before data processing

## 📝 Usage Flow

1. **Upload Medical Documents**: User uploads medical images (lab reports, prescriptions)
2. **Fill Family History**: Answer general health questions about family
3. **Get Unique ID**: System generates patient ID (e.g., PT-2026-A7B3)
4. **Chat Interface**: Enter ID and ask health questions
5. **Autonomous Alerts**: System proactively suggests screenings and medication refills
6. **Book Appointments**: AI detects severe conditions and suggests booking

## 🤝 Demo Features

This is a demo project using:
- Mock hospital database
- Mock doctor appointments
- Simulated medication refill alerts

## 📄 License

This is an educational project for demonstration purposes.

## 🆘 Troubleshooting

**Issue**: `ModuleNotFoundError`
- **Solution**: Ensure venv is activated and dependencies installed

**Issue**: Gemini API errors
- **Solution**: Verify API key in .env is correct

**Issue**: ChromaDB connection errors
- **Solution**: Delete `chroma_db/` folder and restart

## 📧 Support

For issues or questions, check the phase-by-phase implementation plan in the repository.
