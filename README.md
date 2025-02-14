# Etherscan Scraper

## Overview
The **Etherscan Scraper** is a CLI tool built with Python that fetches Ethereum blockchain transactions from Etherscan.io. It allows users to specify a block range, filter transactions by method or amount, and store results in a JSON file or a PostgreSQL database.

## Features
- Query Ethereum transactions from Etherscan API
- Specify block range (max 100 blocks)
- Filter transactions by method and amount (0 or non-0 ETH)
- Save data to JSON or PostgreSQL
- Uses `.env` for API keys and database configuration

## Prerequisites
Ensure you have the following installed:
- Python 3.9+
- pip (Python package manager)
- PostgreSQL (optional, for database storage)
- Docker & Docker Compose (optional, for PostgreSQL setup)

## Installation
1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd etherscan_scraper
   ```
2. Create and activate a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # MacOS/Linux
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Environment Configuration
Create a `.env` file in the project root and add the following:
```sh
ETHERSCAN_API_KEY=your_api_key_here
SAVE_TO=json  # or postgres
JSON_PATH=./transactions.json

# PostgreSQL Configuration (if using database storage)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=etherscan
DB_USER=postgres
DB_PASS=postgres
```

## Running the Scraper
### Query Transactions
Run the following command to fetch transactions within a specified block range:
```sh
python etherscan_scraper.py --start 21442021 --end 21442120 --method transfer --amount 0
```
#### Arguments:
- `--start` : Starting block number (required)
- `--end` : Ending block number (required, max range of 100 blocks)
- `--method` : Filter by transaction method (optional)
- `--amount` : `0` (only 0 ETH) or `1` (non-0 ETH) (optional)

## Output Storage
- If `SAVE_TO=json`, transactions will be saved in `transactions.json`.
- If `SAVE_TO=postgres`, transactions will be inserted into a PostgreSQL database.

## Database Setup with Docker
1. Start PostgreSQL using Docker:
   ```sh
   docker-compose up -d
   ```
2. Connect to the database:
   ```sh
   psql -h localhost -U postgres -d etherscan
   ```

## Example JSON Output
```json
[
  {
    "hash": "0x123abc...",
    "status": "Success",
    "block": 21442021,
    "timestamp": 1739553046,
    "from": "0xabc...",
    "to": "0xdef...",
    "value": 1.5,
    "transaction_fee": 0.00042,
    "gasUsed": 21000,
    "gasPrice": 20000000000,
    "method": "0x12345678",
    "sponsored": "N/A"
  }
]
```

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Commit changes (`git commit -m "Add new feature"`)
4. Push to GitHub (`git push origin feature-name`)
5. Open a pull request

## License
This project is licensed under the MIT License.

## Contact
For questions or suggestions, please open an issue or contact the repository owner.

