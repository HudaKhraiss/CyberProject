
# cyber_dashboard_fixed.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Cyber Resilience Dashboard', layout='wide')

@st.cache_data
def load_data(path):
    return pd.read_excel(path)

data_path = 'data/cleaned_data_cyber_binary.xlsx'
df = load_data(data_path)

# Sidebar filters
st.sidebar.header('Filters')
size_options = ['All'] + sorted(df['Business Size'].dropna().unique())
sector_options = ['All'] + sorted(df['Business Sector'].dropna().unique())
selected_size = st.sidebar.selectbox('Business Size', size_options)
selected_sector = st.sidebar.selectbox('Business Sector', sector_options)

# Dimension prefixes (case-sensitive)
dim_prefix = {'ISU':'ISU:','CB':'CB:','AWM':'AWM:','CRF':'CRF:','CC':'CC:','CA':'CA:','FP':'FP:'}
all_dims = list(dim_prefix.keys())
selected_dims = st.sidebar.multiselect('Cyber Resilience Dimensions', all_dims, default=all_dims)

# Filter rows
filt = df.copy()
if selected_size!='All':
    filt = filt[filt['Business Size']==selected_size]
if selected_sector!='All':
    filt = filt[filt['Business Sector']==selected_sector]

st.title('Cyber Resilience Comparison Dashboard')
st.subheader('Filtered Data Preview')
st.dataframe(filt.head())

# Build comparison values
if selected_dims:
    comp = filt.copy()
    for d in selected_dims:
        cols = [c for c in comp.columns if c.startswith(dim_prefix[d])]
        comp[d] = comp[cols].mean(axis=1, numeric_only=True)
    table = comp.groupby('Cyber Resilience')[selected_dims].mean().reset_index()
    st.subheader('Average Scores by Resilience Level')
    st.write(table)

    # Long-form for Plotly
    long_df = table.melt(id_vars='Cyber Resilience', var_name='Dimension', value_name='Score')
    fig = px.line_polar(long_df, r='Score', theta='Dimension', color='Cyber Resilience', line_close=True,
                        template='plotly_dark', height=550)
    fig.update_traces(fill='toself')
    st.subheader('Spider Plot')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info('Select at least one dimension to display results.')
