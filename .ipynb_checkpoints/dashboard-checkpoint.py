import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
from datetime import datetime
import io

df = pd.read_csv('SCDB_2024_01_caseCentered_Citation.csv')
df['issueArea'] = df['issueArea'].astype('str')
df['decisionDirection'] = df['decisionDirection'].astype('str')
df['precedentAlteration'] = df['precedentAlteration'].astype('str')
df['issue'] = df['issue'].astype('str')
df['dateDecision'] = pd.to_datetime(df['dateDecision'])

# Initialize the Dash app with a custom stylesheet
app = dash.Dash(__name__, external_stylesheets=[
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap',
        'rel': 'stylesheet'
    }
])

# Custom CSS for the navy and white theme (unchanged)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background-color: #f0f8ff;
                color: #000080;
            }
            .banner {
                background-color: #000080;
                color: white;
                padding: 5px;
                padding-left: 25px;
                text-align: left;
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            .content {
                max-width: 2400px;
                margin: 0 auto;
                padding: 20px;
                background-color: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            .box {
                border: 1px solid #000080;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 20px;
                background-color: white;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .box h3 {
                color: #000080;
                border-bottom: 1px solid #000080;
                padding-bottom: 10px;
            }
            .Select-control {
                border-color: #000080;
            }
            .Select-menu-outer {
                border-color: #000080;
            }
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner th {
                background-color: #000080;
                color: white;
            }
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner td {
                background-color: white;
                color: #000080;
            }
            .chart-column {
                padding: 0 10px;
            }
            .filter-box {
                min-height: 725px;
            }
        </style>
    </head>
    <body>
        <div class="banner">Supreme Court Database</div>
        <div class="content">
            {%app_entry%}
        </div>
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

def create_box(title, content):
    return html.Div([
        html.H4(title, style = {'margin-top': '0', 'margin-bottom': '0'}),
        content
    ], className='box')

app.layout = html.Div([
    html.Div([
        html.Div([
            create_box("Filters", html.Div([
                html.Label("Date Range"),
                dcc.RangeSlider(
                    id='date-slider',
                    min=df['term'].min(),
                    max=df['term'].max(),
                    value=[df['term'].min(), df['term'].max()],
                    marks={int(df['term'].min()): {'label': str(df['term'].min())},
                           int(df['term'].max()): {'label': str(df['term'].max())}},
                    tooltip = {'always_visible':False, 'placement': 'bottom'},
                    step=1
                ),
                #html.Br(),
                html.Label("Issue Area"),
                dcc.Dropdown(
                    id='issueArea-dropdown',
                    options=[{'label': i, 'value': i} for i in df['issueArea'].unique()],
                    multi=True,
                    placeholder="Select Issue Area(s)"
                ),
                #html.Br(),
                html.Label("Decision Type"),
                dcc.Dropdown(
                    id='decisionType-dropdown',
                    options=[{'label': i, 'value': i} for i in df['decisionType'].unique()],
                    multi=True,
                    placeholder="Select Decision Type(s)"
                ),
                #html.Br(),
                html.Label("Decision Direction"),
                dcc.Dropdown(
                    id='decisionDirection-dropdown',
                    options=[{'label': i, 'value': i} for i in df['decisionDirection'].unique()],
                    multi=True,
                    placeholder="Select Decision Direction(s)"
                ),
                #html.Br(),
                html.Label("Issue"),
                dcc.Dropdown(
                    id='issue-dropdown',
                    options=[{'label': i, 'value': i} for i in df['issue'].unique()],
                    multi=True,
                    placeholder="Select Issue(s)"
                ),
                #html.Br(),
                html.Label("Chief Justice"),
                dcc.Dropdown(
                    id='chief-dropdown',
                    options=[{'label': i, 'value': i} for i in df['chief'].unique()],
                    multi=True,
                    placeholder="Select Chief Justice(s)"
                ),
                #html.Br(),
                html.Label("Precedent Alteration"),
                dcc.Dropdown(
                    id='precedentAlteration-dropdown',
                    options=[{'label': i, 'value': i} for i in df['precedentAlteration'].unique()],
                    multi=True,
                    placeholder="Select Precedent Alteration(s)"
                ),
                #html.Br(),
                html.Label("Table Variables"),
                dcc.Dropdown(
                    id='column-dropdown',
                    options=[{'label': i, 'value': i} for i in df.columns],
                    multi=True,
                    value=['caseId', 'term', 'chief', 'issueArea', 'decisionDirection'],
                    placeholder="Select Columns to Display"
                ),
                html.Br(),
                html.Center(html.Button("Download Data Table", id="btn_csv", style={'backgroundColor': '#000080', 'color': 'white', 'border': 'none', 'padding': '5px 5px', 'cursor': 'pointer', 'fontWeight': 'bold'})),
                dcc.Download(id="download-dataframe-csv"),
            ], style={}, className='filter-box')),
        ], style={'width': '15%', 'float': 'left', 'display': 'inline-block', 'verticalAlign': 'top'}, className='filter-box'),
        
        # Left column: Charts
        html.Div([
            create_box("Total Cases", dcc.Graph(id='time-series-chart')),
            create_box("Trend Over Time", 
                html.Div([
                    dcc.Dropdown(
                        id='line-plot-variable',
                        options=[{'label': i, 'value': i} for i in ['certReason', 'chief', 'decisionDirection', 'issueArea', 'partyWinning', 'precedentAlteration']],
                        value='decisionDirection',
                        clearable=False
                    ),
                    dcc.Graph(id='line-plot')
                ])
            ),              
        ], style={'width': '41%', 'float':'center', 'display': 'inline-block', 'verticalAlign': 'top'}, className='chart-column'),
        
        # Right column: Table and chart
        html.Div([
            create_box("Data Table", dash_table.DataTable(
                id='data-table',
                columns=[{"name": i, "id": i} for i in ['caseId', 'term', 'issueArea', 'majVotes', 'decisionDirection']],
                data=df.to_dict('records'),
                page_size=10,
                style_table={'height': '250px', 'overflowY': 'auto'},
                filter_action="native",
                sort_action="native",
                style_cell={'backgroundColor': 'white', 'color': '#000080', 'fontSize':16, 'font-family':'sans-serif'},
                style_header={'backgroundColor': '#000080', 'color': 'white', 'fontWeight': 'bold'},
            )),
            create_box("Count Distribution", 
                html.Div([
                dcc.Dropdown(
                    id='bar-plot-variable',
                    options=[{'label': i, 'value': i} for i in ['certReason', 'chief', 'decisionDirection', 'issue', 'issueArea', 'partyWinning', 'precedentAlteration', 'majOpinWriter']],
                    value='issueArea',
                    clearable=False
                ),
                dcc.Graph(id='bar-plot')
            ]),
            ),     
        ], style={'width': '41%', 'float': 'right', 'display': 'inline-block', 'verticalAlign': 'top'}, className='chart-column'),
    ], style={'height':'1000px'}),
])


@app.callback(
    Output('time-series-chart', 'figure'),
    Output('bar-plot', 'figure'),
    Output('line-plot', 'figure'),
    Output('data-table', 'data'),
    Output('data-table', 'columns'),
    Input('date-slider', 'value'),
    Input('issueArea-dropdown', 'value'),
    Input('decisionType-dropdown', 'value'),
    Input('decisionDirection-dropdown', 'value'),
    Input('issue-dropdown', 'value'),
    Input('chief-dropdown', 'value'),
    Input('precedentAlteration-dropdown', 'value'),
    Input('column-dropdown', 'value'),
    Input('bar-plot-variable', 'value'),
    Input('line-plot-variable', 'value')
)
def update_dashboard(date_range, selected_areas, selected_decision_types, selected_decision_directions, 
                     selected_issues, selected_chiefs, selected_precedent_alterations, selected_columns,
                     bar_plot_variable, line_plot_variable):
    dff = df.copy()
    
    # Apply date filter
    start_date = date_range[0]
    end_date = date_range[1]
    dff = dff[(dff['term'] >= start_date) & (dff['term'] <= end_date)]
    
    # Apply filters
    if selected_areas:
        dff = dff[dff['issueArea'].isin(selected_areas)]
    if selected_decision_types:    
        dff = dff[dff['decisionType'].isin(selected_decision_types)]
    if selected_decision_directions:
        dff = dff[dff['decisionDirection'].isin(selected_decision_directions)]
    if selected_issues:
        dff = dff[dff['issue'].isin(selected_issues)]
    if selected_chiefs:
        dff = dff[dff['chief'].isin(selected_chiefs)]
    if selected_precedent_alterations:
        dff = dff[dff['precedentAlteration'].isin(selected_precedent_alterations)]
    
    # Create a copy for the table (ungrouped data)
    table_data = dff.copy()
    
    # Group by year for the time series chart
    time_series_counts = dff.groupby('term').size().reset_index(name='count')
    
    # Create time series chart
    fig_time_series = px.line(time_series_counts, x='term', y='count', title='', height=300)
    fig_time_series.update_xaxes(tickformat="%Y")
    fig_time_series.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='#000080',
        font=dict(size=18, family="Roboto, sans-serif", weight="bold"),
        xaxis = dict(tickfont = dict(size=14, weight='normal')),
        yaxis = dict(tickfont = dict(size=14, weight='normal')),
        xaxis_title="Year",
        yaxis_title="Number of Cases",
        margin=dict(l=0, r=0, b=0, t=0, pad=0)
    )
    
    # Create bar plot with larger, bold labels
    bar_data = dff[dff[bar_plot_variable] != 'nan']  # Exclude NaN values
    bar_data = dff[dff[bar_plot_variable].notna()]
    bar_counts = bar_data[bar_plot_variable].value_counts().reset_index()
    bar_counts.columns = [bar_plot_variable, 'count']
    fig_bar = px.bar(bar_counts, x=bar_plot_variable, y='count', title='', height=300)
    fig_bar.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='#000080',
        font=dict(size=18, family="Roboto, sans-serif", weight="bold"),
        xaxis = dict(tickfont = dict(size=14, weight='normal')),
        yaxis = dict(tickfont = dict(size=14, weight='normal')),
        xaxis_title=bar_plot_variable,
        yaxis_title="Number of Cases",
        margin=dict(l=0, r=0, b=0, t=0, pad=0)
    )

    line_data = dff[dff[line_plot_variable] != 'nan']
    line_data = line_data[line_data[line_plot_variable].notna()]
    line_data = line_data.groupby(['term', line_plot_variable]).size().reset_index(name='count')
    fig_line = px.line(line_data, x='term', y='count', color=line_plot_variable, title='', height=300)
    fig_line.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='#000080',
        font=dict(size=18, family="Roboto, sans-serif", weight="bold"),
        xaxis = dict(tickfont = dict(size=14, weight='normal')),
        yaxis = dict(tickfont = dict(size=14, weight='normal')),
        xaxis_title="Year",
        yaxis_title="Number of Cases",
        legend_title='',
        margin=dict(l=0, r=0, b=0, t=0, pad=0)
    )
    fig_line.update_traces(mode='lines+markers')  # Add markers to the lines for better readability
    
    # Update columns based on selected values from dropdown
    table_columns = [{"name": i, "id": i} for i in selected_columns]
    
    return fig_time_series, fig_bar, fig_line, table_data[selected_columns].to_dict('records'), table_columns

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    State('data-table', 'data'),
    prevent_initial_call=True,
)
def func(n_clicks, data):
    dff = pd.DataFrame(data)
    return dcc.send_data_frame(dff.to_csv, "filtered_dashboard_data.csv")

if __name__ == '__main__':
    app.run_server(debug=True)