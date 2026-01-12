# Teradata PDCR Report Generator

A Python library for generating Teradata PDCR (Performance Data Collection and Reporting) reports using pandas DataFrames and teradatasqlalchemy.

## Features

- Generate PDCR reports from Teradata databases
- Leverage pandas DataFrames for data manipulation and analysis
- Use SQLAlchemy with Teradata dialect for database connectivity
- Modular library design for easy integration

## Prerequisites

- Python 3.8 or higher
- Access to a Teradata database
- Teradata ODBC Driver or appropriate Teradata client software

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/clydewatts1/ubiquitous-palm-tree.git
cd ubiquitous-palm-tree
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Project Structure

```
ubiquitous-palm-tree/
├── src/                    # Source code
│   └── __init__.py
├── tests/                  # Test files
│   └── __init__.py
├── docs/                   # Documentation
├── venv/                   # Virtual environment (not in git)
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore file
└── README.md              # This file
```

## Usage

### Basic Example

```python
from sqlalchemy import create_engine
import pandas as pd

# Create Teradata connection
engine = create_engine('teradatasql://username:password@hostname/database')

# Query data into DataFrame
query = "SELECT * FROM your_pdcr_table"
df = pd.read_sql(query, engine)

# Process and generate reports
print(df.head())
```

## Dependencies

Key dependencies include:
- **pandas** - Data manipulation and analysis
- **teradatasqlalchemy** - Teradata dialect for SQLAlchemy
- **sqlalchemy** - SQL toolkit and ORM
- **pytest** - Testing framework
- **black** - Code formatter
- **flake8** - Linting tool

See [requirements.txt](requirements.txt) for complete list.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ tests/
```

### Linting

```bash
flake8 src/ tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Resources

- [teradatasqlalchemy Documentation](https://pypi.org/project/teradatasqlalchemy/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
