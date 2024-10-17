import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# Cargar el archivo CSV
file_path = 'data/precios_combustibles.csv'
df_combustibles = pd.read_csv(file_path)

# Convertir 'Fecha' a formato datetime para un mejor manejo
df_combustibles['Fecha'] = pd.to_datetime(df_combustibles['Fecha'], format='%b-%y')

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Función para actualizar la gráfica 
def create_figure(selected_year):
    # Filtrar por el año seleccionado
    df_filtered = df_combustibles[df_combustibles['Fecha'].dt.year == selected_year]
    
    # Transformar los datos para la gráfica
    df_melted = df_filtered.melt(
        id_vars=['Fecha'], 
        value_vars=['Gasolina Superior', 'Gasolina Regular', 'Diesel'],
        var_name='Tipo Combustible', 
        value_name='Precios'
    )
    
    # Ordenar los meses para que aparezcan de enero a diciembre 
    df_melted['Mes'] = df_melted['Fecha'].dt.strftime('%b')
    meses_espanol = {
        'Jan': 'Ene', 'Feb': 'Feb', 'Mar': 'Mar', 'Apr': 'Abr', 'May': 'May', 'Jun': 'Jun',
        'Jul': 'Jul', 'Aug': 'Ago', 'Sep': 'Sep', 'Oct': 'Oct', 'Nov': 'Nov', 'Dec': 'Dic'
    }
    df_melted['Mes'] = df_melted['Mes'].map(meses_espanol)
    df_melted['Mes'] = pd.Categorical(df_melted['Mes'], categories=[
        'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
        'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'], ordered=True)

    # Crear la gráfica
    fig = px.bar(
        df_melted,
        x='Mes',
        y='Precios',
        color='Tipo Combustible',
        facet_col='Tipo Combustible',
        facet_col_spacing=0.05,
        category_orders={"Tipo Combustible": ["Gasolina Regular", "Gasolina Superior", "Diesel"]},
        title=f"Tendencia de Precios de Combustible en {selected_year}",
        labels={'Mes': 'Mes', 'Precios': 'Precios (GTQ/Galón)', 'Tipo Combustible': 'Tipo de Combustible'}
    )

    # Modificar colores 
    color_discrete_map = {
        'Gasolina Superior': '#158C59',  # Color interno verde
        'Gasolina Regular': '#C22B30',   # Color interno rojo
        'Diesel': '#A2A2A2'              # Color interno negro
    }
    border_color_map = {
        'Gasolina Superior': '#0F623E',  # Contorno verde
        'Gasolina Regular': '#972125',   # Contorno rojo
        'Diesel': '#808080'              # Contorno negro
    }
    
    # Aplicar el color interno y contorno a las barras
    fig.for_each_trace(
        lambda trace: trace.update(
            marker_color=color_discrete_map[trace.name],
            marker_line_color=border_color_map[trace.name],
            marker_line_width=3,
            opacity=0.9
        )
    )

    # Ajustes adicionales de estilo
    fig.update_layout(
        plot_bgcolor='#FAF3E0',
        paper_bgcolor='#FAF3E0',
        xaxis_title="Mes",
        yaxis_title="Precios",
        title={
            'text': f"Tendencia de Precios de Combustible en {selected_year}",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        font=dict(color='#006CAF'),
        showlegend=False
    )
    
    return fig

# Layout de la aplicación
app.layout = html.Div([
    html.H1("Dashboard de Precios de Combustibles", style={'textAlign': 'center', 'backgroundColor': '#FAF3E0', 'color': '#006CAF'}),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': str(year), 'value': year} for year in sorted(df_combustibles['Fecha'].dt.year.unique())],
        value=df_combustibles['Fecha'].dt.year.min(),
        style={'width': '200px', 'margin': 'auto', 'color': '#006CAF'}
    ),
    dcc.Graph(id='price-graph')
], style={'backgroundColor': '#FAF3E0', 'padding': '10px', 'color': '#006CAF'})

# Callback para actualizar la gráfica cuando se selecciona un año
@app.callback(
    dash.dependencies.Output('price-graph', 'figure'),
    [dash.dependencies.Input('year-dropdown', 'value')]
)
def update_graph(selected_year):
    return create_figure(selected_year)

# Ejecutar la aplicación si se ejecuta este script directamente
if __name__ == '__main__':
    app.run_server(debug=True)
