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
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal", "NYC", "NYC", "NYC", "NYC",
             "SF", "SF", "SF", "Montreal", "Montreal", "Montreal", "NYC", "NYC", "NYC", "NYC"],
    "Time": [start_date + timedelta(days=i) for i in range(20)]
}

df = pd.DataFrame(data)
df['Selected'] = 'False'

# Dashアプリケーションのインスタンスを作成
app = dash.Dash(__name__)

# アプリケーションのレイアウトを定義
app.layout = html.Div(children=[
    html.H1(children='Data Table with Scroll and Checkbox Filter'),

    dash_table.DataTable(
        id='table_show',
        columns=[
            {'name': 'Selected', 'id': 'Selected', 'type': 'text', 'editable': True},
            {'name': 'Amount01', 'id': 'Amount01'},
            {'name': 'Amount02', 'id': 'Amount02'},
            {'name': 'City', 'id': 'City'},
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
                'if': {'column_id': 'City'},
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

    html.Button('Filter', id='filter-button', n_clicks=0),

    dcc.Graph(
        id='filtered-graph'
    )
])

# コールバックを定義

## table上の行が選択されたとき、選択された行のSelected列を更新
@app.callback(
    Output('table_show', 'data'),
    Input('table_show', 'selected_rows'),
    State('table_show', 'data')
)
def update_selected(selected_rows, rows):
    for i in range(len(rows)):
        if i in selected_rows:
            rows[i]['Selected'] = 'True'
        else:
            rows[i]['Selected'] = 'False'
    return rows

## Filterボタンがクリックされたとき、選択された行のデータをグラフに表示
@app.callback(
    Output('filtered-graph', 'figure'),
    Input('filter-button', 'n_clicks'),
    State('table_show', 'data')
)
def update_graph(n_clicks, rows):
    if n_clicks > 0:
        filtered_df = pd.DataFrame(rows)
        selected_df = filtered_df[filtered_df['Selected'] == 'True']
        if not selected_df.empty:
            fig = px.scatter(selected_df, x='Time', y='Amount01', color='City', title='Selected Data Over Time')
        else:
            fig = px.scatter(filtered_df, x='Time', y='Amount01', color='City', title='All Data Over Time')
        return fig
    return px.scatter(df, x='Time', y='Amount01', color='City', title='All Data Over Time')

# サーバーを起動
if __name__ == '__main__':
    app.run_server(debug=True)
