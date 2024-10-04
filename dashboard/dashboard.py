import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
import json
from urllib.request import urlopen
with urlopen('https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson') as response:
 Brazil = json.load(response)

sns.set_theme(style='dark')

def create_time_orders(df:pd.DataFrame):
    return df.resample(rule='D', on='order_purchase_timestamp').size().reset_index(name='item_orders')

def create_product_category(df:pd.DataFrame):
    return df.groupby(by="product_category_name_english").size().reset_index(name='product_order')

def create_customer_state_df(df:pd.DataFrame):
    return df[['customer_id', 'customer_state']].drop_duplicates().groupby('customer_state').size().reset_index(name='customers').sort_values(by="customers", ascending=False)

all_df = pd.read_csv("all_data.csv")

all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])


min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # # Menambahkan logo perusahaan
    # st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]


time_orders = create_time_orders(main_df)
product_category = create_product_category(main_df)
customer_state_df = create_customer_state_df(main_df)

st.header('Brazil E-commerce Dashboard')
st.subheader('Daily Orders')
total_orders = time_orders.item_orders.sum()
st.metric("Total orders", value=total_orders)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    time_orders["order_purchase_timestamp"],
    time_orders["item_orders"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader("Best & Worst Performing Product")

best_category = product_category.sort_values(by='product_order', ascending=False).head()
worst_category = product_category.sort_values(by='product_order').head()

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="product_order", y="product_category_name_english", data=best_category, palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="product_order", y="product_category_name_english", data=worst_category, palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.subheader("Customer Locations")

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customers", 
    y="customer_state",
    data=customer_state_df.head(10),
    palette=colors,
    ax=ax
)
ax.set_title("Number of Customer by States", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

fig = px.choropleth(
    customer_state_df,       
    locations='customer_state',
    geojson=Brazil,
    featureidkey='properties.sigla',
    color='customers',
    hover_name='customer_state',
    color_continuous_scale='Blues',
    title='Map of Item Orders Occurrences by State (Brazil) 2017')

fig.update_layout(
    title={
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
)
fig.update_traces(hovertemplate="%{z}<extra></extra>")
fig.update_geos(fitbounds="locations", visible=False)
st.plotly_chart(fig)