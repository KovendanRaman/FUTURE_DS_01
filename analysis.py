import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Sales Performance Dashboard", layout="wide")
st.markdown("""
<style>
/* Style the metric containers to look like a dark-mode BI tool */
div[data-testid="metric-container"] {
    background-color: #1c2333;
    border: 1px solid #2e3b52;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

st.title(" Business Sales Performance Analytics")
st.markdown("Analyzing transnational e-commerce transaction data to identify revenue trends and top-performing metrics.")


@st.cache_data
def load_and_clean_data():
    df = pd.read_csv('online_retail.csv', encoding='unicode_escape')
    
    
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')] 
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]     
    df = df.dropna(subset=['CustomerID'])  
    df = df[df['Country'] != 'Unspecified']                   
   
   
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['TotalRevenue'] = df['Quantity'] * df['UnitPrice']
    df['Month_Year'] = df['InvoiceDate'].dt.to_period('M').astype(str)
    
    return df

with st.spinner("Loading and cleaning data..."):
    sales_data = load_and_clean_data()

st.divider()
st.subheader("Dashboard Filters")


country_options = sales_data['Country'].unique().tolist()

selected_countries = st.multiselect(
    "Select Regions to Analyze:",
    options=country_options,
    default=country_options 
)


if not selected_countries:
    st.warning("Please select at least one country to view data.")
    st.stop()


filtered_data = sales_data[sales_data['Country'].isin(selected_countries)]


st.header("Executive Summary")
col1, col2, col3 = st.columns(3)

total_revenue = filtered_data['TotalRevenue'].sum()
total_orders = filtered_data['InvoiceNo'].nunique()
top_country = filtered_data.groupby('Country')['TotalRevenue'].sum().idxmax()

col1.metric("Total Revenue", f"£{total_revenue:,.2f}")
col2.metric("Total Unique Orders", f"{total_orders:,}")
col3.metric("Top Region", top_country)


st.divider()
st.subheader("Raw Data Preview")
st.dataframe(filtered_data.head(100))


st.divider()
st.subheader("Revenue Trends")
monthly_revenue = filtered_data.groupby('Month_Year')['TotalRevenue'].sum().reset_index()

fig_line = px.line(monthly_revenue, x='Month_Year', y='TotalRevenue', 
                   template='plotly_dark', markers=True)
fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                       margin=dict(l=0, r=0, t=30, b=0))
fig_line.update_traces(line_color='#00B4D8', line_width=3)


st.plotly_chart(fig_line, width='stretch')


st.divider()
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Top 10 Products by Revenue")
    top_products = filtered_data.groupby('Description')['TotalRevenue'].sum().sort_values(ascending=False).head(10).reset_index()
    
    fig_bar1 = px.bar(top_products, x='TotalRevenue', y='Description', orientation='h', template='plotly_dark')
    fig_bar1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'})
    fig_bar1.update_traces(marker_color='#00B4D8')
    
    
    st.plotly_chart(fig_bar1, width='stretch')

with col_b:
    st.subheader("Regional Performance (Excl. UK)")
    regional_sales = filtered_data[filtered_data['Country'] != 'United Kingdom'].groupby('Country')['TotalRevenue'].sum().sort_values(ascending=False).head(10).reset_index()
    
    if not regional_sales.empty:
        fig_bar2 = px.bar(regional_sales, x='TotalRevenue', y='Country', orientation='h', template='plotly_dark')
        fig_bar2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'})
        fig_bar2.update_traces(marker_color='#FFB703') 
        
        
        st.plotly_chart(fig_bar2, width='stretch')
    else:
        st.info("No non-UK data available in the current selection.")

st.divider()
st.subheader("Key Business Insights & Recommendations")
st.markdown("""
* **Seasonality:** Revenue spikes significantly in Q4 (specifically November), indicating strong holiday-driven sales. **Recommendation:** Front-load marketing and ad spend in October to capture early holiday intent.
* **Product Concentration:** A small fraction of items, like the *White Hanging Heart T-Light Holder* and *Regency Cakestand*, drive the vast majority of revenue. **Recommendation:** Implement strict inventory priority alerts for top-10 historical performers to completely eliminate stockouts during peak seasons.
* **Global Expansion:** Outside of the dominant domestic UK market, EIRE (Ireland), the Netherlands, and Germany represent the highest-value regions. **Recommendation:** Run targeted, localized marketing campaigns and explore discounted shipping options in these top EU territories to increase conversion rates.
""")