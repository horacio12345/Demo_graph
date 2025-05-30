# 🧠 RAG Demo - Knowledge Graph Extraction

A demonstration application that converts documents into interactive knowledge graphs, visually displaying entities, relationships, and embeddings in an educational and interactive way.

## 🌟 Key Features

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
# Edit .env with your API keys
```

4. **Run application**
```bash
python app.py
```

5. **Open in browser**
```
http://127.0.0.1:8050/
```

## ⚙️ Configuration

### Required Environment Variables

```env
# OpenAI API
OPENAI_API_KEY=your_openai_key

# Pinecone (Vector database)
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=index_name
PINECONE_ENV=your_pinecone_environment

# Optional configuration
LLM_DEFAULT=openai
```

### Pinecone Setup

1. Create account at [Pinecone](https://www.pinecone.io/)
2. Create an index with dimension `1536` (for OpenAI embeddings)
3. Copy API key and configuration to `.env`

## 📖 Usage

### 1. Upload Document
- **Drag and drop** PDF, DOCX or image files
- **Paste URL** of web documents or online PDFs
- Select processing method (Docling/Tesseract)

### 2. Configure Processing
- **Text processor**: Docling (recommended) or Tesseract
- **LLM Model**: OpenAI GPT-4o or Claude Sonnet 4

### 3. Explore Results
- **Interactive graph**: Navigation, zoom, node selection
- **Statistics panel**: Entity and relationship counters
- **Dynamic legend**: Types present in current document

### 4. Analyze Embeddings
- **Click** on any graph node
- **View embeddings**: Numerical values representing the concept
- **Understand AI**: Educational explanation of how they work

## 🏗️ Architecture

### Project Structure

```
├── app.py                  # Main entry point
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
│   ├── ocr.py            # OCR processing
│   ├── llm.py            # LLM integration
│   ├── embeddings.py     # Vector management
│   ├── graph_builder.py  # Graph construction
│   └── utils.py          # General utilities
├── assets/               # Static resources
│   └── style.css        # Custom styles
└── requirements.txt     # Python dependencies
```

### Data Flow

1. **Upload** → Document/URL input by user
2. **Extraction** → OCR converts to plain text
3. **Chunking** → Semantic text division
4. **Vectorization** → Embedding generation
5. **Analysis** → LLM extracts entities and relationships
6. **Visualization** → Interactive graph construction

## 🛠️ Technologies Used

### Backend
- **Dash**: Python web framework
- **Flask**: Underlying web server
- **Docling**: Advanced document OCR
- **PyTesseract**: Backup OCR
- **LangChain**: Semantic chunking

### AI and ML
- **OpenAI GPT-4o**: Entity extraction
- **Claude Sonnet 4**: Alternative LLM
- **OpenAI Embeddings**: Text vectorization
- **Pinecone**: Vector database

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

## 🐛 Troubleshooting

### Common Issues

**API Keys Error**
```bash
# Check environment variables
echo $OPENAI_API_KEY
echo $PINECONE_API_KEY
```

**Docling Problems**
```bash
# Install system dependencies
pip install docling[full]
```

**Pinecone Errors**
- Verify index has dimension 1536
- Check environment is correct

### Debug Mode

```bash
# Run with debug enabled
export DASH_DEBUG=true
python app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License. See `LICENSE` file for details.

---

**Enjoy exploring knowledge visually! 🚀**