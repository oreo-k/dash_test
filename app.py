import json
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_table
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import random

# サンプルデータを20行に拡大し、時間軸を追加
start_date = datetime.today().date()
data = {
    "Amount01": [random.randint(1, 10) for _ in range(20)],
    "Amount02": [random.randint(1, 5) for _ in range(20)],
    "Category": ["A", "A", "A", "B", "B", "B", "C", "C", "C", "C",
                 "A", "A", "A", "B", "B", "B", "C", "C", "C", "C"],
    "Time": [start_date + timedelta(days=i) for i in range(20)]
}

def load_config(path_workingdirectory=".", fn_config="config.json"):
    try:
        with open(fn_config, "r") as f:
            setting = json.load(f)
            return setting

    except FileNotFoundError as e:
        print(e)
        return {}

# 設定をロード
config = load_config()

#config jsonファイルpandasのDataFrameにダンプする
data_config=[config]
#print(data_config[0])
columns_config= [{"name":col, "id":col} for col in data_config[0].keys()]

# DataFrameを作成する
df = pd.DataFrame(data)
df['Selected'] = 'False'

# 時間軸をUNIXタイムスタンプに変換
df["Timestamp"] = pd.to_datetime(df["Time"])

# Dashアプリケーションのインスタンスを作成
app = dash.Dash(__name__)

# アプリケーションのレイアウトを定義
app.layout = html.Div(children=[
    html.H1(children='Data Table with Scroll and Checkbox Filter'),

    html.Details([
        html.Summary('Settings'),
        html.H2("NRのパラメータ名"),
        html.Div([
            dash_table.DataTable(
                id="table_config",
                columns=columns_config,
                data=data_config,
                editable=True
            )
        ]),
    ]),
    
    
    ## Trend Data
    html.Div([
        html.H2("Trend Data解析"),

        dcc.DatePickerRange(
            id="date-picker-range",
            start_date=pd.to_datetime("today").date(),
            end_date=start_date + timedelta(days=7),
            display_format="YYYY-MM-DD"
        ),
        dcc.Graph(
            id='trend-chart'
        )
    ]),


    ## Raw Data
    html.H2("Raw Data解析"),

    # データテーブルを作成
    dash_table.DataTable(
        id='table_data-pick',
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
        id='chart-data-picked'
    )
])

## call back for Trend Data Analysis
@app.callback(
    Output("trend-chart", "figure"),
    [Input("date-picker-range", "start_date"),Input("date-picker-range", "end_date")],
)
def trend_data_analysys(start_date, end_date):

    start_timestamp = datetime.strptime(start_date, "%Y-%m-%d")
    end_timestamp = datetime.strptime(end_date, "%Y-%m-%d")
    df_filtered_time= df[(df['Timestamp'] >= start_timestamp) & (df['Timestamp'] <= end_timestamp)]
    
    fig = px.scatter(df_filtered_time , x='Time', y='Amount01', color='Category', title='Trend Data Analysis')

    return fig 
    

## call back for Raw Data Analysis
# コールバックを定義
@app.callback(
    [
    Output('table_data-pick', 'data'),
    Output('table_data-pick', 'selected_rows'),
    Output('chart-data-picked', 'figure')
     ],
    [
    Input("table_data-pick", "selected_rows"),
    Input('unselect-all-button', 'n_clicks'),
    Input('select-all-button', 'n_clicks'),
    Input('filter-button', 'n_clicks')
     ],
    [
    State('table_data-pick', 'data')
    ]
)
def update_table(
                selected_rows,
                unselect_n_clicks,
                select_n_clicks,
                filter_n_clicks, 
                rows
                ):
    ctx = dash.callback_context

    # Determine which input triggered the callback
    if not ctx.triggered:
        return dash.no_update, dash.no_update, px.scatter()
    
    input_id = ctx.triggered[0]['prop_id'].split('.')[0]

    filtered_df = df.copy()
    if input_id == 'table_data-pick':
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
