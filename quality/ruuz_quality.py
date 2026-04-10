# Ruuz Data Quality Scoring Tool v2.1
# Comprehensive Shopify product export analysis with weighted scoring

import pandas as pd
import os

CSV_FILE = 'products_export_1.csv'

def safe_col(df, col):
    return df[col] if col in df.columns else pd.Series([None] * len(df))

def is_empty(val):
    if pd.isna(val):
        return True
    s = str(val).strip()
    return s == '' or s.lower() == 'nan'

def analyze_store():
    if not os.path.exists(CSV_FILE):
        print(f'Error: {CSV_FILE} not found.')
        return

    df = pd.read_csv(CSV_FILE)
    products = df.groupby('Handle').first().reset_index()
    total = len(products)

    print('=== Ruuz Data Quality Report v2.1 ===')
    print(f'Store: ruuz-dev.myshopify.com')
    print(f'Total products: {total}')
    print()

    results = []

    def check(label, failures, weight):
        results.append({
            'label': label,
            'failures': failures,
            'passed': total - len(failures),
            'weight': weight
        })

    # CRITICAL CHECKS (weight 10)
    check('Missing images', products[safe_col(products, 'Image Src').isna()], 10)
    check('Missing or thin descriptions',
          products[safe_col(products, 'Body (HTML)').apply(lambda x: is_empty(x) or len(str(x)) < 20)], 10)
    check('Missing price',
          products[safe_col(products, 'Variant Price').apply(lambda x: is_empty(x) or float(x or 0) == 0)], 10)
    check('Unpublished products',
          products[safe_col(products, 'Published').astype(str).str.lower() == 'false'], 10)

    # HIGH IMPORTANCE (weight 7)
    check('Missing tags', products[safe_col(products, 'Tags').apply(is_empty)], 7)
    check('Missing product type', products[safe_col(products, 'Type').apply(is_empty)], 7)
    check('Missing vendor', products[safe_col(products, 'Vendor').apply(is_empty)], 7)
    check('Missing SKU', products[safe_col(products, 'Variant SKU').apply(is_empty)], 7)
    check('Missing inventory tracking',
          products[safe_col(products, 'Variant Inventory Tracker').apply(is_empty)], 7)
    check('Missing SEO title', products[safe_col(products, 'SEO Title').apply(is_empty)], 7)
    check('Missing SEO description', products[safe_col(products, 'SEO Description').apply(is_empty)], 7)

    # MEDIUM IMPORTANCE (weight 5)
    check('Missing weight (breaks shipping)',
          products[safe_col(products, 'Variant Grams').apply(lambda x: is_empty(x) or float(x or 0) == 0)], 5)
    check('Missing compare-at price (no sale display)',
          products[safe_col(products, 'Variant Compare At Price').apply(is_empty)], 5)

    # LOW IMPORTANCE (weight 3)
    check('Missing barcode', products[safe_col(products, 'Variant Barcode').apply(is_empty)], 3)
    check('Missing product category', products[safe_col(products, 'Product Category').apply(is_empty)], 3)
    check('Duplicate titles', products[products.duplicated(subset='Title', keep=False)], 3)

    # Weighted score: full credit only if check fully passes
    total_weight = sum(r['weight'] for r in results)
    earned_weight = sum(r['weight'] for r in results if len(r['failures']) == 0)
    score = round((earned_weight / total_weight) * 100)

    print('=== CHECKS ===')
    critical = []
    warnings = []
    minor = []

    for r in results:
        status = '[PASS]' if len(r['failures']) == 0 else '[FAIL]'
        print(f"{status} {r['label']}: {r['passed']}/{total}")
        if len(r['failures']) > 0:
            if r['weight'] >= 10:
                critical.append(r)
            elif r['weight'] >= 5:
                warnings.append(r)
            else:
                minor.append(r)

    print()
    print(f'=== READINESS SCORE: {score}% ===')
    print()

    if critical:
        print('*** CRITICAL ISSUES (fix these first) ***')
        for r in critical:
            print(f"  {r['label']}: {len(r['failures'])} product(s)")
            for _, row in r['failures'].head(5).iterrows():
                print(f"     - {row['Title']}")
        print()

    if warnings:
        print('*** WARNINGS ***')
        for r in warnings:
            print(f"  {r['label']}: {len(r['failures'])} product(s)")
        print()

    if minor:
        print('*** MINOR ISSUES ***')
        for r in minor:
            print(f"  {r['label']}: {len(r['failures'])} product(s)")
        print()

    if score == 100:
        print('Your store is fully ready for contextual commerce.')
    elif score >= 80:
        print('Your store is nearly ready. Fix critical issues to reach 100%.')
    elif score >= 60:
        print('Your store needs work before it can fully benefit from contextual commerce.')
    else:
        print('Your store needs significant setup. Start with critical issues.')

if __name__ == '__main__':
    analyze_store()
