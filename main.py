import sys
import subprocess
from dotenv import load_dotenv
from db.dbmanager import DatabaseManager
from agent.graph import generate_visual_graph
from ui.terminal import run_cli

def main():

    load_dotenv()
    # 1. Shared setup logic
    generate_visual_graph()
    db = DatabaseManager()
    db.check_db_health()

    # 2. Check for UI flag: python main.py --ui
    if "--ui" in sys.argv:
        print("🚀 Launching Streamlit UI...")
        subprocess.run(["streamlit", "run", "ui/app_ui.py"])
    else:
        # Default to your existing terminal app
        from agent.graph import app # Import here to avoid circular dependencies
        run_cli(app)

if __name__ == "__main__":
    main()