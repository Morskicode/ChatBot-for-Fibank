# Fibank Chatbot

A sophisticated banking chatbot for **First Investment Bank AD (Fibank)** built with a modular architecture for enhanced maintainability, extensibility, and performance.

## 📁 Project Structure

```
fibank/
├── 📂 core/                    # Core chatbot functionality
│   ├── __init__.py
│   ├── chatbot.py              # Main chatbot orchestrator
│   └── context.py              # Conversation context management
├── 📂 services/                # Service layer components
│   ├── __init__.py
│   ├── gemini_service.py       # Google Gemini AI integration
│   ├── semantic_service.py     # Semantic search with lazy loading
│   └── rendering_service.py    # Unified product rendering
├── 📂 utils/                   # Utility functions
│   ├── __init__.py
│   ├── i18n.py                 # Language detection utilities
│   └── config_loader.py        # Configuration loading utilities
├── 📂 config/                  # Configuration files
│   ├── intents.yml             # Intent recognition patterns
│   └── keywords.yml            # Product keyword mappings
├── 📂 data/                    # Data files
│   ├── credit_cards.json       # Credit card products
│   └── credits.json            # Loan products
├── main.py                     # Main entry point
├── requirements.txt            # Dependencies with version constraints
├── .env.example               # Environment configuration example
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Installation

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd fibank
pip install -r requirements.txt
```

### 2. Configuration

Copy the environment configuration template:

```bash
cp .env.example config.env
```

Edit `config.env` with your settings:

```env
# Google Gemini AI (optional - will fallback to semantic search if not provided)
GOOGLE_GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL_NAME=gemini-1.5-flash

# Paths (optional - uses defaults if not specified)
CREDIT_CARDS_JSON_PATH=data/credit_cards.json
CREDITS_JSON_PATH=data/credits.json

# Semantic search settings
SIMILARITY_THRESHOLD=0.3
```

### 3. Run the Chatbot

```bash
python main.py
```
### Basic Conversation

```
You: Какви кредитни карти предлагате?
[BOT] Fibank Assistant: Ето всички налични кредитни карти от Fibank:

📱 Visa карти:
🔹 Visa Classic
   Кредитен лимит: до 5,000 лв.
   🔗 Повече информация: https://...

🔹 Visa Gold
   Кредитен лимит: до 15,000 лв.
   🔗 Повече информация: https://...
```

### Specific Product Inquiry

```
You: Tell me about Visa Gold
[BOT] Fibank Assistant: 💳 Information about Visa Gold:

**Key Benefits:**
Premium card with enhanced features and higher credit limits...

**Technical Details:**
- Credit limit: up to BGN 15,000
- Annual fee: BGN 60
```

## 🛠️ Development

### Adding New Services

1. Create a new service in `services/`:
```python
# services/new_service.py
class NewService:
    def __init__(self):
        # Initialize service
        pass
```

2. Import and initialize in `core/chatbot.py`:
```python
from services.new_service import NewService

class FibankChatbot:
    def _initialize_services(self):
        self.new_service = NewService()
```

### Adding New Intent Patterns

Edit `config/intents.yml`:
```yaml
new_intent:
  - "\\b(new\\s*pattern|нов\\s*модел)\\b"
  - "\\b(another\\s*pattern|друг\\s*модел)\\b"
```

### Adding New Keywords

Edit `config/keywords.yml`:
```yaml
new_category:
  subcategory:
    - "keyword1"
    - "keyword2"
```

## 📋 Dependencies

### Core Dependencies
- `python-dotenv>=1.0.0` - Environment configuration
- `colorama>=0.4.6` - Colored console output
- `google-generativeai>=0.3.0` - Google Gemini AI
- `sentence-transformers>=2.2.2` - Semantic search
- `scikit-learn>=1.3.0` - Machine learning utilities
- `langdetect>=1.0.9` - Language detection
- `PyYAML>=6.0` - Configuration file parsing

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_GEMINI_API_KEY` | Google Gemini API key | None (fallback mode) |
| `GEMINI_MODEL_NAME` | Gemini model to use | `gemini-1.5-flash` |
| `SIMILARITY_THRESHOLD` | Semantic search threshold | `0.3` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Configuration Files

- **`config/intents.yml`**: Intent recognition patterns
- **`config/keywords.yml`**: Product keyword mappings
- **`data/credit_cards.json`**: Credit card product data
- **`data/credits.json`**: Loan product data

## 🚨 Troubleshooting

### Common Issues

**Import Errors**:
```bash
pip install -r requirements.txt
```

**Missing Data Files**:
- Ensure `data/credit_cards.json` and `data/credits.json` exist
- The system will show an error if these are missing

**Gemini API Issues**:
- The chatbot will automatically fallback to semantic search mode
- Check your API key in `config.env`

**Configuration Errors**:
- YAML files will fallback to defaults if malformed
- Check the log file for specific error messages

## 📈 Architecture Benefits

This modular architecture provides significant improvements over the previous monolithic approach:
- **Better maintainability** with separated concerns
- **Faster startup** with lazy loading of AI models  
- **Easier testing** with isolated components
- **Configuration-driven** behavior with external YAML files

## 🤝 Contributing

1. Follow the modular architecture patterns
2. Add tests for new functionality
3. Update configuration files for new intents/keywords
4. Use type hints and comprehensive docstrings
5. Follow the existing code style