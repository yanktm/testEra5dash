from dash.dependencies import Input, Output, State
import dash_dangerously_set_inner_html as ddsih
import xarray as xr
import os
import dash
import matplotlib
matplotlib.use('Agg')  # Utilisation du backend 'Agg' pour Matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import base64
import numpy as np
import requests
import re

def get_max_timestep(file, variable):
    dataset_path = f'data/{file}'
    ds = xr.open_zarr(dataset_path)
    return ds.sizes['time'] - 1

def get_github_repo_contents(owner, repo, path='', token=None):
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
    headers = {'Authorization': f'token {token}'} if token else {}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        contents = response.json()
        files = [{'label': content['name'], 'value': content['name']} for content in contents if not content['name'].startswith('.')]
        return files
    else:
        return [{"label": "Unable to fetch directory contents.", "value": "error"}]

def get_local_files(path):
    files = []
    for file_name in os.listdir(path):
        if not file_name.startswith('.'):
            files.append({'label': file_name, 'value': file_name})
    return files

def get_filtered_variables(file, include_error=True):
    dataset_path = f'data/{file}'
    ds = xr.open_zarr(dataset_path)
    variables = list(ds.data_vars.keys())
    error_pattern = re.compile(r'error', re.IGNORECASE)
    
    if include_error:
        return [{'label': var, 'value': var} for var in variables if error_pattern.search(var)]
    else:
        return [{'label': var, 'value': var} for var in variables if not error_pattern.search(var)]

def plot_with_rectangle(dataset, variable, lat, lon, level, time, width):
    half_width = width / 2
    bottom_left_lat = lat - half_width
    bottom_left_lon = lon - half_width

    data = dataset[variable].isel(time=time)
    if level is not None and 'level' in dataset[variable].dims:
        data = data.sel(level=level)
    
    data_rotated = data.transpose().values[:, ::-1]  # Transpose et inverse les colonnes pour une rotation de 90° vers la gauche

    fig, ax = plt.subplots(figsize=(10, 5))  # Ajustement de la taille de la figure
    img = ax.imshow(data_rotated, cmap='coolwarm', aspect='auto', origin='lower')
    rect = patches.Rectangle((bottom_left_lon, bottom_left_lat), width, width, linewidth=2, edgecolor='red', facecolor='none')
    ax.add_patch(rect)

    ax.scatter(lon, lat, color='red')
    ax.annotate(f'(lon: {lon}, lat: {lat})', xy=(lon, lat), xytext=(5, 5), textcoords='offset points', color='black', fontsize=12, ha='center')

    ax.set_title(variable)
    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")

    fig.colorbar(img, ax=ax, orientation='vertical', label='2 metre temperature [K]')

    # Ajustement des marges pour éviter les espaces inutiles
    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f'data:image/png;base64,{encoded}'

def calculate_average_absolute_error(ground_truth, prediction):
    return abs(ground_truth - prediction).mean(dim=['longitude', 'latitude'])

def obtenir_dimensions_sans_time(data):
    return [dim for dim in data.dims if dim != 'time']

def register_callbacks(app):
    # Mise à jour de la liste des fichiers pour les deux dropdowns
    @app.callback(
        Output('file-dropdown1', 'options'),
        Output('file-dropdown2', 'options'),
        Input('file-dropdown1', 'value'),  # Déclenché une fois au démarrage
        Input('file-dropdown2', 'value')
    )
    def update_file_dropdowns(_1, _2):
        local_path = 'data'
        if os.path.exists(local_path):
            files = get_local_files(local_path)
        else:
            owner = 'yanktm'
            repo = 'testEra5dash'
            path = 'data'
            files = get_github_repo_contents(owner, repo, path)
        return files, files

    # Mise à jour des variables en fonction du fichier sélectionné pour les graphes
    @app.callback(
        Output('variable-dropdown1', 'options'),
        Output('variable-dropdown2', 'options'),
        Input('file-dropdown1', 'value'),
        Input('file-dropdown2', 'value')
    )
    def update_variable_dropdowns_graphs(file1, file2):
        def filter_variables(file):
            if file:
                return get_filtered_variables(file, include_error=False)
            return []

        variables1 = filter_variables(file1)
        variables2 = filter_variables(file2)
        return variables1, variables2

    # Mise à jour des variables en fonction du fichier sélectionné pour les métriques
    for i in range(1, 6):
        @app.callback(
            Output(f'dataset{i}-variable-dropdown', 'options'),
            Input(f'dataset{i}-dropdown', 'value')
        )
        def update_variable_dropdown_metrics(selected_file):
            if selected_file:
                return get_filtered_variables(selected_file, include_error=True)
            return []

        @app.callback(
            Output(f'dataset{i}-dropdown', 'options'),
            Input(f'dataset{i}-dropdown', 'value')
        )
        def update_file_dropdown_metrics(_):
            local_path = 'data'
            if os.path.exists(local_path):
                files = get_local_files(local_path)
            else:
                owner = 'yanktm'
                repo = 'testEra5dash'
                path = 'data'
                files = get_github_repo_contents(owner, repo, path)
            return files

    # Mise à jour du nombre maximal de timesteps
    @app.callback(
        Output('max-timestep1', 'children'),
        Output('max-timestep2', 'children'),
        Input('file-dropdown1', 'value'),
        Input('file-dropdown2', 'value'),
        Input('variable-dropdown1', 'value'),
        Input('variable-dropdown2', 'value')
    )
    def update_max_timestep(file1, file2, var1, var2):
        max_timestep1 = get_max_timestep(file1, var1) if file1 and var1 else "N/A"
        max_timestep2 = get_max_timestep(file2, var2) if file2 and var2 else "N/A"
        return f"(max timestep = {max_timestep1})", f"(max timestep = {max_timestep2})"

    # Génération des graphiques
    @app.callback(
        Output('graph1-plot', 'src'),
        Input('generate-button1', 'n_clicks'),
        State('file-dropdown1', 'value'),
        State('variable-dropdown1', 'value'),
        State('latitude-input1', 'value'),
        State('longitude-input1', 'value'),
        State('level-input1', 'value'),
        State('timestep-input1', 'value')
    )
    def update_graph1(n_clicks, file, variable, lat, lon, level, timestep):
        if n_clicks > 0 and file and variable is not None and lat is not None and lon is not None and timestep is not None:
            dataset_path = f'data/{file}'
            ds = xr.open_zarr(dataset_path)
            image = plot_with_rectangle(ds, variable, lat, lon, level, timestep, width=20)
            return image
        return dash.no_update

    @app.callback(
        Output('graph2-plot', 'src'),
        Input('generate-button2', 'n_clicks'),
        State('file-dropdown2', 'value'),
        State('variable-dropdown2', 'value'),
        State('latitude-input2', 'value'),
        State('longitude-input2', 'value'),
        State('level-input2', 'value'),
        State('timestep-input2', 'value')
    )
    def update_graph2(n_clicks, file, variable, lat, lon, level, timestep):
        if n_clicks > 0 and file and variable is not None and lat is not None and lon is not None and timestep is not None:
            dataset_path = f'data/{file}'
            ds = xr.open_zarr(dataset_path)
            image = plot_with_rectangle(ds, variable, lat, lon, level, timestep, width=20)
            return image
        return dash.no_update

    # Génération du graphique de comparaison
    @app.callback(
        Output('comparison-plot', 'src'),
        Input('generate-button3', 'n_clicks'),
        [State(f'dataset{i}-dropdown', 'value') for i in range(1, 6)] +
        [State(f'dataset{i}-variable-dropdown', 'value') for i in range(1, 6)]
    )
    def update_comparison_plot(n_clicks, *args):
        datasets = args[:5]
        variables = args[5:]
        if n_clicks > 0:
            ground_truth_path = f'data/{datasets[0]}'
            ground_truth_variable = variables[0]
            ds_ground_truth = xr.open_zarr(ground_truth_path)
            ground_truth_data = ds_ground_truth[ground_truth_variable]

            fig, ax = plt.subplots(figsize=(10, 5))
            for dataset, variable in zip(datasets[1:], variables[1:]):
                if dataset and variable:
                    ds_prediction = xr.open_zarr(f'data/{dataset}')
                    prediction_data = ds_prediction[variable]
                    aae = abs(ground_truth_data - prediction_data)
                    dimensions = obtenir_dimensions_sans_time(ground_truth_data)
                    aae_mean = aae.mean(dim=dimensions)
                    
                    ax.plot(range(len(aae_mean)), aae_mean, label=f'{dataset}-{variable}')  # Utilisation de range(len(aae_mean)) pour l'axe x

            ax.set_ylabel("Averaged Absolute Error")
            ax.set_xlabel("Time")
            ax.legend()

            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)
            return f'data:image/png;base64,{encoded}'
        return dash.no_update
