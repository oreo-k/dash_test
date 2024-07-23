import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_table
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import random

# サンプルデータを20行に拡大し、時間軸を追加
start_date = datetime.now()
data = {
    "Amount01": [random.randint(1, 10) for _ in range(20)],
    "Amount02": [random.randint(1, 5) for _ in range(20)],
    "Category": ["A", "A", "A", "B", "B", "B", "C", "C", "C", "C",
             "A", "A", "A", "B", "B", "B", "C", "C", "C", "C"],
    "Time": [start_date + timedelta(days=i) for i in range(20)]
}

df = pd.DataFrame(data)
df['Selected'] = 'False'

# 時間軸をUNIXタイムスタンプに変換
df["Timestamp"]=df["Time"].apply(lambda x: x.timestamp())

# Dashアプリケーションのインスタンスを作成
app = dash.Dash(__name__)

# アプリケーションのレイアウトを定義
app.layout = html.Div(children=[
    html.H1(children='Data Table with Scroll and Checkbox Filter'),

    dcc.RangeSlider(
        id='time-slider',
        min=df['Timestamp'].min(),
        max=df['Timestamp'].max() + 1,
        step=1,
        marks={i: datetime.fromtimestamp(i).strftime('%Y-%m-%d') for i in range(int(df['Timestamp'].min()), int(df['Timestamp'].max()), 86400)},
        value=[df['Timestamp'].min(), df['Timestamp'].max()]
    ),

    dash_table.DataTable(
        id='table_show',
        columns=[
            {'name': 'Selected', 'id': 'Selected', 'type': 'text', 'editable': True},
            {'name': 'Amount01', 'id': 'Amount01'},
            {'name': 'Amount02', 'id': 'Amount02'},
            {'name': 'Category', 'id': 'Category'},
            {'name': 'Time', 'id': 'Time'}
        ],
        data=df.to_dict('records'),
        editable=True,
        row_selectable='multi',
        selected_rows=[],
        fixed_rows={'headers': True},
        style_table={'height': '400px', 'overflowY': 'auto'},
        style_cell_conditional=[
            {
                'if': {'column_id': 'Selected'},
                'width': '10%',
                'textAlign': 'center'
            },

            {
                'if': {'column_id': 'Amount01'},
                'width': '20%',
                'textAlign': 'center'
            },

            {
                'if': {'column_id': 'Amount02'},
                'width': '20%',
                'textAlign': 'center'
            },
            {
                'if': {'column_id': 'Category'},
                'width': '20%',
                'textAlign': 'center'
            },
            {
                'if': {'column_id': 'Time'},
                'width': '30%',
                'textAlign': 'center'
            }
        ],
    ),

    html.Button('Unselect All', id='unselect-all-button', n_clicks=0),
    html.Button('Select All', id="select-all-button", n_clicks=0),
    html.Button('Filter', id='filter-button', n_clicks=0),

    dcc.Graph(
        id='filtered-graph'
    )
])

# コールバックを定義
@app.callback(
    [Output('table_show', 'data'),
     Output('table_show', 'selected_rows'),
     Output('filtered-graph', 'figure')],
    [Input('table_show', 'selected_rows'),
     Input('unselect-all-button', 'n_clicks'),
     Input('select-all-button', 'n_clicks'),
     Input('filter-button', 'n_clicks'),
     Input('time-slider', 'value')],
    [State('table_show', 'data'),]
)
def update_table(selected_rows, unselect_n_clicks, select_n_clicks, filter_n_clicks, slider_range, rows):
    ctx = dash.callback_context

    # Determine which input triggered the callback
    if not ctx.triggered:
        return rows, dash.no_update, px.scatter()

    input_id = ctx.triggered[0]['prop_id'].split('.')[0]

    start_timestamp, end_timestamp = slider_range
    filtered_df = df[(df['Timestamp'] >= start_timestamp) & (df['Timestamp'] <= end_timestamp)]

    if input_id == 'table_show':
        for i in range(len(rows)):
            if i in selected_rows:
                rows[i]['Selected'] = 'True'
            else:
                rows[i]['Selected'] = 'False'
        return rows, selected_rows, dash.no_update

    elif input_id == 'unselect-all-button':
        for i in range(len(rows)):
            rows[i]['Selected'] = 'False'
        return rows, [], dash.no_update

    elif input_id == 'select-all-button':
        for i in range(len(rows)):
            rows[i]['Selected'] = 'True'
        return rows, list(range(len(rows))), dash.no_update

    elif input_id == 'filter-button':
        filtered_df = pd.DataFrame(rows)
        selected_df = filtered_df[filtered_df['Selected'] == 'True']
        if not selected_df.empty:
            fig = px.scatter(selected_df, x='Time', y='Amount01', color='Category', title='Selected Data Over Time')
        else:
            fig = px.scatter(filtered_df, x='Time', y='Amount01', color='Category', title='All Data Over Time')
        return rows, dash.no_update, fig

    return rows, dash.no_update, px.scatter()

# サーバーを起動
if __name__ == '__main__':
    app.run_server(debug=True)
