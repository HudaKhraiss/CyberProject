import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, dash_table, Output, Input
import dash_bootstrap_components as dbc

# Load data
FILE_PATH = 'data/cleaned_data_cyber_binary.xlsx'
df = pd.read_excel(FILE_PATH, engine='openpyxl')
# keep Yes & No
df = df[df['Cyber Resilience'].isin(['Yes','No'])]

DOMAINS = ['ISU','CB','AWM','CRF','CC','SC','CA','FP']
DOMAINS_COLS = {d:[c for c in df.columns if c.startswith(d+':')] for d in DOMAINS}

def compute(group_col):
    rec = []
    for grp, gp in df.groupby(group_col):
        total = len(gp)
        row = {group_col:grp}
        for d in DOMAINS:
            cols = DOMAINS_COLS[d]
            pct = gp[cols].sum().sum()/(len(cols)*total)*100 if len(cols) else None
            row[d] = round(pct,2)
        rec.append(row)
    return pd.DataFrame(rec)

size_df = compute('Business Size')
sector_df = compute('Business Sector')

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H2('Cyber Resilience Dashboard'),
    dcc.Tabs([
        dcc.Tab(label='By Business Size', children=[
            dash_table.DataTable(id='size-table',
                                 columns=[{'name':c,'id':c} for c in size_df.columns],
                                 data=size_df.to_dict('records'),
                                 style_table={'overflowX':'auto'},
                                 page_size=10,
                                 row_selectable='multi'),
            dcc.Graph(id='size-radar')
        ]),
        dcc.Tab(label='By Business Sector', children=[
            dash_table.DataTable(id='sector-table',
                                 columns=[{'name':c,'id':c} for c in sector_df.columns],
                                 data=sector_df.to_dict('records'),
                                 style_table={'overflowX':'auto'},
                                 page_size=10,
                                 row_selectable='multi'),
            dcc.Graph(id='sector-radar')
        ])
    ])
])

@app.callback(Output('size-radar','figure'),
              [Input('size-table','derived_virtual_data'),
               Input('size-table','derived_virtual_selected_rows')])
def update_size(rows, selected):
    temp = pd.DataFrame(rows)
    if selected:
        temp = temp.iloc[selected]
    fig = go.Figure()
    for _, r in temp.iterrows():
        fig.add_trace(go.Scatterpolar(r=r[DOMAINS].tolist()+[r[DOMAINS[0]]],
                                      theta=DOMAINS+[DOMAINS[0]],
                                      name=r['Business Size']))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])),showlegend=True,title='Domains by Business Size')
    return fig

@app.callback(Output('sector-radar','figure'),
              [Input('sector-table','derived_virtual_data'),
               Input('sector-table','derived_virtual_selected_rows')])
def update_sector(rows, selected):
    temp = pd.DataFrame(rows)
    if selected:
        temp = temp.iloc[selected]
    fig = go.Figure()
    for _, r in temp.iterrows():
        fig.add_trace(go.Scatterpolar(r=r[DOMAINS].tolist()+[r[DOMAINS[0]]],
                                      theta=DOMAINS+[DOMAINS[0]],
                                      name=r['Business Sector']))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])),showlegend=True,title='Domains by Business Sector')
    return fig

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
