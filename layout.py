from dash import dcc, html

layout = html.Div([
    # Division principale pour permettre l'ajout de futurs modules
    html.Div([
        # Grand titre centré
        html.H1("Comparaison de Graphes", style={'textAlign': 'center', 'padding': '10px', 'margin-bottom': '10px'}),

        # Division pour les graphiques côte à côte
        html.Div([
            # Division pour Graph1 à gauche
            html.Div([
                dcc.Graph(id='graph1-plot'),
                html.Div("Graphique 1", style={'textAlign': 'center', 'fontWeight': 'bold', 'margin-top': '20px'}),
                html.Div([
                    html.Div([
                        dcc.Dropdown(id='file-dropdown1', options=[], placeholder='Select a file'),
                        html.Button('PROCESS', id='button1-11', n_clicks=0, style={'margin': '5px'}),
                        html.Button('SELECT DATASET', id='button1-12', n_clicks=0, style={'margin': '5px'}),
                    ]),
                    html.Div([
                        dcc.Dropdown(id='variable-dropdown1', options=[], placeholder='Select a variable'),
                        html.Button('SELECT VARIABLE', id='button1-2', n_clicks=0, style={'margin': '5px'}),
                    ]),
                    html.Div([
                        html.Label("Time Step:"),
                        dcc.Input(id='timestep-input1', type='number', value=1, min=0),
                        html.Span(id='max-timestep1', style={'margin-left': '10px'}),
                        html.Button('UPDATE', id='button1-3', n_clicks=0, style={'margin': '5px'}),
                    ]),
                    html.Div([
                        dcc.Dropdown(id='region-dropdown1', options=[], placeholder='Select a region'),
                        html.Button('SELECT REGION', id='button1-4', n_clicks=0, style={'margin': '5px'}),
                    ]),
                    html.Button('Generate', id='generate-button1', n_clicks=0, style={'margin': '5px'})
                ], style={'textAlign': 'center'})
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
            
            # Division pour Graph2 à droite
            html.Div([
                dcc.Graph(id='graph2-plot'),
                html.Div("Graphique 2", style={'textAlign': 'center', 'fontWeight': 'bold', 'margin-top': '20px'}),
                html.Div([
                    html.Div([
                        dcc.Dropdown(id='file-dropdown2', options=[], placeholder='Select a file'),
                        html.Button('PROCESS', id='button2-11', n_clicks=0, style={'margin': '5px'}),
                        html.Button('SELECT DATASET', id='button2-12', n_clicks=0, style={'margin': '5px'}),
                    ]),
                    html.Div([
                        dcc.Dropdown(id='variable-dropdown2', options=[], placeholder='Select a variable'),
                        html.Button('SELECT VARIABLE', id='button2-2', n_clicks=0, style={'margin': '5px'}),
                    ]),
                    html.Div([
                        html.Label("Time Step:"),
                        dcc.Input(id='timestep-input2', type='number', value=1, min=0),
                        html.Span(id='max-timestep2', style={'margin-left': '10px'}),
                        html.Button('UPDATE', id='button2-3', n_clicks=0, style={'margin': '5px'}),
                    ]),
                    html.Div([
                        dcc.Dropdown(id='region-dropdown2', options=[], placeholder='Select a region'),
                        html.Button('SELECT REGION', id='button2-4', n_clicks=0, style={'margin': '5px'}),
                    ]),
                    html.Button('Generate', id='generate-button2', n_clicks=0, style={'margin': '5px'})
                ], style={'textAlign': 'center'})
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'})
        ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'height': '80vh'}),
    ], style={'display': 'flex', 'flex-direction': 'column', 'height': '100vh', 'overflowY': 'scroll'}),

    # Division principale pour permettre l'ajout de futurs modules
    html.Div([
        # Grand titre centré
        html.H1("Métrique de comparaisons des modèles", style={'textAlign': 'center', 'padding': '10px', 'margin-bottom': '10px'}),

        # Division pour le graphique de comparaison
        html.Div([
            # Division pour de comparaison au centre
            html.Div([
                dcc.Graph(id='lower-right-plot'),
                html.Div("Comparaison", style={'textAlign': 'center', 'fontWeight': 'bold', 'margin-top': '10px'}),
                html.Div([
                    html.Button('+', id='button3-1', n_clicks=0, style={'margin': '5px'}),
                    html.Button('+', id='button3-2', n_clicks=0, style={'margin': '5px'}),
                    html.Button('+', id='button3-3', n_clicks=0, style={'margin': '5px'}),
                    html.Button('+', id='button3-4', n_clicks=0, style={'margin': '5px'}),
                    html.Button('Generate', id='generate-button3', n_clicks=0, style={'margin': '5px'})
                ], style={'textAlign': 'center'})
            ], style={'width': '100%', 'display': 'inline-block', 'padding': '10px'}),

        ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'height': '80vh'}),
    ], style={'display': 'flex', 'flex-direction': 'column', 'height': '100vh', 'overflowY': 'scroll'}),

    # Liseuse de fichiers
    html.Div(id='file-viewer', style={'padding': '20px', 'border': '1px solid #ddd', 'margin-top': '20px'})
], style={'padding': '20px'})
