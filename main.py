from dotenv import load_dotenv
load_dotenv()

from api import app

# From crewai main.py
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
