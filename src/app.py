import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Cyber Resilience Dashboard', layout='wide')

@st.cache_data
def load_data(path):
    return pd.read_excel(path, engine='openpyxl')

data_path = 'data/cleaned_data_cyber_binary.xlsx'
df = load_data(data_path)

df['Cyber Resilience'] = df['Cyber Resilience'].astype(str).str.strip()

st.sidebar.header('Filters')
size_options = ['All'] + sorted(df['Business Size'].dropna().unique())
sector_options = ['All'] + sorted(df['Business Sector'].dropna().unique())
selected_size = st.sidebar.selectbox('Business Size', size_options)
selected_sector = st.sidebar.selectbox('Business Sector', sector_options)

dim_prefix = {'ISU':'ISU:', 'CB':'CB:', 'AWM':'AWM:', 'CRF':'CRF:', 'CC':'CC:', 'SC':'SC:', 'CA':'CA:', 'FP':'FP:'}
all_dims = list(dim_prefix.keys())
selected_dims = st.sidebar.multiselect('Cyber Resilience Domains', all_dims, default=all_dims)

filt = df.copy()
if selected_size != 'All':
    filt = filt[filt['Business Size'] == selected_size]
if selected_sector != 'All':
    filt = filt[filt['Business Sector'] == selected_sector]

st.title('Cyber Resilience Comparison Dashboard')
st.subheader('Filtered Data Preview')
st.dataframe(filt.head())

if selected_dims:
    def pct_yes(group_df, cols):
        yes_counts = group_df[cols].sum().sum()
        total = len(group_df) * len(cols)
        return round(yes_counts / total * 100, 2) if total else 0

    size_rows = []
    for size, grp in filt.groupby('Business Size'):
        row = {'Business Size': size}
        for d in selected_dims:
            cols = [c for c in grp.columns if c.startswith(dim_prefix[d])]
            row[d] = pct_yes(grp, cols)
        size_rows.append(row)
    size_df = pd.DataFrame(size_rows)

    sector_rows = []
    for sector, grp in filt.groupby('Business Sector'):
        row = {'Business Sector': sector}
        for d in selected_dims:
            cols = [c for c in grp.columns if c.startswith(dim_prefix[d])]
            row[d] = pct_yes(grp, cols)
        sector_rows.append(row)
    sector_df = pd.DataFrame(sector_rows)

    st.subheader('Yes Percentage by Business Size')
    st.dataframe(size_df)
    st.subheader('Yes Percentage by Business Sector')
    st.dataframe(sector_df)

    if not size_df.empty:
        long_size = size_df.melt(id_vars='Business Size', var_name='Domain', value_name='Yes %')
        fig1 = px.line_polar(long_size, r='Yes %', theta='Domain', color='Business Size', line_close=True, template='plotly_dark', height=500)
        fig1.update_traces(fill='toself')
        st.subheader('Radar Chart – Business Size')
        st.plotly_chart(fig1, use_container_width=True)

    if not sector_df.empty:
        top_sectors = filt['Business Sector'].value_counts().nlargest(5).index
        plot_df = sector_df[sector_df['Business Sector'].isin(top_sectors)]
        long_sector = plot_df.melt(id_vars='Business Sector', var_name='Domain', value_name='Yes %')
        fig2 = px.line_polar(long_sector, r='Yes %', theta='Domain', color='Business Sector', line_close=True, template='plotly_dark', height=500)
        fig2.update_traces(fill='toself')
        st.subheader('Radar Chart – Top 5 Sectors')
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info('Select at least one domain to display results.')
