# 🏦 NeoBank ARIA — AI Security Workshop

**ARIA** (Automated Response & Inquiry Assistant) is NeoBank's intentionally vulnerable AI banking assistant, built for the Gen Academy AI security workshop. Participants interact with ARIA to explore common AI-agent security weaknesses through hands-on testing, including prompt injection, information disclosure, unsafe tool use, and multi-turn attacks.

The application uses a Streamlit interface, an OpenAI-powered LangChain agent, a local SQLite database, and a simple Python knowledge base. All NeoBank customers, accounts, balances, and transactions in this project are fictional.

## Quick Start

### 1. Prerequisites

- Python 3.10 or newer
- pip
- An [OpenAI API key](https://platform.openai.com/api-keys)

### 2. Create and activate a virtual environment

#### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Run the app

```bash
python -m streamlit run app.py
```

Streamlit will normally open the application automatically. Otherwise, open:

```text
http://localhost:8501
```

### 5. Enter your API key

Enter your own OpenAI API key in the sidebar. The app validates the key before allowing access to the chatbot.

### 6. Sign in

Use the fictional NeoBank customer account provided for the workshop.

| Name | User ID | Tier |
|---|---|---|
| Alex Mercer | USR-0042 | Standard |

Other fictional accounts exist in the database and form part of the security exercise.

---

## Project Structure

```text
week6-neobank-aria-agent/
├── app.py
├── agent.py
├── database.py
├── knowledge_base.py
├── seed_data.py
├── neobank.db
├── requirements.txt
├── redteam/                 # Promptfoo configuration, Python provider, and tests
├── architecture.html
├── security_guide.html
├── .gitignore
└── README.md
```

### Main files

| File | Purpose |
|---|---|
| `app.py` | Streamlit UI, API-key validation, login flow, chat interface, navigation, and workshop challenges |
| `agent.py` | Unguarded ARIA agent built with LangChain and OpenAI tools |
| `database.py` | SQLite connection, initialization, authentication, and query helpers |
| `knowledge_base.py` | NeoBank policy and knowledge-base content |
| `seed_data.py` | Fictional customer, account, and transaction seed data |
| `neobank.db` | SQLite database used by the workshop |
| `architecture.html` | In-app architecture reference |
| `security_guide.html` | In-app AI security guide |
| `requirements.txt` | Python dependencies |
| `redteam/` | Promptfoo attack suites, agent adapter, pinned Node dependencies, and offline adapter tests |

---

## Requirements

The unguarded ARIA version uses:

```text
streamlit>=1.38.0
langchain>=0.3.0
langchain-openai>=0.3.0
langchain-core>=0.3.0
python-dotenv>=1.0.0
```

Install the repository's current `requirements.txt` before running the app.

---

## Architecture

- **LLM:** OpenAI `gpt-4o-mini`
- **Agent framework:** LangChain
- **Database:** SQLite
- **Knowledge base:** Python dictionary
- **UI:** Streamlit
- **Authentication:** Fictional NeoBank customer lookup
- **API access:** User-supplied OpenAI API key

ARIA is intentionally designed as an **unguarded security-testing target**. The workshop challenges are meant to demonstrate why model instructions alone are not a sufficient security boundary.

---

## Workshop Challenges

The sidebar includes guided security challenges covering areas such as:

- Jailbreaking
- Obfuscation
- Sensitive data exposure
- Prompt injection
- Red teaming
- Multi-turn escalation
- PII extraction

Participants are expected to test ARIA within the scope of the fictional workshop environment.

---

## Test ARIA with Promptfoo

Promptfoo checks how ARIA responds to attacks such as requests for another
customer's data, prompt injection, and attempts to bypass its rules. You do not
need to start Streamlit.

### 1. Set up

Install Node.js 22.22.0 or newer. From the project root, activate the Python
virtual environment and install dependencies as shown in Quick Start. Then run:

```bash
cd redteam
npm ci
```

Create a `.env` file inside `redteam/`:

```dotenv
OPENAI_API_KEY=your-key-here
```

Keep your key private. This file is ignored by Git.

### 2. Run the tests

Run these commands from `redteam/` with your Python environment active:

```bash
# Start with nine fixed tests.
npm run smoke -- --env-file .env

# Generate a broader set of attacks.
npm run generate -- --env-file .env --remote

# Review generated.yaml, then run the scan.
npm run scan -- --env-file .env --remote

# View the results.
npm run report
```

Tests use paid model calls. The broader suite also uses Promptfoo's remote attack
services, so use only the fictional workshop data.

### What is being tested?

- **Plugins** choose what to test, such as unauthorized data access (`bola`),
  privacy leaks (`pii:direct`), or unsupported actions (`excessive-agency`).
- **Strategies** choose how to attack, such as direct requests (`basic`), encoded
  prompts (`base64`), or escalating conversations (`crescendo`).
- **`provider.py`** connects Promptfoo to ARIA, runs it as Alex Mercer against a
  fresh temporary database, and returns responses for grading.

ARIA is intentionally vulnerable, so some security tests are expected to fail.
A failed test may reveal a weakness; an execution error means the test could not
complete normally. Review the results manually.

See the [detailed Promptfoo guide](redteam/README.md) for additional tests,
configuration, and adapter checks.

---

## Important Security Notes

- Do not commit real API keys to the repository.
- Do not place secrets directly in `app.py`, `agent.py`, or other tracked files.
- Use only fictional workshop data.
- This project intentionally contains insecure behavior for educational testing.
- Do not use this implementation as a production banking assistant.

---

### API key is rejected

Confirm that the OpenAI API key:

- is complete,
- is still active,
- belongs to an OpenAI project/account with API access,
- and can reach OpenAI from the current network.

---

## Disclaimer

NeoBank, ARIA, all customer identities, accounts, balances, and transactions in this repository are fictional.

This project is intended solely for educational use, controlled AI-security testing, and red-team exercises.

---

*Gen Academy · AI Security Workshop*
