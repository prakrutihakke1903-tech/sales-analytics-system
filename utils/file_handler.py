# utils/file_handler.py
import codecs

def read_sales_data(filename):
    """
    Reads sales data handling encoding issues
    """
    encodings = ["utf-8", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            with codecs.open(filename, "r", encoding=enc, errors="strict") as file:
                lines = file.readlines()
                clean_lines = [
                    line.strip()
                    for line in lines[1:]
                    if line.strip()
                ]
                return clean_lines
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print("❌ File not found:", filename)
            return []
    print("❌ Unable to read file due to encoding issues")
    return []


def parse_transactions(raw_lines):
    transactions = []
    for line in raw_lines:
        parts = line.split("|")
        if len(parts) != 8:
            continue

        tid, date, pid, pname, qty, price, cid, region = parts

        pname = pname.replace(",", " ")
        qty = qty.replace(",", "")
        price = price.replace(",", "")

        try:
            transaction = {
                "TransactionID": tid,
                "Date": date,
                "ProductID": pid,
                "ProductName": pname.strip(),
                "Quantity": int(qty),
                "UnitPrice": float(price),
                "CustomerID": cid,
                "Region": region
            }
            transactions.append(transaction)
        except:
            continue
    return transactions


def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    valid = []
    invalid = 0
    regions = set(t["Region"] for t in transactions if "Region" in t)

    amounts = [t["Quantity"] * t["UnitPrice"] for t in transactions]
    print("Regions:", ", ".join(regions))
    print(f"Amount Range: ₹{min(amounts)} - ₹{max(amounts)}")

    for t in transactions:
        if (
            t["Quantity"] <= 0 or
            t["UnitPrice"] <= 0 or
            not t["TransactionID"].startswith("T") or
            not t["ProductID"].startswith("P") or
            not t["CustomerID"].startswith("C")
        ):
            invalid += 1
            continue

        amount = t["Quantity"] * t["UnitPrice"]
        if region and t["Region"] != region:
            continue
        if min_amount and amount < min_amount:
            continue
        if max_amount and amount > max_amount:
            continue

        valid.append(t)

    summary = {
        "total_input": len(transactions),
        "invalid": invalid,
        "final_count": len(valid)
    }

    return valid, invalid, summary
