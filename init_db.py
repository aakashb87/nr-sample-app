import os
import psycopg2

# Reuse the same env-var pattern as app.py
PG_HOST = os.getenv("PGHOST", "nrpgdemo-aakashb.postgres.database.azure.com")
PG_DB = os.getenv("PGDATABASE", "postgres")
PG_USER = os.getenv("PGUSER", "demo")
PG_PASSWORD = os.getenv("PGPASSWORD", "b5yf.W9vhS9ebWC")
PG_SSLMODE = os.getenv("PGSSLMODE", "require")

conn = psycopg2.connect(
    host=PG_HOST,
    dbname=PG_DB,
    user=PG_USER,
    password=PG_PASSWORD,
    sslmode=PG_SSLMODE,
)
conn.autocommit = True
cur = conn.cursor()

# Create products table if not exists
cur.execute(
    """
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
"""
)

# Seed data if table is empty
cur.execute("SELECT COUNT(*) FROM products;")
count = cur.fetchone()[0]

if count == 0:
    cur.execute(
        """
    INSERT INTO products (name, category, price) VALUES
    ('Red Collar', 'Pet Accessories', 19.99),
    ('Blue Leash', 'Pet Accessories', 24.99),
    ('Dog Bed XL', 'Pet Furniture', 89.99),
    ('Cat Tower', 'Pet Furniture', 129.99),
    ('Fish Food Premium', 'Pet Food', 9.99),
    ('Bird Seed Mix', 'Pet Food', 14.49);
    """
    )
    print("Inserted sample products")
else:
    print(f"Products table already has {count} rows")

cur.close()
conn.close()
print("DB initialization complete")
