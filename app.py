# app qui calcule les tweets des candidats aux présidentielles 2022 en direct
# Exécuter puis http://127.0.0.1:8050/ 

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc #fait gagner du temps sur le css (faire colonnes etc)
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random
from datetime import datetime # pour manipuler des dates
import time 
import sqlite3 #connecteur entre base de donnée et python
from collections import deque
from dash.dependencies import Input, Output


#######################################################################################################
#                                      DATA
#######################################################################################################
max_lenght = 60
mapbox_token_api = 'pk.eyJ1IjoiYWxleGFuZHJhaCIsImEiOiJja3g5NXZpN28waGw2MzBvMTlxcTVsZHl0In0.4MBe-FazeTboFE561tDeuw'

#je crée une liste deque pour chaque élément (les 14 candidats)
em_tweets, vp_tweets, mlp_tweets, ez_tweets, jlm_tweets, yj_tweets, ah_tweets, \
    am_tweets, fr_tweets, pp_tweets, nda_tweets, jl_tweets, na_tweets, \
    datetimes = [deque(maxlen=max_lenght) for i in range(14)]

# chaque candidat a une couleur et sa liste deque
data_twitter = {
    '@EmmanuelMacron': ['#FA6E00', em_tweets], '@vpecresse': ['#195F91', vp_tweets], '@MLP_officiel': ['#414141', mlp_tweets],
    '@ZemmourEric': ['#7B2B01', ez_tweets], '@JLMelenchon': ['#F01918', jlm_tweets], '@yjadot': ['#469A01', yj_tweets],
    '@Anne_Hidalgo': ['#E86DB3', ah_tweets], '@montebourg': ['#ECADC7', am_tweets], '@Fabien_Roussel': ['#C31E00', fr_tweets],
    '@PhilippePoutou' : ['#BB0806', pp_tweets], '@dupontaignan': ['#4B9BC3', nda_tweets], '@jeanlassalle': ['#0E3653', jl_tweets],
    '@n_arthaud': ['#960A0A', na_tweets],}

# pour chaque liste deque on assigne un range random à l'heure de now
# c'est cette fonction qui sera appelée chaque minute jusqu'à 60.
def update_data():
    datetimes.append(datetime.now().strftime("%H:%M:%S"))
    em_tweets.append(random.randrange(215, 285))
    vp_tweets.append(random.randrange(132, 205))
    mlp_tweets.append(random.randrange(131, 201))
    ez_tweets.append(random.randrange(122, 197))
    jlm_tweets.append(random.randrange(87, 112))
    yj_tweets.append(random.randrange(65, 106))
    ah_tweets.append(random.randrange(43, 98))
    am_tweets.append(random.randrange(22, 65))
    fr_tweets.append(random.randrange(23, 62))
    pp_tweets.append(random.randrange(23, 62))
    nda_tweets.append(random.randrange(18, 53))
    jl_tweets.append(random.randrange(15, 42))
    na_tweets.append(random.randrange(8, 26))

# APP
# on instancie un objet de dash
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], meta_tags= [
    {"name" : "viewport", "content" : "width=device-width, initial-scale=1"}]) 

#######################################################################################################
#                                      LAYOUT
#######################################################################################################
# une page web est cadrillée 12 colonnes et plusieurs lignes.
#Layout = Front end
app.layout = html.Div([
    
    html.Div([
        
        dbc.Row([ #ajoute une ligne
            
            dbc.Col([ # ajoute une colonne à cette ligne
                
                html.Div([ # à cette colonne on ajoute un container
                          
                    html.Img(src="https://wallpaperaccess.com/full/397845.jpg", className="french-flag"),
                    html.Div([
                        html.H1("Présidentielles françaises 2022", className="main-title"),
                        html.H2("Analyse de tweets", className="second-title"),
                        html.P('version : 0.1.0', className='text-version')
                    ], className="title-div"),
                
                
                    html.Div([
                        html.P('Sélectionnez un ou plusieurs candidat(s) :', className='form-text'),
                        
                        dcc.Dropdown(
                            options=[{'label': c, 'value' : c} 
                                     for c in data_twitter.keys()                                    
                                ],
                            value=list(data_twitter.keys())[:3], #valeurs par défaut
                            multi=True, # on peut en sélectionner plusieurs dans le dropdown
                            id ="dropdown-component"
                        ),
                        
                        html.P('Sélectionnez une période d\'analyse :', className='form-text'),
                        
                        dcc.Slider (
                            id='slider-component',
                            min=0,
                            max=60,
                            step=1,
                            value=60, #valeur par défaut quand je charge la page
                            marks={
                                1: {'label': '1m', 'style': {'fontWeight': 'bold'}},
                                10: {'label': '10m'},
                                20: {'label': '20m'},
                                30: {'label': '30m'},
                                40: {'label': '40m'},
                                50: {'label': '50m'},
                                60: {'label': '60m', 'style': {'fontWeight': 'bold'}}},
                            tooltip={"placement": "bottom", "always_visible": True},
                        ),
                        
                        html.Div(
                        dbc.Button('Restaurer les paramètres par défaut', 
                                   id='restore-default-params', 
                                   outline=True, 
                                   color="secondary", 
                                   className="button me-1"), className='d-flex justify-content-center'),
                                                
                    ])
                ], className= "form-container")
                
            ], lg=4, md=12, sm=12), #la colonne prendra une largeur de 4 colonnes sur un écran large, et 12 sur un petit écran
            
            dbc.Col([
                
                dcc.Graph(id='barplot', config={'displayModeBar': False}, className='graph top'),
                dcc.Graph(id='mapbox-graph', className='graph bottom', config={'displayModeBar': False})
                
            ], lg= 4, md=12, sm=12),
            
            dbc.Col([
                
                dcc.Graph(id='scatterplot', config={'displayModeBar': False}, className='graph top')
            ])
            
        ])
        
    ]),
    
    html.Div(id='update-data'), #div vide qui sert au callback qui appelle la fcontion appel date. 
    #élément invisible
    # on utilise dcc.interval pour appeler un callback toutes les n intervalles
    dcc.Interval(id="interval-component",interval=2000, n_intervals=0 ), #2sec
    
    dcc.Loading([
            html.Div(id='empty-div')
    ], id="loading-component", type="graph", fullscreen=True, color='#03045e')
    
    
])

#######################################################################################################
#                                      CALLBACKS
#######################################################################################################

# CALLBACKS : ce qui rend intéractif l'app : décorateur @app.callback + fonction associée
# callback 
@app.callback(
    Output(component_id='update-data', component_property='children'), #Children = le corps de mon component empty-div
    Input(component_id="interval-component", component_property='n_intervals')
)
def generate_data(n):
    data = update_data() # -> on fait tourner la fonction qui génère la donnée
    return data 

@app.callback(
     Output(component_id='dropdown-component', component_property='value'),
     Output(component_id='slider-component', component_property='value'),
     Input(component_id='restore-default-params', component_property='n_clicks'),
     prevent_initial_call = True
)
def restore_default_params(n_click):
    if n_click:
        return list(data_twitter.keys())[:3], 60
    

@app.callback(
    Output(component_id='loading-component', component_property='children'),
    Input(component_id='empty-div', component_property='children')
)
def loading_triggers(value):
    time.sleep(3)
    return value

# callback du barplot
@app.callback(
    Output(component_id='barplot', component_property='figure'), #élément où il y aura l'output, la propriété à modifier ici la figure
    Input(component_id="dropdown-component", component_property= 'value'), # sur quel element on va chercher l'input, ce qu'on va chercher  
    Input('slider-component', 'value'),
    Input(component_id="interval-component", component_property='n_intervals'),
    )
def update_barplot(candidates, period, n): #autant de paramètres que d'input dans le décorateur
    # on affiche le graph
    fig = go.Figure()
    #pour chaque candidat on ajoute une trace
    for candidate in candidates:
        fig.add_trace(
            # on remet la liste dequeu en liste normal car plotly ne comprends pas les dequeu
            go.Bar(x=[i for i in list(datetimes)[max_lenght - period:]], 
                   y=list(data_twitter[candidate][-1]),
                   marker_color= data_twitter[candidate][0],
                   name = f'<b>{candidate}</b>')
            )
        fig.update_layout(
        title={
            'text': "<b>Nombre de tweets cumulés</b>",
            'y':0.95,
            'x':0.15},
        barmode='stack',
        legend=dict(
            x=0,
            y=0,
            font=dict(
                size=10,
                color="black"
            ),
            bgcolor="white",
            bordercolor="Black",
            borderwidth=2
        ),
        xaxis_title ='Heure',
        yaxis_title = 'Nb. de tweets cumulés',
        plot_bgcolor = 'rgba(0, 0, 0, 0)',
        paper_bgcolor = 'rgba(0, 0, 0, 0)',
        margin=dict(
            l=0,
            r=20,
            b=0,
            t=0,
            pad=0
        ),
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        font_color='black'
    )
        
    return fig

@app.callback(
    Output(component_id='scatterplot',component_property='figure'),
    Input(component_id="dropdown-component", component_property='value'),
    Input(component_id='slider-component', component_property='value'),
    Input(component_id='interval-component', component_property='n_intervals'),
)
def update_scatterplot(candidates, period, n):
    
    fig = go.Figure()
    for candidate in candidates:
        fig.add_trace(
            go.Scatter(
                x=[i for i in list(datetimes)[max_lenght - period:]],
                y=list(data_twitter[candidate][-1]),
                line=dict(color=data_twitter[candidate][0], width=4),
                name=f'<b>{candidate}</b>'
            )
        )
    fig.update_yaxes(range=[0, 350]),
    fig.update_layout(
        title={
            'text': "<b>Nombre de tweets par candidat</b>",
            'y':0.95,
            'x':0.15},
        legend=dict(
            x=0,
            y=0,
            font=dict(
                size=10,
                color="black"
            ),
            bgcolor="white",
            bordercolor="Black",
            borderwidth=2
        ),
        xaxis_title ='Heure',
        yaxis_title = 'Volume de tweets',
        plot_bgcolor = 'rgba(0, 0, 0, 0)',
        paper_bgcolor = 'rgba(0, 0, 0, 0)',
        margin=dict(
            l=0,
            r=20,
            b=0,
            t=0,
            pad=0
        ),
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        font_color='black'
    )
    return fig

@app.callback(
    Output(component_id='mapbox-graph',component_property='figure'),
    Input(component_id="dropdown-component", component_property='value'),
    Input(component_id='interval-component', component_property='n_intervals'),
)
def update_mapbox(candidates, n):
    fig = go.Figure()
    for candidate in candidates:
        con = sqlite3.connect('data/villes_france.db')
        cur = con.cursor()
        cur.execute("SELECT ville_longitude_deg, ville_latitude_deg FROM villes_france \
            WHERE ville_id IN (SELECT ville_id FROM villes_france ORDER BY RANDOM() LIMIT '%s')" \
            % data_twitter[candidate][-1][-1])
        results = cur.fetchall()
        con.close()
        fig.add_trace(
            go.Scattermapbox(
                lat=[i[1] for i in results],
                lon=[i[0] for i in results],
                mode='markers',
                marker={
                    'color': data_twitter[candidate][0],
                    'size': 7
                },
            )
        )
    fig.update_layout(
        title={
            'text': "<b>Localisation des tweets</b>",
            'font_color': 'black',
            'y':0.95,
            'x':0.07},
        paper_bgcolor = 'rgba(0,0,0,0)',
        plot_bgcolor = 'rgba(0,0,0,0)',
        autosize=True,
        showlegend = False,
        margin = dict(l=0, r=0, t=0, b=0),
        mapbox = dict(
            accesstoken = mapbox_token_api,
            bearing = 0,
            center = dict(
                lat = 47.0276,
                lon = 2.3137
            ),
           pitch = 0,
           zoom = 4.4,
           style = 'mapbox://styles/mapbox/light-v10'
        ),
    )
    return fig
    


# pour démarrer le serveur et l'app 
app.run_server(debug=True)