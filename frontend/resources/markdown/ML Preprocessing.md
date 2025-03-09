# Desarrollo de Modelos de Machine Learning para la Predicción de Temperatura
Los conjuntos de datos finales se pueden encontrar [aquí](https://proyectometeorologico.streamlit.app/ML)
## Variable Objetivo: tmed (Temperatura Media Diaria)
## Años Utilizados: 2010-2025
## Modelos Utilizados:
- Facebook Prophet
- SimpleRNN
- Gated Recurrent Unit (GRU)
## Pipeline de Procesamiento de Datos
Estos cuadernos demuestran la conversión de datos meteorológicos históricos brutos en formatos optimizados para precisión y eficiencia en nuestros modelos de pronóstico.
### 1. Proceso de Limpieza:
- Concatenación de tablas de todos los años en un único conjunto de datos
- Conversión de columnas de fecha y dirección del viento a representaciones de seno y coseno
- Extracción de valores de año y normalización: 1950 → 0.0, 2050 → 1.0 (2000 = 0.5)
- Fusión de metadatos de estaciones (IDEMA*, latitud, longitud, altitud)
- Conversión de columnas numéricas a formatos apropiados
- Redondeo de todos los valores a 4 decimales
*IDEMA - Identificación Estación Meteorológica (AEMET Station ID)
### 2. Selección de Características:
#### Columnas Conservadas:
| Columna    | % NaN |
|------------|-------|
| hr_max     | 5.90% |
| hr_media   | 5.60% |
| prec       | 3.64% |
| tmed       | 2.27% |
| tmin       | 2.24% |
| tmax       | 2.23% |
| latitud    | 0%    |
| altitud    | 0%    |
| fecha_sin  | 0%    |
| fecha_cos  | 0%    |
#### Columnas Eliminadas:
| Columna    | % NaN  |
|------------|--------|
| sol        | 82.91% |
| pres_max   | 75.85% |
| pres_min   | 75.61% |
| dir_sin    | 20.79% |
| dir_cos    | 20.79% |
| racha      | 20.79% |
| velmedia   | 20.14% |
| hr_min     | 5.90%  |
| longitud   | 0%     |
| year       | 0%     |
### 3. Búsqueda de Estación más Cercana:
- Creación de un mapeo de cada estación a todas las demás estaciones en orden desde la más cercana a la más lejana
- Distancia calculada utilizando latitud, longitud y altitud después de aplicar StandardScaler
### 4. Imputación por Estación más Cercana:
- Imputación de todos los valores NaN utilizando la media de las 5 estaciones más cercanas para cada día
- Este enfoque previene la filtración de datos entre conjuntos, ya que solo utiliza datos del mismo día
- Columnas imputadas y sus porcentajes de valores faltantes:
  
| Columna   | % NaN |
|-----------|-------|
| hr_max    | 5.90% |
| hr_media  | 5.60% |
| prec      | 3.64% |
| tmed      | 2.27% |
| tmin      | 2.24% |
| tmax      | 2.23% |
### 5. División Train-Validation-Test:
- División de los datos finales en 4 conjuntos distintos:
  1. **Conjunto de Entrenamiento**: 3,249,868 filas (70.91%) - Utilizado para el entrenamiento inicial del modelo
  2. **Conjunto de Validación**: 633,758 filas (13.83%) - Utilizado para evaluación de rendimiento durante el entrenamiento
  3. **Conjunto de Prueba**: 699,154 filas (15.26%) - Conjunto ciego para evaluación final del modelo y métricas
  4. **Conjunto Completo**: 4,582,780 filas (100%) - Conjunto de datos completo utilizado para el entrenamiento final del modelo desplegado
### 6. Escalado MinMax:
- Escalado de todos los valores en los 4 conjuntos de datos de 0 a 1 utilizando MinMaxScaler
- Creación y guardado de 2 escaladores separados:
  1. **Escalador de Entrenamiento**: Ajustado en el conjunto de entrenamiento y aplicado a los conjuntos de entrenamiento, validación y prueba
  2. **Escalador Completo**: Ajustado en el conjunto completo para transformar entradas reales de usuarios en el modelo desplegado