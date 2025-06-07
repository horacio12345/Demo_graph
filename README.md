# 🧠 RAG Demo - Knowledge Graph Extraction & Conversational AI

An advanced demonstration application that combines knowledge graph extraction with a conversational RAG (Retrieval-Augmented Generation) chat system. It processes documents, visualizes entities and relationships interactively, and enables intelligent queries about the content.

## 🌟 Key Features

### 🔐 Secure Access
- **Authentication System**: Login required with Flask session management
- **Session Management**: Temporary sessions with automatic logout (30 minutes)
- **User Administration**: Admin account expandable to multiple users

### 📄 Intelligent Document Processing
- **Advanced OCR**: Support for PDF, DOCX, images using Docling and Tesseract
- **URL Processing**: Web content and online PDF extraction
- **Semantic Chunking**: Intelligent text division for better processing
- **Vector Database**: Storage in Pinecone for semantic searches

### 🕸️ Knowledge Graph Generation
- **Automatic Extraction**: Entity and relationship identification using LLMs
- **Interactive Visualization**: Navigable graphs with Cytoscape.js
- **Dynamic Legend**: Automatically adapts to processed content
- **Database Generation**: Create graphs from stored documents

### 🤖 Conversational RAG System
- **Intelligent Chat**: Conversational interface to query documents
- **Educational Process**: Step-by-step visualization of RAG pipeline
- **Multiple LLMs**: Support for OpenAI GPT-4o and Claude Sonnet 4
- **Semantic Context**: Automatic search and context construction

### 🧮 Embedding Analysis
- **Vectorization**: Text to embeddings conversion with OpenAI
- **Storage**: Vector database with Pinecone
- **Educational Visualization**: Shows real numerical values of embeddings
- **Semantic Search**: Information retrieval based on similarity

### 🎨 Modern Interface
- **Responsive Design**: Optimized for desktop and mobile
- **Dark Theme**: Professional interface with visual effects
- **Multi-Page Navigation**: Graph processing and conversational chat
- **Interactive Components**: Dropdowns, information panels, and intuitive controls

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **System Dependencies**: `tesseract-ocr`, `poppler-utils`
- **API Keys**: OpenAI, Pinecone, and optionally Anthropic

### Installation

1. **Clone repository**
```bash
git clone <repository-url>
cd rag-demo-knowledge-graph
```

2. **Install system dependencies**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr poppler-utils

# macOS
brew install tesseract poppler

# Windows
# Download and install manually from official sites
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and authentication settings
```

5. **Run application**
```bash
python app.py
```

6. **Access application**
```
http://localhost:8080/
```

7. **Login**
- Use the admin credentials configured in `.env`
- Default: username `admin` with your chosen password

## ⚙️ Configuration

### Required Environment Variables

```env
# Authentication (Required)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
FLASK_SECRET_KEY=your_flask_secret_key

# OpenAI API (Required)
OPENAI_API_KEY=your_openai_key

# Pinecone (Required for embeddings)
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=index_name

# Anthropic API (Optional for Claude)
ANTHROPIC_API_KEY=your_anthropic_key

# Optional configuration
LLM_DEFAULT=openai
```

### Generate Flask Secret Key

**For all platforms:**
```bash
python -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"
```

### Pinecone Setup

1. Create account at [Pinecone](https://www.pinecone.io/)
2. Create an index with dimension `1536` (for OpenAI embeddings)
3. Copy API key and configuration to `.env`

## 📖 Usage

### 1. Authentication
- **Access** application at configured URL
- **Login** with admin credentials from `.env`
- **Session** remains active for 30 minutes of inactivity

### 2. Main Page - Processing and Graphs (`/`)

#### Upload Document
- **Drag and drop** PDF, DOCX or image files
- **Paste URL** of web documents or online PDFs
- Select processing method (Docling/Tesseract)

#### Configure Processing
- **Text processor**: Docling (recommended) or Tesseract
- **LLM Model**: OpenAI GPT-4o or Claude Sonnet 4

#### Explore Results
- **Interactive graph**: Navigation, zoom, node selection
- **Statistics panel**: Entity and relationship counters
- **Dynamic legend**: Types present in current document
- **Generate from DB**: Create graphs from stored documents

#### Analyze Embeddings
- **Click** on any graph node
- **View embeddings**: Numerical values representing the concept
- **Understand AI**: Educational explanation of how they work

### 3. RAG Chat Page (`/chat`)

#### Ask Questions
- **Write queries** about processed documents
- **Select LLM**: OpenAI GPT-4o or Claude Sonnet 4
- **Send question** and receive contextualized response

#### Educational Process
- **Step-by-step visualization** of RAG pipeline:
  1. **Vectorization**: Question to embedding conversion
  2. **Search**: Find similar fragments
  3. **Context**: Relevant context construction
  4. **Generation**: LLM response creation
- **Detailed statistics** for each step
- **Source information** used

#### Session Management
- **Logout**: Use "Cerrar Sesión" link in top-right corner
- **Auto-logout**: Sessions expire after 30 minutes of inactivity

## 🏗️ Architecture

### Project Structure

```
├── app.py                     # Main entry point with authentication
├── agent/                     # Conversational RAG system
│   ├── __init__.py
│   ├── chat_page.py          # Chat page layout
│   ├── search.py             # Semantic search
│   ├── context.py            # Context building
│   ├── response.py           # LLM response generation
│   └── prompts.yaml          # Configurable prompts
├── components/                # UI components
│   ├── chat_interface.py     # Chat interface with Markdown
│   ├── rag_process_panel.py  # Educational RAG process panel
│   ├── graph_view.py         # Graph visualization
│   ├── upload_component.py   # File upload
│   ├── ocr_selector.py       # OCR selector
│   ├── llm_selector.py       # LLM selector
│   └── progress_bar.py       # Progress bar
├── callbacks/                 # Dash callback logic
│   ├── chat_callbacks.py     # Chat system callbacks
│   ├── graph_callbacks.py    # Graph callbacks
│   ├── ocr_callbacks.py      # Document processing
│   ├── llm_callbacks.py      # LLM extraction
│   └── embedding_callbacks.py # Embedding management
├── core/                      # Business logic
│   ├── auth.py               # Authentication system
│   ├── rag_orchestrator.py   # RAG pipeline coordinator
│   ├── ocr.py                # OCR processing
│   ├── llm.py                # LLM integration
│   ├── embeddings.py         # Vector management
│   ├── graph_builder.py      # Graph construction
│   └── utils.py              # General utilities
├── data/                      # User data (created automatically)
│   └── users.json            # User credentials (hashed)
├── assets/                    # Static resources
│   └── style.css             # Custom styles
└── requirements.txt          # Python dependencies
```

### Data Flow

#### Document Processing Pipeline
1. **Authentication** → User login verification
2. **Upload** → Document/URL input by user
3. **Extraction** → OCR converts to plain text
4. **Chunking** → Semantic text division
5. **Vectorization** → Embedding generation
6. **Analysis** → LLM extracts entities and relationships
7. **Visualization** → Interactive graph construction

#### Conversational RAG Pipeline
1. **Question** → User input in chat interface
2. **Vectorization** → Question to embedding conversion
3. **Search** → Similar chunks retrieval from Pinecone
4. **Context** → Relevant context construction
5. **LLM** → Context-based response generation
6. **Visualization** → Educational process presentation

## 🛠️ Technologies Used

### Backend
- **Dash**: Python web framework
- **Flask**: Underlying web server with session management
- **Docling**: Advanced document OCR
- **PyTesseract**: Backup OCR
- **LangChain**: Semantic chunking and text processing

### AI and ML
- **OpenAI GPT-4o**: Entity extraction and response generation
- **Claude Sonnet 4**: Alternative LLM
- **OpenAI Embeddings**: Text vectorization
- **Pinecone**: Vector database

### Security
- **Flask Sessions**: Secure session management
- **SHA-256 Hashing**: Password security
- **Environment Variables**: Secure configuration

### Frontend
- **Dash Cytoscape**: Graph visualization
- **Dash Bootstrap Components**: UI components
- **Plotly**: Interactive charts
- **CSS Custom**: Modern dark theme with visual effects

## 🎯 Use Cases

### Educational
- **Demonstrate AI**: Show how embeddings and RAG work
- **Text Analysis**: Visualize document relationships
- **NLP Understanding**: See step-by-step processing

### Professional
- **Document Analysis**: Extract knowledge from reports
- **Concept Mapping**: Visualize complex relationships
- **RAG Prototyping**: Base for more complex systems
- **Intelligent Consultation**: Conversational chat about corporate documents

### Research
- **Graph Exploration**: Analyze knowledge structures
- **LLM Comparison**: Evaluate different models
- **Embedding Optimization**: Experiment with vectorization
- **RAG Study**: Understand retrieval-augmented pipelines

## 🔧 Customization

### Add New Users

The system is designed for expansion. You can modify `core/auth.py` to add user management features:

```python
# Example: Add user programmatically
from core.auth import auth_manager
success, message = auth_manager.add_user("newuser", "password123")
```

### Add New Entity Types

1. Modify prompt in `agent/prompts.yaml`
2. Update colors in `components/graph_view.py`
3. Add mapping in `callbacks/graph_callbacks.py`

### Integrate Other LLMs

1. Create function in `agent/response.py`
2. Add option in `components/llm_selector.py`
3. Register in corresponding callbacks

### Change Visual Styles

- Edit `assets/style.css` for themes
- Modify `working_stylesheet` in `graph_view.py` for nodes
- Customize colors in `create_dynamic_legend()`

### Configure RAG Prompts

- Edit `agent/prompts.yaml` to customize LLM behavior
- Modify templates for different query types
- Adjust temperature and length parameters

## 🔒 Security Notes

- **Passwords**: Stored as SHA-256 hashes, never in plain text
- **Sessions**: Expire after 30 minutes of inactivity
- **Keys**: Keep API keys and secret keys secure
- **Production**: Always use strong passwords and secret keys in production
- **Environment Variables**: Never commit `.env` files to repository

## 🚀 Production Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Environment variables
ENV PYTHONPATH=/app
ENV DASH_DEBUG=False

# Start command
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "120", "--workers", "2", "app:server"]
```

### Railway/Heroku

The application includes:
- `Procfile` for Railway/Heroku
- `nixpacks.toml` for automatic configuration
- Optimized `requirements.txt`

### Production Environment Variables

Make sure to configure all required variables in your deployment platform:

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong-password>
FLASK_SECRET_KEY=<generated-secret-key>
OPENAI_API_KEY=<your-api-key>
PINECONE_API_KEY=<your-api-key>
PINECONE_INDEX=<index-name>
ANTHROPIC_API_KEY=<your-optional-api-key>
```

## 📝 Interface Language Note

The user interface is currently in Spanish, including:
- Navigation elements ("Agente RAG Conversacional", "Haz tu pregunta")
- Status messages and labels
- Chat interface text

This is intentional for the target audience, while maintaining English documentation for international developers.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License. See `LICENSE` file for details.

---

**Secure and conversational knowledge exploration! 🔐🤖🚀**