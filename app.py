from dash import Dash, Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import dash_dangerously_set_inner_html
import datetime

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],  # bootstrap theme settings
           meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1, maximum-scale=1.2, minimum-scale=0.5,"}
]
)

data = pd.read_csv('data/data.tsv', sep='\t')
data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
data['airdate'] = pd.to_datetime(data['airdate'])

dropdown_show = dcc.Dropdown(
    id="dropdown-show",
    options=[{"label": show, "value": show}
             for show in data.show_title.unique()],
    multi=False,
    value='Breaking Bad',
    clearable=False,
)

dropdown_season = dcc.Dropdown(
    id="dropdown-season",
    options={},
    multi=False,
    placeholder='Season',
    clearable=True,
)

def w_avg(df, values, weights):
    d = df[values]
    w = df[weights]
    return (d * w).sum() / w.sum()

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Img(src='assets/logo2.png', className='mx-auto d-block img-fluid mt-5')
        ], lg=7),
        dbc.Col([
            dropdown_show,
        ], className="mt-5 pt-5"),
    ],),
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='ratings-chart', figure={}, className="pt-4 mt-3", responsive=True, style={'min-height': '525px'}),
            ], id='tv'),
        ], id='col1', class_name='my-auto'),
    ], class_name='my-auto', id='row1'),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.Img(id='show-img', className='img-fluid d-block mx-auto', width=400)
                ], lg=4),
                dbc.Col([
                    html.P(id="max-season", className='info'),
                    html.P(id="max-episodes", className='info'),
                    html.P(id="run-time", className='info'),
                    html.P(id="starring", className='info'),
                ], lg=8, class_name='my-auto'),
            ],),
        ], lg=7),
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.P("IMDB Rating", className="stat-title"),
                    html.P(id='show-rating', className="stat-value"),
                    html.P(id='show-ranking', className="rank-value"),
                ], lg=5, className="stat-col",),
                dbc.Col([], lg=1),
                dbc.Col([
                    html.P("Avg Votes Per Ep.", className="stat-title"),
                    html.P(id='average-votes', className="stat-value"),
                    html.P(id='vote-ranking', className="rank-value"),
                ], lg=5, className="stat-col",),
            ],),
        ], lg=5),
    ],),
])

def get_first_value(column):
    return column.iloc[0]

@app.callback(
    Output('ratings-chart', 'figure'),
    Output('show-img', 'src'),
    Output('show-rating', 'children'),
    Output('average-votes', 'children'),
    Output('show-ranking', 'children'),
    Output('vote-ranking', 'children'),
    Output('starring', 'children'),
    Output('run-time', 'children'),
    Output('max-season', 'children'),
    Output('max-episodes', 'children'),
    Input('dropdown-show', 'value'),
)
def update_layout(show):
    df = data[data['show_title'] == show]

    image = df['img_url_y'].iloc[0]

    show_rating = df['show_rating'].iloc[0].round(2)
    show_ranking = f"#{df['rank'].iloc[0]}".rstrip('0').rstrip('.')
    vote_ranking = f"#{df['vote_rank'].iloc[0]}".rstrip('0').rstrip('.')

    average_votes = df['avg_votes'].iloc[0]
    average_votes = f'{average_votes:,}'.rstrip('0').rstrip('.')

    start_date = df['airdate'].min()
    start_date = datetime.date.strftime(start_date, "%m/%d/%Y")
    end_date = df['airdate'].max()
    end_date = datetime.date.strftime(end_date, "%m/%d/%Y")

    starring = f"Starring: {df['star_cast'].iloc[0]}"
    starring = dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
        '''<b>Starring | </b>''' + str(df['star_cast'].iloc[0]))
    run_time = dash_dangerously_set_inner_html.DangerouslySetInnerHTML('''
        <b>Aired | </b>
    ''' + start_date + ''' - ''' + end_date)
    seasons = dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
        '''<b>Seasons | </b>''' + str(max(df['season'])))
    episodes = dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
        '''<b>Episodes | </b>''' + str(max(df['ep_num'])))

    test = df.season.unique()
    fig = px.line(
        df,
        x='ep_num',
        y='rating',
        markers=True,
        line_shape='spline',
        title="IMDb Rating by Episode",
        custom_data=['season', 'episode_number',
                     'title', 'total_votes', 'airdate', 'desc'],
    )

    for s in test:
        yes = df.query(f'season=={s}')
        yes = yes['ep_num'].iloc[-1]
        new = df.query(f'(season=={s}) and (episode_number<=1)')
        line = new['ep_num'].iloc[0]
        fig.add_vrect(x0=yes, x1=line,
                      annotation_text=f"S.{s}", annotation_position="bottom left",
                      fillcolor="#3c3c3c", opacity=0.25, line_width=0)

    fig.update_yaxes(range=[0, 10], dtick=1,
                     showgrid=False, zeroline=True, ticksuffix="  ")
    fig.update_xaxes(showgrid=False, zeroline=True,
                     rangemode="tozero", visible=False)

    fig.update_traces(
        textposition="bottom center",
        line_color='#F5C518',
        hovertemplate="<br>".join([
            "<b>%{customdata[2]}</b>",
            "Rating: %{y}",
            "Episode: S%{customdata[0]}.E%{customdata[1]}",
            "Votes: %{customdata[3]}",
            "Airdate: %{customdata[4]}",
            "Description: %{customdata[5]}",
        ])
    )

    fig.update_layout(
        {
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
        },
        showlegend=False,
        autosize=False,
        margin={'t': 60, 'l': 0, 'b': 30, 'r': 0},
        font_color="white",
        hovermode="x",
        hoverlabel = dict(namelength = -1)
    )

    return fig, image, show_rating, average_votes, show_ranking, vote_ranking, starring, run_time, seasons, episodes


server = app.server

if __name__ == "__main__":
    while True:
        app.run_server(debug=True)
