# Instalar las librerías si no las tienes (quitar el comentario para instalarlas)
# install.packages("shiny")
# install.packages("ggplot2")
# install.packages("dplyr")
# install.packages("readr")
# install.packages("tidyr")
# install.packages("lubridate")

library(shiny)
library(ggplot2)
library(dplyr)
library(readr)
library(tidyr)
library(lubridate)

# Cargar el archivo CSV
file_path <- "data/precios_combustibles.csv"
df_combustibles <- read_csv(file_path)

# Convertir la columna 'Fecha' y asegurar el formato adecuado
df_combustibles <- df_combustibles %>%
  mutate(
    Fecha = my(Fecha),  # 'my' es una función de lubridate que convierte 'MMM-YY' a una fecha válida.
    Año = year(Fecha),
    Mes = month(Fecha, label = TRUE, abbr = TRUE)  # Obtener nombres de meses abreviados
  )

# Traducir los meses a español utilizando niveles ordenados
levels(df_combustibles$Mes) <- c("Ene", "Feb", "Mar", "Abr", "May", "Jun", 
                                 "Jul", "Ago", "Sep", "Oct", "Nov", "Dic")

# Definir la aplicación Shiny
ui <- fluidPage(
  titlePanel("Dashboard de Precios de Combustibles"),
  
  sidebarLayout(
    sidebarPanel(
      selectInput(
        inputId = "year",
        label = "Año",
        choices = unique(df_combustibles$Año),
        selected = min(df_combustibles$Año)
      )
    ),
    
    mainPanel(
      plotOutput("pricePlot")
    )
  )
)

server <- function(input, output) {
  
  output$pricePlot <- renderPlot({
    # Filtrar los datos por el año seleccionado
    df_filtered <- df_combustibles %>%
      filter(Año == input$year) %>%
      gather(key = "Tipo_Combustible", value = "Precios", 
             c("Gasolina Superior", "Gasolina Regular", "Diesel"))
    
    # Ordenar los factores para que se agrupen los tipos de combustible
    df_filtered$Tipo_Combustible <- factor(df_filtered$Tipo_Combustible, 
                                           levels = c("Gasolina Superior", "Gasolina Regular", "Diesel"))

    # Crear la gráfica
    ggplot(df_filtered, aes(x = Mes, y = Precios, fill = Tipo_Combustible)) +
      geom_bar(stat = "identity", position = "dodge", 
               color = "#000000", size = 0.2) +
      geom_text(aes(label = round(Precios, 1)), 
                position = position_dodge(width = 0.9), vjust = -0.5, size = 3, color = "#006CAF") +
      scale_fill_manual(
        values = c("Gasolina Superior" = "#158C59",  # Color interno verde
                   "Gasolina Regular" = "#C22B30",   # Color interno rojo
                   "Diesel" = "#A2A2A2"),            # Color interno negro
        name = "Tipo de Combustible"
      ) +
      facet_wrap(~ Tipo_Combustible, scales = "free_x", nrow = 1) +
      labs(title = paste("Tendencia de Precios de Combustible en", input$year),
           x = "Mes",
           y = "Precios (GTQ/Galón)") +
      theme_minimal(base_size = 14) +
      theme(
        plot.title = element_text(color = "#006CAF", face = "bold", hjust = 0.5),
        axis.title = element_text(color = "#006CAF"),
        axis.text = element_text(color = "#006CAF"),
        strip.text = element_text(color = "#006CAF"),
        legend.title = element_text(color = "#006CAF"),
        legend.text = element_text(color = "#006CAF")
      )
  })
}

# Correr la aplicación
shinyApp(ui = ui, server = server)
