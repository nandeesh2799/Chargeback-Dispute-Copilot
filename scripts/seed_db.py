import sys
import os

# Add project root and backend directory to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "backend"))

from app.db.session import SessionLocal
from app.services.seeder import seed_database

def main():
    print("Seeding Chargeback & Dispute Copilot database with RJ Kitchen synthetic fixtures...")
    db = SessionLocal()
    try:
        count = seed_database(db, force_reset=True)
        print(f"Done! {count} disputes seeded successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
