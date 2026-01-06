# main.py
from utils.file_handler import *
from utils.data_processor import *
from utils.api_handler import *
from datetime import datetime
import os

def main():
    try:
        print("=" * 40)
        print("SALES ANALYTICS SYSTEM")
        print("=" * 40)

        # Step 1: Read file
        raw = read_sales_data("data/sales_data.txt")

        # Step 2: Parse & clean
        parsed = parse_transactions(raw)

        # Step 3: Filtering
        choice = input("Do you want to filter data? (y/n): ").lower()
        region = None
        if choice == "y":
            region = input("Enter region: ")

        valid, invalid, summary = validate_and_filter(parsed, region)
        print(f"Valid: {len(valid)} | Invalid: {invalid}")

        # Step 4: API integration
        api_products = fetch_all_products()
        mapping = create_product_mapping(api_products)

        # Step 5: Enrichment
        enriched = enrich_sales_data(valid, mapping)
        save_enriched_data(enriched)

        # ✅ STEP 6: REPORT GENERATION (THIS WAS MISSING)
        print("[9/10] Generating report...")
        generate_sales_report(valid, enriched)
        print("✓ Report saved to: output/sales_report.txt")

        print("[10/10] Process Complete!")
        print("=" * 40)

    except Exception as e:
        print("❌ ERROR:", str(e))


if __name__ == "__main__":
    main()
