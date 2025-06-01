# 🧠 RAG Demo - Knowledge Graph Extraction

A demonstration application that converts documents into interactive knowledge graphs, visually displaying entities, relationships, and embeddings in an educational and interactive way.

## 🌟 Key Features

### 🔐 Secure Access
- **Authentication System**: Login required to access the application
- **Session Management**: Secure Flask sessions with automatic logout
- **User Management**: Admin account with expandable user system

### 📄 Intelligent Document Processing
- **Advanced OCR**: Support for PDF, DOCX, images using Docling and Tesseract
- **URL Processing**: Web content and online PDF extraction
- **Semantic Chunking**: Intelligent text division for better processing

### 🕸️ Knowledge Graph Generation
- **Automatic Extraction**: Entity and relationship identification using LLMs
- **Interactive Visualization**: Navigable graphs with Cytoscape.js
- **Dynamic Legend**: Automatically adapts to processed content

### 🧮 Embedding Analysis
- **Vectorization**: Text to embeddings conversion with OpenAI
- **Storage**: Vector database with Pinecone
- **Educational Visualization**: Shows real numerical values of embeddings

### 🎨 Modern Interface
- **Responsive Design**: Optimized for desktop and mobile
- **Dark Theme**: Professional interface with visual effects
- **Interactive Components**: Dropdowns, information panels and intuitive controls

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js (for some components)
- OpenAI and Pinecone API keys

### Installation

1. **Clone repository**
```bash
git clone <repository-url>
cd rag-demo-knowledge-graph
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and authentication settings
```

4. **Run application**
```bash
python app.py
```

5. **Access application**
```
http://127.0.0.1:8080/
```

6. **Login**
- Use the admin credentials you configured in `.env`
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

# Optional configuration
LLM_DEFAULT=openai
```

### Generate Flask Secret Key

**For Linux/Mac:**
```bash
python -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"
```

**For Windows:**
```bash
python -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"
```

### Pinecone Setup

1. Create account at [Pinecone](https://www.pinecone.io/)
2. Create an index with dimension `1536` (for OpenAI embeddings)
3. Copy API key and configuration to `.env`

## 📖 Usage

### 1. Authentication
- **Access application** at your configured URL
- **Login** with admin credentials from `.env`
- **Session** remains active for 10 minutes of inactivity

### 2. Upload Document
- **Drag and drop** PDF, DOCX or image files
- **Paste URL** of web documents or online PDFs
- Select processing method (Docling/Tesseract)

### 3. Configure Processing
- **Text processor**: Docling (recommended) or Tesseract
- **LLM Model**: OpenAI GPT-4o or Claude Sonnet 4

### 4. Explore Results
- **Interactive graph**: Navigation, zoom, node selection
- **Statistics panel**: Entity and relationship counters
- **Dynamic legend**: Types present in current document

### 5. Analyze Embeddings
- **Click** on any graph node
- **View embeddings**: Numerical values representing the concept
- **Understand AI**: Educational explanation of how they work

### 6. Session Management
- **Logout**: Use "Cerrar Sesión" link in top-right corner
- **Auto-logout**: Sessions expire after 10 minutes of inactivity

## 🏗️ Architecture

### Project Structure

```
├── app.py                  # Main entry point with authentication
├── components/             # UI components
│   ├── graph_view.py      # Graph visualization
│   ├── upload_component.py # File upload
│   ├── ocr_selector.py    # OCR selector
│   ├── llm_selector.py    # LLM selector
│   └── progress_bar.py    # Progress bar
├── callbacks/             # Dash callback logic
│   ├── graph_callbacks.py # Graph callbacks
│   ├── ocr_callbacks.py   # Document processing
│   ├── llm_callbacks.py   # LLM extraction
│   └── embedding_callbacks.py # Embedding management
├── core/                  # Business logic
│   ├── auth.py           # Authentication system
│   ├── ocr.py            # OCR processing
│   ├── llm.py            # LLM integration
│   ├── embeddings.py     # Vector management
│   ├── graph_builder.py  # Graph construction
│   └── utils.py          # General utilities
├── data/                 # User data (created automatically)
│   └── users.json       # User credentials (hashed)
├── assets/               # Static resources
│   └── style.css        # Custom styles
└── requirements.txt     # Python dependencies
```

### Data Flow

1. **Authentication** → User login verification
2. **Upload** → Document/URL input by user
3. **Extraction** → OCR converts to plain text
4. **Chunking** → Semantic text division
5. **Vectorization** → Embedding generation
6. **Analysis** → LLM extracts entities and relationships
7. **Visualization** → Interactive graph construction

## 🛠️ Technologies Used

### Backend
- **Dash**: Python web framework
- **Flask**: Underlying web server with session management
- **Docling**: Advanced document OCR
- **PyTesseract**: Backup OCR
- **LangChain**: Semantic chunking

### AI and ML
- **OpenAI GPT-4o**: Entity extraction
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
- **CSS Custom**: Modern dark theme

## 🎯 Use Cases

### Educational
- **Demonstrate AI**: Show how embeddings work
- **Text Analysis**: Visualize document relationships
- **NLP Understanding**: See step-by-step processing

### Professional
- **Document Analysis**: Extract knowledge from reports
- **Concept Mapping**: Visualize complex relationships
- **RAG Prototyping**: Base for more complex systems

### Research
- **Graph Exploration**: Analyze knowledge structures
- **LLM Comparison**: Evaluate different models
- **Embedding Optimization**: Experiment with vectorization

## 🔧 Customization

### Add New Users

The system is designed for expansion. You can modify `core/auth.py` to add user management features:

```python
# Example: Add user programmatically
from core.auth import auth_manager
success, message = auth_manager.add_user("newuser", "password123")
```

### Add New Entity Types

1. Modify prompt in `core/llm.py`
2. Update colors in `components/graph_view.py`
3. Add mapping in `callbacks/graph_callbacks.py`

### Integrate Other LLMs

1. Create function in `core/llm.py`
2. Add option in `components/llm_selector.py`
3. Register in corresponding callbacks

### Change Visual Styles

- Edit `assets/style.css` for themes
- Modify `working_stylesheet` in `graph_view.py` for nodes
- Customize colors in `create_dynamic_legend()`


## 🔒 Security Notes

- **Passwords**: Stored as SHA-256 hashes, never in plain text
- **Sessions**: Expire after 10 minutes of inactivity
- **Keys**: Keep API keys and secret keys secure
- **Production**: Always use strong passwords and secret keys in production

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License. See `LICENSE` file for details.

---

**Secure knowledge exploration! 🔐🚀**