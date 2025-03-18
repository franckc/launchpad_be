Initialize the repo afetr checkint it out:
uv virtualenv
source .venv/bin/activate
uv pip install -r requirements.txt

Note: if there is an error about numpy depency, remove the version in requirements.txt

Add a new package
uv pip add <package>

Generate requirements.txt
uv pip freeze > requirements.txt

Start the app:
uv run main.py
