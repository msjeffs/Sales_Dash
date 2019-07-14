'''
Project: Dash Basic Sales Dashboard
Description: The purpose of this project was to experiment with Dash and its
capabilities to produce a simple dashboard.
Version 1: (incomplete) Show basic sales KPIs, plot map of profitability, barcharts to
    display sale by category.
Version 2:
Author: Matt Jeffs
'''

###############################################################################

'''
import Libraries
'''

import dash
from dash.dependencies import Input, Output
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
import plotly.figure_factory as ff
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
#init_notebook_mode(connected=True)
import pandas as pd
from babel.numbers import format_currency


df = pd.read_csv("~/data/SuperstoreExample.csv")
sale_col = ['row_id', 'order_id', 'order_date', 'ship_date', 'ship_mode', 'customer_id', 'customer_name', 'segment', 'country', 'city', 'state', 'postal_code', 'region', 'origin_id', 'category', 'sub_category', 'product_name', 'sales', 'quantity', 'discount', 'profit']
df.columns = sale_col

df = df.astype({"row_id": 'str', 'order_id': 'str', 'order_date': 'str', 'ship_date': 'str', 'ship_mode': 'str' , 'customer_id': 'str', 'customer_name': 'str', 'segment' : 'str', 'country': "str", 'city' : 'str', 'state' : 'str', 'postal_code' : 'str'})
df = df.astype({'region' : 'str', 'origin_id' : 'str', 'category' : 'str', 'sub_category' : 'str', 'product_name' : 'str', 'sales' : 'float64', 'quantity' : 'int64', 'discount' : 'float64', 'profit' : 'float64'})
fips = pd.read_csv('https://query.data.world/s/r3t2p2hkwvkpwmyou2lpapj65gdgjl')
fips.columns = ['state_fips', 'st_abbr', 'state', 'statens']
fips_df = pd.DataFrame(fips)

sales = df['sales'].sum()
sales = format_currency(sales, 'USD', locale='en_US')

profit = df['profit'].sum()
profit = format_currency(profit, 'USD', locale='en_US')

profit_ratio = df['profit'].sum() / df['sales'].sum()
profit_ratio = round(profit_ratio, 2)

profit_per_order = df['profit'].sum() / len(df['order_id'])
profit_per_order = format_currency(profit_per_order, 'USD', locale='en_US')

sales_per_customer = df['sales'].sum() / len(df['customer_id'].unique())
sales_per_customer = format_currency(sales_per_customer, 'USD', locale='en_US')
averageDiscount = df['discount'].median()
averageDiscount = format_currency(averageDiscount, 'USD', locale='en_US')


'''
Functions

Below are a list of all the functions that will be used
makeChoropleth(),
makeBarChart1(),
makeBarChart2()
'''

def makeChoropleth():

    purplescl = [
    [0.0, 'rgb(242,240,247)'],
    [0.2, 'rgb(218,218,235)'],
    [0.4, 'rgb(188,189,220)'],
    [0.6, 'rgb(158,154,200)'],
    [0.8, 'rgb(117,107,177)'],
    [1.0, 'rgb(84,39,143)']
    ]
    bluescl = [
    [0.0, '#E6F2FF'],
    [0.2, '#99CCFF'],
    [0.4, '#66B3FF'],
    [0.6, '#3399FF'],
    [0.8, '#0080FF'],
    [1.0, '#0066CC']
    ]


    sales_by_state = pd.DataFrame(df.groupby('state', as_index = False)['sales'].sum())
    chorodata= pd.merge(sales_by_state,
             fips_df,
             on = 'state',
            how = 'left')

    data = [
        go.Choropleth(
            locations = chorodata['st_abbr'],
            locationmode = 'USA-states',
            z = chorodata['sales'],
            colorscale = bluescl,
            reversescale = False,
            marker = go.choropleth.Marker(
                line = go.choropleth.marker.Line(
                    color = 'rgb(255,255,255)',
                    width = 2
                )),
            colorbar = go.choropleth.ColorBar(
                title = "Sales ($)"),
            zmin = 0,
            zmax = 400000
        )
    ]

    layout = go.Layout(
        title = 'U.S. Sales by State<br>(Hover for breakdown)',
        geo = dict(
            scope = 'usa',
            projection = go.layout.geo.Projection(type = 'albers usa'),
            showlakes = True,
            lakecolor = 'rgb(255, 255, 255)'
        )
    )

    return go.Figure(data = data, layout = layout)


def makeBarChart1():

    segment_data = pd.DataFrame(df.groupby('segment', as_index = False)['sales'].sum())
    x = segment_data['segment']
    y = segment_data['sales']

    trace0 = go.Bar(
    x=x,
    y=y,
    text=y,
    marker=dict(
        color='#4DA6FF',
        line=dict(
            color='#4DA6FF',
            width=1.5,
        )
    )
    )

    data = [trace0]
    layout = go.Layout(
        title='Sales by Segment',
        )

    return go.Figure(data=data, layout=layout)

def makeBarChart2():

    segment_data = pd.DataFrame(df.groupby('category', as_index = False)['sales'].sum())
    x = segment_data['category']
    y = segment_data['sales']

    trace0 = go.Bar(
    x=x,
    y=y,
    text=y,
    marker=dict(
        color='#4DA6FF',
        line=dict(
            color='#4DA6FF',
            width=1.5,
        )
    )
    )

    data = [trace0]
    layout = go.Layout(
        title='Sales by Category',
        )

    return go.Figure(data=data, layout=layout)

    #return go.Figure(data = data, layout = layout)

# this code will eventually be added on later
def generate_table(dataframe, max_rows=10):
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in df.columns],

        style_as_list_view=True,
        style_header={'backgroundColor': 'rgb(30, 30, 30)'},
        style_cell={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
            },
    )

'''
KPI cards and graph_1
'''

graph_1 = dcc.Graph(
    figure={"data": [{"x": df['segment'], "y": df['sales'], 'type': 'bar', 'type': 'Sales'}]}
    )

card_content_1 = [
    dbc.CardHeader("Sales"),
    dbc.CardBody(
        [
            html.H5(sales)
        ]
    )
]

card_content_2 = [
    dbc.CardHeader("Profit"),
    dbc.CardBody(
        [
            html.H5(profit),


        ]
    )
]

card_content_3 = [
    dbc.CardHeader("Profit Ratio"),
    dbc.CardBody(
        [
            html.H5(profit_ratio),
        ]
    )
]

card_content_4 = [
    dbc.CardHeader("Profit Per Order"),
    dbc.CardBody(
        [
            html.H5(profit_per_order),

        ]
    )
]

card_content_5 = [
    dbc.CardHeader("Sales Per Customer"),
    dbc.CardBody(
        [
            html.H5(sales_per_customer),
        ]
    )
]

card_content_6 = [
    dbc.CardHeader("Avg. Discount"),
    dbc.CardBody(
        [
            html.H5(averageDiscount),
        ]
    )
]

'''
Outline structure
'''

row_1 = dbc.Row(
    [
        dbc.Col(dbc.Card(card_content_1, color="white", outline="True")),
        dbc.Col(dbc.Card(card_content_2, color="white", outline="True")),
        dbc.Col(dbc.Card(card_content_3, color="white", outline="True")),
        dbc.Col(dbc.Card(card_content_4, color="white", outline="True")),
        dbc.Col(dbc.Card(card_content_5, color="white", outline="True")),
        dbc.Col(dbc.Card(card_content_6, color="white", outline="True"))
    ],
    className="mb-4"
)

row_2 = dbc.Row(
    [
        dbc.Col(dbc.Card(dcc.Graph(id = 'countryMap', figure = makeChoropleth()), color="black", outline="True"))
    ],
    className="mb-4"
)

row_3 = dbc.Row(
    [
        dbc.Col(dbc.Card(dcc.Graph(id = 'segmentSales', figure = makeBarChart1()), color="white", outline="True")),
        dbc.Col(dbc.Card(dcc.Graph(id = 'categorySales', figure = makeBarChart2()), color="white", outline="True"))
    ],
    className="mb-4"
)

structure = html.Div([html.H1("Executive Profile"), html.Hr(), row_1, row_2, row_3], style = {'marginBottom': 50, 'marginTop': 25, 'text-align': 'center'})

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Main", href="#")),
    ],
    brand="Welcome to Dash",
    brand_href="#",
    sticky="top",
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.config['suppress_callback_exceptions']=True
app.layout = html.Div([
    navbar,
    structure
    ])



if __name__ == "__main__":
    app.run_server()
