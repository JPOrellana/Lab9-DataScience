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

# Función para crear la gráfica de barras
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
        category_orders={"Tipo Combustible": ["Gasolina Regular", "Gasolina Superior", "Diesel"]},  # Cambiar el orden a rojo, verde, gris
        title=f"Tendencia de Precios de Combustible por Año",
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
            'text': f"Tendencia de Precios de Combustible por Año",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        font=dict(color='#006CAF'),
        showlegend=False
    )
    
    return fig

# Función para calcular el promedio de cada tipo de combustible
def calcular_promedio(selected_year):
    df_filtered = df_combustibles[df_combustibles['Fecha'].dt.year == selected_year]
    promedio_superior = df_filtered['Gasolina Superior'].mean()
    promedio_regular = df_filtered['Gasolina Regular'].mean()
    promedio_diesel = df_filtered['Diesel'].mean()
    
    return round(promedio_superior, 2), round(promedio_regular, 2), round(promedio_diesel, 2)

# Layout de la aplicación
app.layout = html.Div([
    html.Div([
        html.H2("Tendencia de Precios de Combustible por Año", style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(year), 'value': year} for year in sorted(df_combustibles['Fecha'].dt.year.unique())],
            value=df_combustibles['Fecha'].dt.year.min(),
            style={'width': '200px', 'margin': 'auto', 'color': '#006CAF'}
        ),
        dcc.Graph(id='price-graph')
    ], style={'width': '75%', 'display': 'inline-block', 'verticalAlign': 'top'}),

    # Cuadros con promedios
    html.Div([
        html.H3("Promedio de Precios de Combustible por Año", style={'textAlign': 'center'}),
        html.Div(id='cuadros-promedio', style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'gap': '20px'})
    ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top'})
], style={'backgroundColor': '#FAF3E0', 'padding': '10px', 'color': '#006CAF'})

# Callback para actualizar los cuadros con los promedios
@app.callback(
    [dash.dependencies.Output('cuadros-promedio', 'children'),
     dash.dependencies.Output('price-graph', 'figure')],
    [dash.dependencies.Input('year-dropdown', 'value')]
)
def actualizar_dashboard(selected_year):
    promedio_superior, promedio_regular, promedio_diesel = calcular_promedio(selected_year)

    cuadros = [
        html.Div([
            html.Img(src='/assets/img/rojo.jpg', style={'width': '50px', 'height': '50px'}),
            html.Span(f"GTQ {promedio_regular}", style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#C22B30'}),
        ], style={'border': '2px solid #972125', 'padding': '10px', 'borderRadius': '5px', 'textAlign': 'center', 'width': '150px'}),
        
        html.Div([
            html.Img(src='/assets/img/verde.jpg', style={'width': '50px', 'height': '50px'}),
            html.Span(f"GTQ {promedio_superior}", style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#158C59'}),
        ], style={'border': '2px solid #0F623E', 'padding': '10px', 'borderRadius': '5px', 'textAlign': 'center', 'width': '150px'}),
        
        html.Div([
            html.Img(src='/assets/img/negro.jpg', style={'width': '50px', 'height': '50px'}),
            html.Span(f"GTQ {promedio_diesel}", style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#808080'}),
        ], style={'border': '2px solid #808080', 'padding': '10px', 'borderRadius': '5px', 'textAlign': 'center', 'width': '150px'})
    ]
    
    # Actualizar la gráfica de barras también
    figure = create_figure(selected_year)
    
    return cuadros, figure

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
