# coin-squeezer

Price scraper of select products using Agents, saving the result into Cloud SQL and sends email notifications through Gmail.

Using Google's Agentic Development Kit and Antigravity, deployed in Google Cloud's Agent Runtime, Database in Cloud SQL.

Agent generated with `agents-cli` version `1.4.2`

## Project Structure

```
coin-squeezer/
├── app/                                    # Core agent code
│   ├── agent.py                            # Main agent logic
│   ├── fast_api_app.py                     # FastAPI Backend server
│   └── app_utils/                          # App utilities and helpers
│   └── agent_orchestrator                  # Agent Orchestrator
│       └── scraper_suborchestrator         # Scraper Suborchestrator
│       └── vea_scraper_agent               # Vea Market Data Extractor
│       └── mas_scraper_agent               # MasOnline Market Data Extrator
│       └── carrefour_scraper_agent         # Carrefour Market Data Extractor       
│       └── data_parser_agent               # Data parser Agent for data unification
│       └── database_agent                  # Database Agent for Cloud SQL Operations
│       └── email_agent                     # Email Agent for Notifications
├── tests/                                  # Unit, integration, and load tests
├── GEMINI.md                               # AI-assisted development guide
└── pyproject.toml                          # Project dependencies
```

## Architecture Diagram



## Requirements

Before you begin, ensure you have:
- **Clone the project**: Project includes both requirements.txt and uv.lock, requirements.txt is used for local testing and uv.lock for Agent Runtime Deployment.
- **uv**: Python package manager (used for all dependency management in this project) - [Install](https://docs.astral.sh/uv/getting-started/installation/) ([add packages](https://docs.astral.sh/uv/concepts/dependencies/) with `uv add <package>`)
- **Verify Service Accounts and Roles**: This project won't work properly unless you setup their corresponding Service Accounts, Roles and Keys in order to use Cloud SQL and GMail through Agents.
- **Roles**: Cloud SQL Instance, Cloud SQL User, Gmail Send, Secret Manager Accessor.


## Quick Start

Open terminal in your preferred IDE and setup a virtual environment:

```bash
python -m venv .venv
```

Activate the Virtual Environment:

- On Mac/Linux
```bash
source .venv/bin/activate
```

- On Windows (Powershell)
```None
venv\Scripts\Activate.ps1
```

- On Windows (CMD)
```None
venv\Scripts\activate.bat
```

Install dependencies:

```bash
pip install requirements.txt
```

Setup an .env file on the root folder with following:
```
# Vertex AI Configuration (default)
GOOGLE_GENAI_USE_VERTEXAI=""
GOOGLE_CLOUD_PROJECT=""
GOOGLE_CLOUD_LOCATION=""

# Database Credentials
CLOUD_SQL_MYSQL_PROJECT=""
CLOUD_SQL_MYSQL_REGION=""
CLOUD_SQL_MYSQL_INSTANCE=""
CLOUD_SQL_MYSQL_DATABASE=""
CLOUD_SQL_MYSQL_USER=""

# Email Variables
GOOGLE_USER_EMAIL_SENDER=""
GOOGLE_USER_EMAIL_DESTINATION="" 
```

Test the agent with a local web server:

```bash
adk web
```

This will connect to the Agent Runtime instance, that has Cloud SQL and Gmail access.

You can simply say something like "Perform a run" and will execute the workflow.

You can also check the small website that I built as an alternative to the email, it's deployed in Netlify for frontend, Render for backend, so please give it a moment while it spins up the server.

https://coin-squeezer.netlify.app/