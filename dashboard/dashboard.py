import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
from babel.numbers import format_currency
sns.set(style='dark')

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("./data/all_data.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Main
main_df = all_df[(all_df["order_approved_at"] >= str(min_date)) & 
                 (all_df["order_approved_at"] <= str(max_date))]

def create_monthly_orders_df():
    monthly_orders_df = main_df.resample(rule='M', on='order_approved_at').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return monthly_orders_df

monthly_orders_df = create_monthly_orders_df()

def create_monthly_spend_df():
    monthly_spend_df = main_df.resample(rule='M', on='order_approved_at').agg({
        "payment_value": "sum"
    })
    monthly_spend_df = monthly_spend_df.reset_index()
    monthly_spend_df.rename(columns={
        "payment_value": "total_spend"
    }, inplace=True)
    return monthly_spend_df

monthly_spend_df = create_monthly_spend_df()

def create_sum_order_items_df():
    sum_order_items_df = main_df.groupby("product_category_name_english")["product_id"].count().reset_index()
    sum_order_items_df.rename(columns={
        "product_id": "product_count"
    }, inplace=True)
    sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)
    return sum_order_items_df

sum_order_items_df = create_sum_order_items_df()

# Title
st.header("Brazilian E-Commerce Public Dataset Analysis")

# Daily Orders
st.subheader("Monthly Orders")

col1, col2 = st.columns(2)

with col1:
    total_order = monthly_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = format_currency(monthly_orders_df["revenue"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Revenue: **{total_revenue}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    monthly_orders_df["order_approved_at"],
    monthly_orders_df["revenue"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Customer Spend Money
st.subheader("Monthly Customer Spend Money")
col1, col2 = st.columns(2)

with col1:
    total_spend = format_currency(monthly_spend_df["total_spend"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Spend: **{total_spend}**")

with col2:
    avg_spend = format_currency(monthly_spend_df["total_spend"].mean(), "IDR", locale="id_ID")
    st.markdown(f"Average Spend: **{avg_spend}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    monthly_spend_df["order_approved_at"],
    monthly_spend_df["total_spend"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Order Items
st.subheader("Order Items")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Items: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Average Items: **{avg_items}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

colors = ["#068DA9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Produk paling banyak terjual", loc="center", fontsize=50)
ax[0].tick_params(axis ='y', labelsize=35)
ax[0].tick_params(axis ='x', labelsize=30)

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk paling sedikit terjual", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)


st.subheader("Conclusions")

st.markdown("1. Produk mana yang memiliki order terbesar? dan Produk mana yang memiliki order terkecil?")
st.markdown("Berdasarkan data yang sudah diolah dan divisualisasikan pada sheet diatas, Maka di ketahui produk dengan perolehan order terbesar berada pada product dengan dengan category `Bed Bath Table`. Selain itu, Product dengan perolehan order terkecil berada pada product dengan category `security and services`")

st.markdown("2. Bagaimana performa penjualan platform E-commerce tersebut setiap bulannya?")
st.markdown("Berdasarkan Line Graph diatas, Penjualan pada platform E-commerce tersebut sangat fluktuatif. Akan tetapi, dapat terlihat bahwa terdapat peningkatan penjualan yang fantastis dari Bulan `September ke November`, Yakni terdapat **Puncak pembelian minimum** pada bulan `September` dan mencapai **Puncak pembelian maksimum** pada bulan `November`")

st.markdown("3. Berapa pengeluaran customer pada platform E-commerce dalam beberapa bulan terakhir?")
st.markdown("Berdasarkan data yang kita dapatkan dari pertanyaan sebelumnya, terdapat hubungan yang erat antara **Performa penjualan setiap bulan** dengan **pengeluaran customer beberapa bulan terakhir** dimana grafik yang ditujukan `Hampir Sama secara keseluruhan` antara satu sama lain yang mengartikan jumlah total pengeluaran customer sama dengan jumlah total pembelian produk setiap bulannya")