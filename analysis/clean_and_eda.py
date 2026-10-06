# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

"""# Task 1- Load and inspect"""
BASE_DIR = Path(__file__).resolve().parents[1]
customers = pd.read_csv(BASE_DIR/"data"/"customers.csv")
products = pd.read_csv(BASE_DIR/"data"/"products.csv")
orders = pd.read_csv(BASE_DIR/"data"/"orders.csv")

print("shape of orders : ",orders.shape)

"""# Task 2 - Standardize payment_method casing"""

print("Before the fix :",orders["payment_method"].unique())
orders["payment_method"] = orders["payment_method"].str.strip().str.upper()
print("After the fix :",orders["payment_method"].unique())

"""# Task 3 - Remove duplicate orders"""

duplicate_orders = orders.loc[orders.duplicated(subset = ["customer_id", "product_id",
                            "order_date", "quantity",
                            "discount_pct", "payment_method", "rating", "returned"], keep = "first")==True,["order_id"]]

orders_clean = orders.drop_duplicates(subset = ["customer_id", "product_id",
                            "order_date", "quantity",
                            "discount_pct", "payment_method", "rating", "returned"], keep = "first").copy()
print("5 dropped order_id values are:\n",duplicate_orders)
print(orders_clean.shape)

"""# Task 4 - Impute missing values"""

orders_clean["discount_pct"] = orders_clean["discount_pct"].fillna(0)
print(f"the median value for rating is : {orders_clean["rating"].median()} and {orders_clean["rating"].isnull().sum()} rows affected")
orders_clean["rating"] = orders_clean["rating"].fillna(orders_clean["rating"].median())
orders_clean[['discount_pct','rating']].isnull().sum()

"""# Task 5 - Merge and reconcile against Part1"""

merged_data = pd.merge(pd.merge(orders_clean,products, on = "product_id"),customers, on = "customer_id")
merged_data["order_value"] = merged_data["quantity"] * merged_data["price"] * (1 - merged_data["discount_pct"]/100)
merged_data_total_order_value = merged_data["order_value"].sum().round(2)
print("total = ",merged_data["order_value"].sum().round(2))
dropped_rows = duplicate_orders.merge(orders,on = "order_id",how = "left").merge(products, on = "product_id", how = "left")
dropped_rows["order_value"] = dropped_rows["quantity"] * dropped_rows["price"] * (1 - dropped_rows["discount_pct"]/100)
dropped_rows_total_order_value = dropped_rows["order_value"].sum().round(2)
reconciliation_note = f'''The total revenue after cleaning the data is {merged_data_total_order_value},
which is lesser than the calculated value from SQL 99860.20.
The reason for the difference in the values is the dropped rows, which sums up the order value to
{dropped_rows_total_order_value} which is the exact difference observed.'''
print(f"{reconciliation_note}")

"""# Task 6 - IQR outlier detection on quantity"""

Q1 = merged_data["quantity"].quantile(0.25)
Q3 = merged_data["quantity"].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
outliers = merged_data[(merged_data["quantity"] < lower) | (merged_data["quantity"] > upper)].copy()
print("outliers : \n",outliers[["order_id","quantity"]])
merged_data["is_outlier"] = (merged_data["quantity"] < lower) | (merged_data["quantity"] > upper)

"""# Task 7 -  Hypothesis: does COD have a higher return rate?"""

print("Hypothesis: does COD have a higher return rate?")
hypothesis = merged_data.groupby("payment_method")["returned"].agg(["count","mean"])
payment_methods = ["CARD","COD","UPI"]
for payment in payment_methods :
    print(f"{payment}: {(hypothesis.loc[payment,'mean']*100).round(1)}%")
cod_rate = hypothesis.loc["COD", "mean"]
other_rates = hypothesis.loc[["CARD", "UPI"], "mean"]
if(cod_rate > other_rates.max()):
    print(f"Hypothesis : Confirmed")
else:
    print(f"Hypothesis : Busted")

"""# Task 8 - Multi-level segmentation"""

seg_data = merged_data.groupby(["payment_method","city_tier"])["returned"].agg(["count","mean"])
COD_Tier1 = (seg_data.loc[("COD",1),"mean"]*100).round(1)
COD_Tier2 = (seg_data.loc[("COD",2),"mean"]*100).round(1)
Highest_risk_segment = f'''The COD risk is not uniform across tiers.
Below is the segmentation that shows COD risk is not uniform across tiers:
{seg_data.loc["COD",["count","mean"]]}
{seg_data.loc[("COD",1),"count"]} Tier-1 COD orders at {COD_Tier1}%.
{seg_data.loc[("COD",2),"count"]} Tier-2 COD orders at {COD_Tier2}%
Our segmentation shows that single highest-risk segment is COD + Tier-2 cities at {COD_Tier2}%'''
print(f"{Highest_risk_segment}")

"""# Task 9 - Correlation analysis"""

corr_matrix = merged_data[["rating", "returned", "discount_pct", "quantity"]].corr(numeric_only = True)
correlation_strength = '''(rating-returned) - negligible
(rating-discount_pct) - negligible
(rating-quantity) - negligible
(returned-discount_pct) - negligible
(returned-quantity) - negligible
quantity-discount_pct - negligible'''
print(correlation_strength)
print("Higher discounts reduce returns : Busted (discount_pct vs returned correlation ≈ -0.09)")

"""# Task 10 - Outlier-corrected time series"""

merged_data["order_date_time"] = pd.to_datetime(merged_data["order_date"],dayfirst=True )
merged_data["year_month"] = merged_data["order_date_time"].dt.to_period("M")
including_outliers = merged_data.groupby("year_month")["order_value"].agg("sum")
excluding_outliers = merged_data[merged_data["is_outlier"] == False].groupby("year_month")["order_value"].agg("sum")
print(f"Including the two outlier orders:\n {including_outliers}\n")
print(f"Excluding the two outlier orders:\n {excluding_outliers}")
mrge = merged_data.merge(outliers , on = "order_id")
print("\nJanuary's apparent lead is an artifact of the two bulk orders landing in January (O0011 on 2026-01-28, O0098 on 2026-01-10), and that March is the genuine peak month once they're excluded ")
print("The excluded orders:\n",mrge[mrge["year_month"]=="2026-01"][["order_id","order_date_y","order_value_y"]])

"""# Data Prep for part 3"""

reset_seg_data = seg_data.reset_index()
reset_excluding_outliers = excluding_outliers.reset_index()
reset_including_outliers = including_outliers.reset_index()
apparent_highest_revenue_month = reset_including_outliers.iloc[reset_including_outliers["order_value"].idxmax()]["year_month"]
json_data = {
    "cleaned_total_revenue_inr":  merged_data["order_value"].sum().round(2),
    "raw_total_revenue_inr": merged_data["order_value"].sum().round(2) + dropped_rows["order_value"].sum().round(2),
    "duplicate_reconciliation_delta_inr": dropped_rows["order_value"].sum().round(2),
    "return_rate_by_payment": {
        "COD":float((hypothesis.loc["COD","mean"]*100).round(2)),
        "CARD":float((hypothesis.loc["CARD","mean"]*100).round(2)),
        "UPI":float((hypothesis.loc["UPI","mean"]*100).round(2))
    } ,
    "highest_risk_segment": {
        "payment_method": reset_seg_data.iloc[reset_seg_data["mean"].idxmax()].loc["payment_method"],
        "city_tier": int(reset_seg_data.iloc[reset_seg_data["mean"].idxmax()].loc["city_tier"]),
        "return_rate_pct": float((reset_seg_data.iloc[reset_seg_data["mean"].idxmax()].loc["mean"]*100).round(1))
    },
    "true_peak_month": {
        "month": str(reset_excluding_outliers.iloc[reset_excluding_outliers["order_value"].idxmax()]["year_month"]),
        "revenue_inr": float(reset_excluding_outliers.iloc[reset_excluding_outliers["order_value"].idxmax()]["order_value"])
    },
    "outlier_inflated_month": {
        "month": str(reset_including_outliers.iloc[reset_including_outliers["order_value"].idxmax()]["year_month"]),
        "apparent_revenue_inr": float((reset_including_outliers.iloc[reset_including_outliers["order_value"].idxmax()]["order_value"]).round(2)),
        "corrected_revenue_inr": float(reset_excluding_outliers.loc[reset_excluding_outliers["year_month"] == apparent_highest_revenue_month]["order_value"].iloc[0])
    }
}
import json

with open(BASE_DIR/"narrator"/"findings.json", "w") as file:
    json.dump(json_data, file, indent=4)