import requests
import re


# -------------------------------
# FETCH PRODUCTS FROM API
# -------------------------------
def fetch_all_products():
    """
    Fetches all products from DummyJSON API
    Returns: list of product dictionaries
    """
    url = "https://dummyjson.com/products?limit=100"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("products", [])
    except Exception as e:
        print(f"⚠ API Error: {e}")
        return []


# -------------------------------
# CREATE PRODUCT MAPPING
# -------------------------------
def create_product_mapping(api_products):
    """
    Creates a mapping of product IDs to product info
    Returns: dictionary mapping numeric product IDs to API data
    """
    mapping = {}

    for product in api_products:
        product_id = product.get("id")

        if product_id is None:
            continue

        mapping[product_id] = {
            "title": product.get("title"),
            "category": product.get("category"),
            "brand": product.get("brand"),     # safe
            "rating": product.get("rating")    # safe
        }

    return mapping


# -------------------------------
# HELPER: EXTRACT NUMERIC PRODUCT ID
# -------------------------------
def extract_numeric_product_id(product_id):
    """
    Extracts numeric part from ProductID
    Example: P101 -> 101
    """
    match = re.search(r"\d+", str(product_id))
    return int(match.group()) if match else None


# -------------------------------
# ENRICH SALES DATA
# -------------------------------
def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information
    """
    enriched = []

    for tx in transactions:
        enriched_tx = tx.copy()
        numeric_id = extract_numeric_product_id(tx.get("ProductID"))

        if numeric_id and numeric_id in product_mapping:
            api_product = product_mapping[numeric_id]

            enriched_tx.update({
                "API_Category": api_product.get("category"),
                "API_Brand": api_product.get("brand"),
                "API_Rating": api_product.get("rating"),
                "API_Match": True
            })
        else:
            enriched_tx.update({
                "API_Category": None,
                "API_Brand": None,
                "API_Rating": None,
                "API_Match": False
            })

        enriched.append(enriched_tx)

    return enriched


# -------------------------------
# SAVE ENRICHED DATA TO FILE
# -------------------------------
def save_enriched_data(enriched_transactions, filename="data/enriched_sales_data.txt"):
    """
    Saves enriched transactions to a pipe-delimited file
    """
    if not enriched_transactions:
        print("⚠ No enriched transactions to save.")
        return

    headers = list(enriched_transactions[0].keys())

    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write("|".join(headers) + "\n")

            for tx in enriched_transactions:
                row = []
                for h in headers:
                    value = tx.get(h)
                    row.append("" if value is None else str(value))
                file.write("|".join(row) + "\n")

        print(f"✓ Enriched data saved to: {filename}")

    except Exception as e:
        print(f"⚠ File save error: {e}")
