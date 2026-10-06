# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
customers = pd.read_csv(BASE_DIR/"data"/"customers.csv")
products = pd.read_csv(BASE_DIR/"data"/"products.csv")
orders = pd.read_csv(BASE_DIR/"data"/"orders.csv")
orders["payment_method"] = orders["payment_method"].str.strip().str.upper()
orders_clean = orders.drop_duplicates(subset = ["customer_id", "product_id",
                            "order_date", "quantity",
                            "discount_pct", "payment_method", "rating", "returned"], keep = "first").copy()
orders_clean["discount_pct"] = orders_clean["discount_pct"].fillna(0)
orders_clean["rating"] = orders_clean["rating"].fillna(orders_clean["rating"].median())
merged_data = pd.merge(pd.merge(orders_clean,products, on = "product_id"),customers, on = "customer_id")
merged_data["order_value"] = merged_data["quantity"] * merged_data["price"] * (1 - merged_data["discount_pct"]/100)
Q1 = merged_data["quantity"].quantile(0.25)
Q3 = merged_data["quantity"].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
outliers = merged_data[(merged_data["quantity"] < lower) | (merged_data["quantity"] > upper)].copy()
merged_data["is_outlier"] = (merged_data["quantity"] < lower) | (merged_data["quantity"] > upper)

merged_data["order_date_time"] = pd.to_datetime(merged_data["order_date"],dayfirst=True )
merged_data["year_month"] = merged_data["order_date_time"].dt.to_period("M")
return_rate_by_payment = merged_data.groupby("payment_method")["returned"].agg(["count","mean"]).reset_index()[["payment_method","mean"]]
return_rate_by_payment["return_rate"] = (return_rate_by_payment["mean"]*100).round(2)
return_rate_by_payment =return_rate_by_payment.sort_values("return_rate", ascending=False)
plt.figure(figsize = (8,6))
bars = plt.bar(x = return_rate_by_payment["payment_method"] ,
            height = return_rate_by_payment["return_rate"],
            color = ["#F5B7B1", "#D7BDE2", "#A9DFBF"])
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height:.2f}%",
        ha="center",
        va="bottom"
    )
plt.title("COD Returns at 44.4% — 3x Card")
plt.xlabel("Payment Method")
plt.ylabel("Return Rate (%)")
plt.tight_layout()
plt.savefig(BASE_DIR/"visualizations"/"return_rate_by_payment.png")
monthly_revenue_trend = merged_data[merged_data["is_outlier"] == False].copy()
monthly_revenue_trend["order_date_time"] = pd.to_datetime(monthly_revenue_trend["order_date_time"])
monthly_revenue_trend["month"] = monthly_revenue_trend["order_date_time"].dt.month_name()
monthly_revenue_trend = monthly_revenue_trend.groupby(monthly_revenue_trend["month"])["order_value"].agg("sum")
monthly_revenue_trend = monthly_revenue_trend.reset_index()
months = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

monthly_revenue_trend["month"] = pd.Categorical(
    monthly_revenue_trend["month"],
    categories=months,
    ordered=True
)

monthly_revenue_trend = monthly_revenue_trend.sort_values("month")
peak_idx = monthly_revenue_trend["order_value"].idxmax()
peak_month = monthly_revenue_trend.loc[peak_idx, "month"]
peak_revenue = monthly_revenue_trend.loc[peak_idx, "order_value"]
plt.figure(figsize = (10,10))
plt.plot( monthly_revenue_trend["month"],
          monthly_revenue_trend["order_value"],
          marker = "o")
# Highlight peak
plt.scatter(
    peak_month,
    peak_revenue,
    color="red",
    s=100,
    zorder=5
)
# Label peak
plt.annotate(
    f"Peak: {peak_month}\n₹{peak_revenue:,.2f}",
    xy=(peak_month, peak_revenue),
    xytext=(10, 5),
    textcoords="offset points"
)
plt.xlabel("Month")
plt.ylabel("Revenue (₹)")
plt.title(f"Monthly Revenue — Peak: {peak_month}")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(BASE_DIR/"visualizations"/"monthly_revenue_trend.png")


