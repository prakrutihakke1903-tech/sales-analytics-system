import os
from datetime import datetime
from collections import defaultdict

def generate_sales_report(
    transactions,
    enriched_transactions,
    output_file="output/sales_report.txt"
):
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    total_transactions = len(transactions)
    total_revenue = sum(t["Quantity"] * t["UnitPrice"] for t in transactions)
    avg_order_value = total_revenue / total_transactions if total_transactions else 0

    dates = sorted(t["Date"] for t in transactions)
    start_date = dates[0] if dates else "N/A"
    end_date = dates[-1] if dates else "N/A"

    # ---------------- REGION ANALYSIS ----------------
    region_stats = defaultdict(lambda: {"revenue": 0, "count": 0})
    for t in transactions:
        amt = t["Quantity"] * t["UnitPrice"]
        region_stats[t["Region"]]["revenue"] += amt
        region_stats[t["Region"]]["count"] += 1

    # ---------------- PRODUCT ANALYSIS ----------------
    product_stats = defaultdict(lambda: {"qty": 0, "rev": 0})
    for t in transactions:
        product_stats[t["ProductName"]]["qty"] += t["Quantity"]
        product_stats[t["ProductName"]]["rev"] += t["Quantity"] * t["UnitPrice"]

    top_products = sorted(
        product_stats.items(),
        key=lambda x: x[1]["qty"],
        reverse=True
    )[:5]

    # ---------------- CUSTOMER ANALYSIS ----------------
    customer_stats = defaultdict(lambda: {"spent": 0, "count": 0})
    for t in transactions:
        amt = t["Quantity"] * t["UnitPrice"]
        customer_stats[t["CustomerID"]]["spent"] += amt
        customer_stats[t["CustomerID"]]["count"] += 1

    top_customers = sorted(
        customer_stats.items(),
        key=lambda x: x[1]["spent"],
        reverse=True
    )[:5]

    # ---------------- DAILY TREND ----------------
    daily = defaultdict(lambda: {"rev": 0, "count": 0, "customers": set()})
    for t in transactions:
        d = t["Date"]
        amt = t["Quantity"] * t["UnitPrice"]
        daily[d]["rev"] += amt
        daily[d]["count"] += 1
        daily[d]["customers"].add(t["CustomerID"])

    peak_day = max(daily.items(), key=lambda x: x[1]["rev"])

    # ---------------- API ENRICHMENT ----------------
    enriched_count = sum(1 for t in enriched_transactions if t.get("API_Match"))
    enrichment_rate = (enriched_count / len(enriched_transactions) * 100) if enriched_transactions else 0
    failed_products = sorted({
        t["ProductName"]
        for t in enriched_transactions
        if not t.get("API_Match")
    })

    # ---------------- WRITE REPORT ----------------
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 45 + "\n")
        f.write("SALES ANALYTICS REPORT\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Records Processed: {total_transactions}\n")
        f.write("=" * 45 + "\n\n")

        f.write("OVERALL SUMMARY\n")
        f.write("-" * 45 + "\n")
        f.write(f"Total Revenue: ₹{total_revenue:,.2f}\n")
        f.write(f"Total Transactions: {total_transactions}\n")
        f.write(f"Average Order Value: ₹{avg_order_value:,.2f}\n")
        f.write(f"Date Range: {start_date} to {end_date}\n\n")

        f.write("REGION-WISE PERFORMANCE\n")
        f.write("-" * 45 + "\n")
        for r, s in sorted(region_stats.items(), key=lambda x: x[1]["revenue"], reverse=True):
            pct = (s["revenue"] / total_revenue) * 100 if total_revenue else 0
            f.write(f"{r:<10} ₹{s['revenue']:>12,.2f}  {pct:>6.2f}%  {s['count']} txns\n")

        f.write("\nTOP 5 PRODUCTS\n")
        f.write("-" * 45 + "\n")
        for i, (p, s) in enumerate(top_products, 1):
            f.write(f"{i}. {p:<20} Qty: {s['qty']}  Rev: ₹{s['rev']:,.2f}\n")

        f.write("\nTOP 5 CUSTOMERS\n")
        f.write("-" * 45 + "\n")
        for i, (c, s) in enumerate(top_customers, 1):
            f.write(f"{i}. {c}  ₹{s['spent']:,.2f} ({s['count']} orders)\n")

        f.write("\nDAILY SALES TREND\n")
        f.write("-" * 45 + "\n")
        for d, s in sorted(daily.items()):
            f.write(f"{d}  ₹{s['rev']:,.2f}  {s['count']} txns  {len(s['customers'])} customers\n")

        f.write("\nPRODUCT PERFORMANCE\n")
        f.write("-" * 45 + "\n")
        f.write(f"Peak Sales Day: {peak_day[0]} (₹{peak_day[1]['rev']:,.2f})\n")

        f.write("\nAPI ENRICHMENT SUMMARY\n")
        f.write("-" * 45 + "\n")
        f.write(f"Enriched Records: {enriched_count}/{len(enriched_transactions)}\n")
        f.write(f"Success Rate: {enrichment_rate:.2f}%\n")
        if failed_products:
            f.write("Products Not Enriched:\n")
            for p in failed_products:
                f.write(f"- {p}\n")

    print(f"✓ Report saved to: {output_file}")
