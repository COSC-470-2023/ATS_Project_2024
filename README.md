# Algorithmic Trading System
## Setup
1. `cp example.env .env`
2. Fill `.env` file with appropriate credentials
   - Can skip this step if only running tests
3. `./setup`
   - Creates the virtual environment and installs necessary packages

## Execution
You can execute scripts using `.venv/bin/python3` as your Python executable.
- `.venv/bin/python3 -m ats.collection.bonds_api_query`

You can also use `source .venv/bin/activate` instead, which is useful when running multiple scripts.
- `source .venv/bin/activate`
- `python3 -m ats.collection.bonds_api_query`
- `python3 -m ats.database.bonds_insert`
- `deactivate`
