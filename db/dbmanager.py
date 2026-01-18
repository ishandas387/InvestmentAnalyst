import sqlite3
import random
from datetime import datetime, timedelta
import os

from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

console = Console()


class DatabaseManager:
    def __init__(self, db_path="investments.db"):
        self.db_path = db_path

    def check_db_health(self):
        """Checks DB status and asks for recreation if it exists."""
        if os.path.exists(self.db_path):
            console.print(f"[bold green]📂 Database found at:[/bold green] {self.db_path}")

            # Use Rich's Confirm prompt
            recreate = Confirm.ask("Do you want to [bold red]Wipe and Recreate[/bold red] the database?", default=False)

            if recreate:
                console.print("[bold red]🗑️ Deleting existing database...[/bold red]")
                os.remove(self.db_path)
                self.initialize_db()
                self.display_stats()
            else:
                self.display_stats()
        else:
            console.print("[yellow]⚠️ Database not found. Initializing fresh...[/yellow]")
            self.initialize_db()
            self.display_stats()

    def display_stats(self):
        """Prints counts of tables and rows."""
        stats_table = Table(title="📊 Current Database Statistics")
        stats_table.add_column("Table Name", style="cyan")
        stats_table.add_column("Row Count", style="magenta")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [row[0] for row in cursor.fetchall()]

            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats_table.add_row(table, str(count))

        console.print(stats_table)

    def initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executescript('''
                CREATE TABLE IF NOT EXISTS instruments (ticker TEXT PRIMARY KEY, name TEXT, sector TEXT, asset_class TEXT);
                CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT, side TEXT, qty REAL, price REAL, date TEXT, asset_class TEXT);
                CREATE TABLE IF NOT EXISTS holdings (ticker TEXT PRIMARY KEY, qty REAL, avg_cost REAL);
            ''')

        # 2. Seed 100 Instruments (explicit list)
        raw_instruments = [
            ('AAPL', 'Apple Inc.', 'Technology', 'Equity'),
            ('MSFT', 'Microsoft', 'Technology', 'Equity'),
            ('GOOGL', 'Alphabet Inc.', 'Technology', 'Equity'),
            ('AMZN', 'Amazon.com', 'Consumer', 'Equity'),
            ('TSLA', 'Tesla Inc.', 'Consumer', 'Equity'),
            ('NVDA', 'NVIDIA Corp.', 'Technology', 'Equity'),
            ('META', 'Meta Platforms', 'Technology', 'Equity'),
            ('ORCL', 'Oracle Corp.', 'Technology', 'Equity'),
            ('ADBE', 'Adobe Inc.', 'Technology', 'Equity'),
            ('CRM', 'Salesforce', 'Technology', 'Equity'),

            ('JPM', 'JPMorgan Chase', 'Financials', 'Equity'),
            ('BAC', 'Bank of America', 'Financials', 'Equity'),
            ('WFC', 'Wells Fargo', 'Financials', 'Equity'),
            ('GS', 'Goldman Sachs', 'Financials', 'Equity'),
            ('MS', 'Morgan Stanley', 'Financials', 'Equity'),
            ('C', 'Citigroup', 'Financials', 'Equity'),
            ('V', 'Visa Inc.', 'Financials', 'Equity'),
            ('MA', 'Mastercard Inc.', 'Financials', 'Equity'),
            ('AXP', 'American Express', 'Financials', 'Equity'),
            ('PYPL', 'PayPal Holdings', 'Financials', 'Equity'),

            ('XOM', 'Exxon Mobil', 'Energy', 'Equity'),
            ('CVX', 'Chevron Corp.', 'Energy', 'Equity'),
            ('COP', 'ConocoPhillips', 'Energy', 'Equity'),
            ('SLB', 'Schlumberger', 'Energy', 'Equity'),
            ('BP', 'BP plc', 'Energy', 'Equity'),
            ('SHEL', 'Shell plc', 'Energy', 'Equity'),
            ('TTE', 'TotalEnergies', 'Energy', 'Equity'),
            ('EOG', 'EOG Resources', 'Energy', 'Equity'),
            ('OXY', 'Occidental Petroleum', 'Energy', 'Equity'),
            ('PSX', 'Phillips 66', 'Energy', 'Equity'),

            ('UNH', 'UnitedHealth Group', 'Healthcare', 'Equity'),
            ('JNJ', 'Johnson & Johnson', 'Healthcare', 'Equity'),
            ('PFE', 'Pfizer Inc.', 'Healthcare', 'Equity'),
            ('MRK', 'Merck & Co.', 'Healthcare', 'Equity'),
            ('LLY', 'Eli Lilly', 'Healthcare', 'Equity'),
            ('ABBV', 'AbbVie Inc.', 'Healthcare', 'Equity'),
            ('AMGN', 'Amgen Inc.', 'Healthcare', 'Equity'),
            ('GILD', 'Gilead Sciences', 'Healthcare', 'Equity'),
            ('TMO', 'Thermo Fisher Scientific', 'Healthcare', 'Equity'),
            ('ISRG', 'Intuitive Surgical', 'Healthcare', 'Equity'),

            ('COST', 'Costco Wholesale', 'Consumer', 'Equity'),
            ('WMT', 'Walmart Inc.', 'Consumer', 'Equity'),
            ('TGT', 'Target Corp.', 'Consumer', 'Equity'),
            ('HD', 'Home Depot', 'Consumer', 'Equity'),
            ('LOW', "Lowe's Companies", 'Consumer', 'Equity'),
            ('NKE', 'Nike Inc.', 'Consumer', 'Equity'),
            ('SBUX', 'Starbucks', 'Consumer', 'Equity'),
            ('MCD', "McDonald's", 'Consumer', 'Equity'),
            ('KO', 'Coca-Cola', 'Consumer', 'Equity'),
            ('PEP', 'PepsiCo', 'Consumer', 'Equity'),

            ('NFLX', 'Netflix Inc.', 'Technology', 'Equity'),
            ('DIS', 'Walt Disney', 'Consumer', 'Equity'),
            ('INTC', 'Intel Corp.', 'Technology', 'Equity'),
            ('AMD', 'Advanced Micro Devices', 'Technology', 'Equity'),
            ('AVGO', 'Broadcom Inc.', 'Technology', 'Equity'),
            ('QCOM', 'Qualcomm Inc.', 'Technology', 'Equity'),
            ('CSCO', 'Cisco Systems', 'Technology', 'Equity'),
            ('IBM', 'IBM', 'Technology', 'Equity'),
            ('SNOW', 'Snowflake Inc.', 'Technology', 'Equity'),
            ('NOW', 'ServiceNow', 'Technology', 'Equity'),

            ('PLTR', 'Palantir Technologies', 'Technology', 'Equity'),
            ('SHOP', 'Shopify Inc.', 'Technology', 'Equity'),
            ('SQ', 'Block Inc.', 'Financials', 'Equity'),
            ('UBER', 'Uber Technologies', 'Consumer', 'Equity'),
            ('LYFT', 'Lyft Inc.', 'Consumer', 'Equity'),
            ('ABNB', 'Airbnb Inc.', 'Consumer', 'Equity'),
            ('ZM', 'Zoom Video Communications', 'Technology', 'Equity'),
            ('DOCU', 'DocuSign', 'Technology', 'Equity'),
            ('TWLO', 'Twilio Inc.', 'Technology', 'Equity'),
            ('PANW', 'Palo Alto Networks', 'Technology', 'Equity'),

            ('BA', 'Boeing', 'Technology', 'Equity'),
            ('LMT', 'Lockheed Martin', 'Technology', 'Equity'),
            ('NOC', 'Northrop Grumman', 'Technology', 'Equity'),
            ('RTX', 'RTX Corp.', 'Technology', 'Equity'),
            ('CAT', 'Caterpillar', 'Energy', 'Equity'),
            ('DE', 'Deere & Company', 'Energy', 'Equity'),
            ('GE', 'GE Aerospace', 'Technology', 'Equity'),
            ('UPS', 'United Parcel Service', 'Consumer', 'Equity'),
            ('FDX', 'FedEx', 'Consumer', 'Equity'),
            ('HON', 'Honeywell', 'Technology', 'Equity'),

            # Space / related
            ('RKLB', 'Rocket Lab USA', 'Space', 'Equity'),
            ('ASTS', 'AST SpaceMobile', 'Space', 'Equity'),
            ('LUNR', 'Intuitive Machines', 'Space', 'Equity'),
            ('IRDM', 'Iridium Communications', 'Space', 'Equity'),
            ('SPCE', 'Virgin Galactic', 'Space', 'Equity'),
            ('SPIR', 'Spire Global', 'Space', 'Equity'),

            # Extra to reach 100
            ('TSM', 'Taiwan Semiconductor', 'Technology', 'Equity'),
            ('ASML', 'ASML Holding', 'Technology', 'Equity'),
            ('BABA', 'Alibaba Group', 'Technology', 'Equity'),
            ('TM', 'Toyota Motor', 'Consumer', 'Equity'),
            ('SONY', 'Sony Group', 'Technology', 'Equity'),
            ('NVO', 'Novo Nordisk', 'Healthcare', 'Equity'),
            ('SAP', 'SAP SE', 'Technology', 'Equity'),
            ('UBS', 'UBS Group', 'Financials', 'Equity'),
            ('HSBC', 'HSBC Holdings', 'Financials', 'Equity'),
            ('RIO', 'Rio Tinto', 'Energy', 'Equity'),
        ]

        # Insert into DB
        cursor.executemany(
            "INSERT OR IGNORE INTO instruments VALUES (?,?,?,?)",
            raw_instruments
        )

        # Extract ticker -> sector mapping from raw_instruments
        ticker_to_sector = {t: sector for (t, name, sector, asset_class) in raw_instruments}
        tickers = list(ticker_to_sector.keys())

        # Sector-based price ranges (min, max)
        sector_price_ranges = {
            'Technology': (80, 600),
            'Financials': (40, 300),
            'Energy': (30, 250),
            'Healthcare': (50, 500),
            'Consumer': (20, 400),
            'Space': (5, 80),
        }

        def random_date(start_date: str, end_date: str) -> str:
            """
            Returns a random date string between start_date and end_date (inclusive).
            Format: YYYY-MM-DD
            """
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            delta_days = (end - start).days
            return (start + timedelta(days=random.randint(0, delta_days))).strftime("%Y-%m-%d")

        # Seed 50 random transactions
        for _ in range(50):
            t = random.choice(tickers)
            sector = ticker_to_sector.get(t, 'Technology')

            # Pick realistic price range for the sector
            low, high = sector_price_ranges.get(sector, (50, 500))
            way = random.choices(['BUY', 'SELL'], weights=[70, 30])[0]
            qty = random.randint(1, 50)
            price = round(random.uniform(low, high), 2)
            to_be_added_to_holding = random.randint(1, 50)
            cursor.execute(
                "INSERT INTO transactions (ticker, side, qty, price, date, asset_class) VALUES (?,?,?,?,?,?)",
                (
                    t,
                    way,
                    qty,
                    price,
                    random_date("2024-01-01", "2024-12-31"),
                    'Equity'
                )
            )
            # ignore this if, remove and re-indent.
            if 0 == 0:
                cursor.execute("SELECT qty, avg_cost FROM holdings WHERE ticker = ?", (t,))
                row = cursor.fetchone()

                current_qty = row[0] if row else 0.0
                current_avg = row[1] if row else 0.0

                if way == "BUY":
                    new_qty = current_qty + qty
                    # Weighted average cost
                    new_avg = ((current_qty * current_avg) + (qty * price)) / new_qty
                    cursor.execute(
                        "INSERT INTO holdings (ticker, qty, avg_cost) VALUES (?,?,?) "
                        "ON CONFLICT(ticker) DO UPDATE SET qty = excluded.qty, avg_cost = excluded.avg_cost",
                        (t, new_qty, round(new_avg, 2))
                    )

                else:  # SELL
                    new_qty = current_qty - qty

                    if new_qty <= 0:
                        # Position closed (or oversold) -> reset holding
                        cursor.execute(
                            "INSERT INTO holdings (ticker, qty, avg_cost) VALUES (?,?,?) "
                            "ON CONFLICT(ticker) DO UPDATE SET qty = excluded.qty, avg_cost = excluded.avg_cost",
                            (t, 0.0, 0.0)
                        )
                    else:
                        # Avg cost unchanged on sell
                        cursor.execute(
                            "UPDATE holdings SET qty = ? WHERE ticker = ?",
                            (new_qty, t)
                        )
        conn.commit()

    def get_schema(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
            return "\n".join([row[0] for row in cursor.fetchall()])

    def execute_query(self, query):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()
