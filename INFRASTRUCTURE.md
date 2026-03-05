# Infrastructure Components

This document describes the core infrastructure components added to enable the delegated agent pattern in the Arabic Diana Project.

## Components

### 1. BaseReconstructionEngine (`base_reconstruction_engine.py`)

Abstract base class that provides a common interface for all grammar reconstruction engines.

**Key features:**
- Defines the contract that all engine classes must follow
- Requires subclasses to implement `make_df()` method
- Requires subclasses to define `SHEET_NAME` attribute

**Usage:**
```python
from base_reconstruction_engine import BaseReconstructionEngine
import pandas as pd

class MyEngine(BaseReconstructionEngine):
    SHEET_NAME = 'MySheet'
    
    @classmethod
    def make_df(cls) -> pd.DataFrame:
        # Generate and return DataFrame
        return pd.DataFrame(...)
```

### 2. Harakat Engine (`harakat_engine.py`)

Engine for loading and processing Arabic diacritical marks (harakat) data.

**Key features:**
- Loads harakat data from CSV files (supports multiple file names)
- Automatically generates UTF-8 encoding if missing
- Used by `reconstruction_utils.py` for linguistic reconstruction

**Usage:**
```python
from harakat_engine import حركات

# Load harakat data
df = حركات.make_df()
print(df.head())
```

### 3. Web Application (`web_app/`)

FastAPI web application providing REST API access to the grammar engines.

**Endpoints:**
- `GET /` - API information
- `GET /health` - Health check
- `GET /engines` - List all available engines
- `GET /engines/{sheet_name}` - Get data for a specific engine
- `GET /export/all` - Export all engines to Excel

**Starting the server:**
```bash
python run_server.py --host 127.0.0.1 --port 8000
```

Or with auto-reload for development:
```bash
python run_server.py --host 127.0.0.1 --port 8000 --reload
```

**Example API calls:**
```bash
# Get health status
curl http://127.0.0.1:8000/health

# List all engines
curl http://127.0.0.1:8000/engines

# Get verb engine data
curl http://127.0.0.1:8000/engines/الأفعال
```

## Testing

Run the infrastructure tests:
```bash
python test_infrastructure.py
```

This validates:
- BaseReconstructionEngine import
- Harakat engine functionality
- Web app initialization
- Engine collection and inheritance

## Architecture

The delegated agent pattern allows:
1. **Modularity**: Each grammar category has its own engine
2. **Extensibility**: New engines can be added by inheriting from BaseReconstructionEngine
3. **Automation**: Main_engine.py automatically discovers and collects all engines
4. **API Access**: Web app provides programmatic access to all engines

## Engine Count

Currently supports **64 engines** covering various Arabic grammar categories including:
- Verbs (الأفعال)
- Nouns (الأسماء)
- Particles (الحروف)
- Adjectives (الصفات)
- And many more...

Each engine generates structured data for linguistic analysis and natural language processing.
