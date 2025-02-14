import requests
import json
import argparse
import time
import os
import psycopg2
from dotenv import load_dotenv

# Reading environment variables
load_dotenv()
API_KEY = os.getenv("ETHERSCAN_API_KEY")
SAVE_TO = os.getenv("SAVE_TO", "json")  # json or postgres
JSON_PATH = os.getenv("JSON_PATH", "./transactions.json")

# Postgres Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "etherscan")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

# API Base URL
BASE_URL = "https://api.etherscan.io/api"


def fetch_transactions(block_number):
    """
    Fetch block transactions from Etherscan API
    """
    hex_block = hex(block_number)  # Convert to hexadecimal
    url = f"{BASE_URL}?module=proxy&action=eth_getBlockByNumber&tag={hex_block}&boolean=true&apikey={API_KEY}"

    response = requests.get(url)
    data = response.json()

    if "result" not in data or data["result"] is None:
        print(f"Error fetching transactions for block {block_number}: {data.get('message', 'Unknown error')}")
        return []

    transactions = data["result"].get("transactions", [])
    parsed_transactions = []

    for tx in transactions:
        parsed_transactions.append({
            "hash": tx["hash"],
            "status": tx.get("txreceipt_status", "N/A"),
            "block": block_number,
            "timestamp": int(data["result"]["timestamp"], 16),
            "from": tx["from"],
            "to": tx["to"],
            "value": int(tx["value"], 16) / 10**18,  # Convert to ETH
            "gasUsed": int(tx.get("gas", "0"), 16),
            "gasPrice": int(tx.get("gasPrice", "0"), 16),
            "transaction_fee": (int(tx.get("gas", "0"), 16) * int(tx.get("gasPrice", "0"), 16)) / 10**18,
            "method": tx.get("input", "N/A")[:10],  # Transaction method (only the first 10 codes)
            "sponsored": tx.get("maxFeePerGas", "N/A")  # May indicate whether there is sponsorship
        })

    return parsed_transactions


def save_to_json(transactions):
    """
    Storing transaction results in JSON
    """
    with open(JSON_PATH, "w") as f:
        json.dump(transactions, f, indent=4)
    print(f"✅ Transaction data has been stored in {JSON_PATH}")


def save_to_postgres(transactions):
    """
    Storing transaction results in PostgreSQL
    """
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            hash TEXT,
            status TEXT,
            block INTEGER,
            timestamp INTEGER,
            from_address TEXT,
            to_address TEXT,
            value NUMERIC,
            gasUsed INTEGER,
            gasPrice INTEGER,
            transaction_fee NUMERIC,
            method TEXT,
            sponsored TEXT
        )
    """)
    conn.commit()

    for tx in transactions:
        cursor.execute("""
            INSERT INTO transactions (hash, status, block, timestamp, from_address, to_address, value, gasUsed, gasPrice, transaction_fee, method, sponsored)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (tx["hash"], tx["status"], tx["block"], tx["timestamp"], tx["from"], tx["to"], tx["value"], tx["gasUsed"], tx["gasPrice"], tx["transaction_fee"], tx["method"], tx["sponsored"]))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Transaction data has been stored PostgreSQL")


def main():
    parser = argparse.ArgumentParser(description="Etherscan Transaction Query Tool")
    parser.add_argument("--start", type=int, required=True, help="Starting block number")
    parser.add_argument("--end", type=int, required=True, help="End block number")
    parser.add_argument("--method", type=str, default=None, help="Filter by specified transaction method")
    parser.add_argument("--amount", type=int, choices=[0, 1], default=None, help="0 = Only see 0 ETH, 1 = Only see non-0 ETH")

    args = parser.parse_args()

    # Limit the block range to a maximum of 100
    if args.end - args.start > 100:
        print("❌ Error: The block range cannot exceed 100")
        return

    all_transactions = []

    for block in range(args.start, args.end + 1):
        transactions = fetch_transactions(block)

        # Filtering Transactions
        if args.method:
            transactions = [tx for tx in transactions if tx["method"] == args.method]
        if args.amount is not None:
            transactions = [tx for tx in transactions if (tx["value"] == 0) == (args.amount == 0)]

        all_transactions.extend(transactions)
        print(f"Block {block}: {len(transactions)} transactions processed")
        time.sleep(0.2)  # Avoid API throttling

    # Storing Data
    if SAVE_TO == "json":
        save_to_json(all_transactions)
    else:
        save_to_postgres(all_transactions)


if __name__ == "__main__":
    main()
