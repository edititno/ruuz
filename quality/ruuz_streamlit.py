# Ruuz Data Quality Dashboard v1.0
# Visual report for the data quality scoring tool

import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title='Ruuz Quality Report', layout='wide')
st.title('Ruuz Data Quality Report')
st.markdown('Merchant readiness analysis for contextual commerce')
st.markdown('---')

CSV_FILE = 'products_export_1.csv'

def safe_col(df, col):
    return df[col] if col in df.columns else pd.Series([None] * len(df))

def is_empty(val):
    if pd.isna(val):
        return True
    s = str(val).strip()
    return s == '' or s.lower() == 'nan'

if not os.path.exists(CSV_FILE):
    st.error(f'{CSV_FILE} not found. Export your products from Shopify admin first.')
    st.stop()

df = pd.read_csv(CSV_FILE)
products = df.groupby('Handle').first().reset_index()
total = len(products)

# Run all checks
checks = []

def check(label, failures, weight, tier):
    checks.append({
        'label': label,
        'failures': failures,
        'passed': total - len(failures),
        'weight': weight,
        'tier': tier
    })

check('Missing images', products[safe_col(products, 'Image Src').isna()], 10, 'critical')
check('Thin descriptions', products[safe_col(products, 'Body (HTML)').apply(lambda x: is_empty(x) or len(str(x)) < 20)], 10, 'critical')
check('Missing price', products[safe_col(products, 'Variant Price').apply(lambda x: is_empty(x) or float(x or 0) == 0)], 10, 'critical')
check('Unpublished products', products[safe_col(products, 'Published').astype(str).str.lower() == 'false'], 10, 'critical')
check('Missing tags', products[safe_col(products, 'Tags').apply(is_empty)], 7, 'high')
check('Missing product type', products[safe_col(products, 'Type').apply(is_empty)], 7, 'high')
check('Missing vendor', products[safe_col(products, 'Vendor').apply(is_empty)], 7, 'high')
check('Missing SKU', products[safe_col(products, 'Variant SKU').apply(is_empty)], 7, 'high')
check('Missing inventory tracking', products[safe_col(products, 'Variant Inventory Tracker').apply(is_empty)], 7, 'high')
check('Missing SEO title', products[safe_col(products, 'SEO Title').apply(is_empty)], 7, 'high')
check('Missing SEO description', products[safe_col(products, 'SEO Description').apply(is_empty)], 7, 'high')
check('Missing weight', products[safe_col(products, 'Variant Grams').apply(lambda x: is_empty(x) or float(x or 0) == 0)], 5, 'medium')
check('Missing compare-at price', products[safe_col(products, 'Variant Compare At Price').apply(is_empty)], 5, 'medium')
check('Missing barcode', products[safe_col(products, 'Variant Barcode').apply(is_empty)], 3, 'minor')
check('Missing product category', products[safe_col(products, 'Product Category').apply(is_empty)], 3, 'minor')
check('Duplicate titles', products[products.duplicated(subset='Title', keep=False)], 3, 'minor')

# Score
total_weight = sum(c['weight'] for c in checks)
earned = sum(c['weight'] for c in checks if len(c['failures']) == 0)
score = round((earned / total_weight) * 100)
passed = sum(1 for c in checks if len(c['failures']) == 0)

# Header stats
col1, col2, col3, col4 = st.columns(4)
col1.metric('Readiness Score', f'{score}%')
col2.metric('Products Analyzed', total)
col3.metric('Checks Passed', f'{passed}/{len(checks)}')
col4.metric('Issues Found', sum(1 for c in checks if len(c['failures']) > 0))

# Score color
if score >= 80:
    st.success(f'Your store is nearly ready for contextual commerce.')
elif score >= 60:
    st.warning(f'Your store needs work before fully benefiting from contextual commerce.')
else:
    st.error(f'Your store needs significant setup.')

st.markdown('---')

# Tiered issues
tab1, tab2, tab3, tab4 = st.tabs(['Critical', 'High Priority', 'Medium', 'Minor'])

for tab, tier, label in [(tab1, 'critical', 'Critical Issues'),
                          (tab2, 'high', 'High Priority Issues'),
                          (tab3, 'medium', 'Medium Priority Issues'),
                          (tab4, 'minor', 'Minor Issues')]:
    with tab:
        tier_checks = [c for c in checks if c['tier'] == tier]
        for c in tier_checks:
            status = 'PASS' if len(c['failures']) == 0 else 'FAIL'
            if len(c['failures']) == 0:
                st.success(f"[PASS] {c['label']}")
            else:
                st.error(f"[FAIL] {c['label']}: {len(c['failures'])} product(s)")
                with st.expander(f"View affected products"):
                    for _, row in c['failures'].iterrows():
                        st.write(f"- {row['Title']}")

st.markdown('---')

# All products table
st.markdown('### All Products')
display_cols = ['Title', 'Vendor', 'Type', 'Published']
available = [c for c in display_cols if c in products.columns]
st.dataframe(products[available], use_container_width=True)

st.markdown(f'*Dashboard v1.0 — {total} products analyzed across {len(checks)} quality checks*')