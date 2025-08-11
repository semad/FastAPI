# ERD Generator Script

This script generates Entity Relationship Diagrams (ERDs) for the FastAPI application's database models.

## Features

- **Text ERD**: Generates a detailed text representation of the database schema
- **Visual ERD**: Creates a visual diagram showing entities and relationships (requires matplotlib)
- **Automatic Relationship Detection**: Automatically detects foreign key relationships between models
- **Column Properties**: Shows primary keys, foreign keys, unique constraints, indexes, and nullable fields

## Installation

Install the required dependencies:

```bash
pip install -r requirements_erd.txt
```

## Usage

### Basic Usage

Generate both text and visual ERDs:

```bash
python scripts/generate_erd.py
```

### Command Line Options

- `--output` or `-o`: Specify output file path for visual ERD (default: `erd_diagram.png`)
- `--text-only` or `-t`: Generate only text ERD
- `--visual-only` or `-v`: Generate only visual ERD

### Examples

Generate only text ERD:
```bash
python scripts/generate_erd.py --text-only
```

Generate only visual ERD with custom filename:
```bash
python scripts/generate_erd.py --visual-only --output my_erd.png
```

Generate both with custom visual output:
```bash
python scripts/generate_erd.py --output database_schema.png
```

## Output

The script generates two files:

1. **Text ERD** (`.txt`): Detailed text representation showing:
   - All entities (tables) with their columns
   - Column types and properties (PK, FK, Unique, Index, Nullable)
   - Relationships between entities

2. **Visual ERD** (`.png`): Visual diagram showing:
   - Entity boxes with column details
   - Relationship arrows with labels
   - Color-coded columns (red for PK, blue for FK)

## Models Covered

- **User**: Core user entity with authentication and profile data
- **Tier**: User subscription tiers
- **Book**: Book catalog with user ownership
- **Post**: User-generated content
- **RateLimit**: API rate limiting configuration per tier

## Dependencies

- `matplotlib`: For visual diagram generation
- `sqlalchemy`: For model introspection
- Python 3.7+

## Troubleshooting

- **Import errors**: Make sure you're running from the project root directory
- **Matplotlib not available**: Install matplotlib or use `--text-only` flag
- **Model not found**: Ensure all models are properly imported in the script
