from dotenv import load_dotenv

from db.dbmanager import DatabaseManager
from agent.graph import app, generate_visual_graph
from ui.terminal import run_cli

def main():
    load_dotenv()
    generate_visual_graph()
    db = DatabaseManager()
    db.check_db_health()
    run_cli(app)

if __name__ == "__main__":
    main()