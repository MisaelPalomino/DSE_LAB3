import pandas as pd
import numpy as np
import re

# Cargar datasets
catalog_orders = pd.read_csv('Catalog_Orders.txt', sep=',')
web_orders = pd.read_csv('Web_orders.txt', sep=';')
products = pd.read_csv('products.txt', sep=',')

print("=== CATALOG ORDERS ===")
print(catalog_orders.head())
print(f"Dimensiones: {catalog_orders.shape}")
print(f"Columnas: {catalog_orders.columns.tolist()}")

print("\n=== WEB ORDERS ===")
print(web_orders.head())
print(f"Dimensiones: {web_orders.shape}")
print(f"Columnas: {web_orders.columns.tolist()}")

print("\n=== PRODUCTS ===")
print(products.head())
print(f"Dimensiones: {products.shape}")
print(f"Columnas: {products.columns.tolist()}")

# Funcion para analisis exploratorio detallado
def analisis_exploratorio(df, nombre):
    print(f"\n{'='*80}")
    print(f"ANALISIS EXPLORATORIO - {nombre}")
    print(f"{'='*80}\n")
    
    # i. Tipos de datos, longitud, intervalos, varianza, singularidad
    print("i. TIPOS DE DATOS Y ESTADISTICOS BASICOS")
    print("-" * 50)
    
    # Tipos de datos
    print("\nTipos de datos por columna:")
    for col in df.columns:
        print(f"   {col}: {df[col].dtype}")
    
    # Longitud y valores nulos
    print(f"\nLongitud del dataset: {len(df)} registros")
    print("Valores nulos por columna:")
    if df.isnull().any().any():
        print(df.isnull().sum()[df.isnull().sum() > 0])
    else:
        print("   No hay valores nulos")
    
    # Analisis de columnas numericas
    num_cols = df.select_dtypes(include=[np.number]).columns
    if len(num_cols) > 0:
        print(f"\nAnalisis de columnas numericas:")
        for col in num_cols:
            print(f"\n   Columna: {col}")
            print(f"      Rango: [{df[col].min():.2f} - {df[col].max():.2f}]")
            print(f"      Media: {df[col].mean():.2f}")
            print(f"      Mediana: {df[col].median():.2f}")
            print(f"      Varianza: {df[col].var():.2f}")
            print(f"      Desviacion estandar: {df[col].std():.2f}")
    
    # Singularidad (valores unicos)
    print(f"\nSingularidad (valores unicos):")
    for col in df.columns:
        unique_vals = df[col].nunique()
        total_vals = len(df[col])
        porcentaje = (unique_vals / total_vals) * 100
        print(f"   {col}: {unique_vals} unicos / {total_vals} totales ({porcentaje:.2f}% unicos)")
        if unique_vals <= 20:
            print(f"      Valores: {sorted(df[col].dropna().unique())}")
    
    # ii. Distribucion de valores y relaciones
    print(f"\nii. DISTRIBUCION DE ATRIBUTOS CLAVE Y RELACIONES")
    print("-" * 50)
    
    # Distribucion de columnas categoricas
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        if df[col].nunique() <= 15:
            print(f"\nDistribucion de '{col}':")
            print(df[col].value_counts().head(10))
    
    # Relaciones entre pares de atributos (correlacion)
    if len(num_cols) >= 2:
        print(f"\nMatriz de correlacion (Pearson):")
        corr_matrix = df[num_cols].corr()
        print(corr_matrix)
        
        print("\nCorrelaciones fuertes encontradas:")
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.5:
                    print(f"   {corr_matrix.columns[i]} y {corr_matrix.columns[j]}: {corr_val:.3f}")
    
    # iii. Patrones de string tipicos
    print(f"\niii. PATRONES DE STRING TIPICOS")
    print("-" * 50)
    
    def detectar_patron(columna, patron, nombre_patron):
        col_str = columna.astype(str)
        match = col_str.str.match(patron, na=False)
        if match.any():
            print(f"   {nombre_patron} detectado en columna: {columna.name}")
            print(f"     Ejemplos: {columna[match].head(3).tolist()}")
            return True
        return False
    
    for col in cat_cols:
        # Detectar fechas (YYYY-MM-DD, DD/MM/YYYY, etc.)
        patron_fecha = r'^\d{4}-\d{2}-\d{2}$|^\d{2}/\d{2}/\d{4}$|^\d{2}-\d{2}-\d{4}$'
        if detectar_patron(df[col], patron_fecha, "FECHAS"):
            continue
        
        # Detectar telefonos
        patron_telefono = r'^\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}$|^\d{10,15}$'
        if detectar_patron(df[col], patron_telefono, "TELEFONOS"):
            continue
        
        # Detectar emails
        patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if detectar_patron(df[col], patron_email, "EMAILS"):
            continue
        
        # Detectar codigos postales
        patron_cp = r'^\d{5}$|^\d{5}-\d{3}$'
        if detectar_patron(df[col], patron_cp, "CODIGOS POSTALES"):
            continue
        
        # Detectar URLs
        patron_url = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        detectar_patron(df[col], patron_url, "URLS")
    
    # iv. Propiedades de sub-poblaciones
    print(f"\niv. SUB-POBLACIONES Y PROPIEDADES ESPECIFICAS")
    print("-" * 50)
    
    # Identificar posibles columnas de segmentacion
    segmentacion_encontrada = False
    for col in cat_cols:
        if 2 <= df[col].nunique() <= 15:
            segmentacion_encontrada = True
            print(f"\nSub-poblaciones por '{col}':")
            print(f"   Categorias: {df[col].nunique()} grupos")
            
            # Distribucion porcentual
            print(f"\n   Distribucion porcentual:")
            percent_dist = (df[col].value_counts() / len(df) * 100).round(2)
            print(percent_dist)
            
            # Estadisticas por grupo para columnas numericas
            if len(num_cols) > 0:
                for num_col in num_cols[:3]:
                    print(f"\n   Estadisticas de '{num_col}' por '{col}':")
                    grouped_stats = df.groupby(col)[num_col].agg(['mean', 'median', 'min', 'max', 'count'])
                    print(grouped_stats)
                    
                    # Detectar diferencias significativas
                    if len(grouped_stats) >= 2:
                        max_mean = grouped_stats['mean'].max()
                        min_mean = grouped_stats['mean'].min()
                        if min_mean > 0 and (max_mean / min_mean) > 3:
                            print(f"   Diferencia significativa detectada en '{num_col}' (ratio: {max_mean/min_mean:.2f})")
    
    if not segmentacion_encontrada:
        print("\nNo se encontraron columnas categoricas adecuadas para segmentacion")
        print("Verificando posibles sub-poblaciones por rangos numericos:")
        for col in num_cols[:2]:
            print(f"\n   Sub-poblaciones por cuartiles de '{col}':")
            df[f'{col}_cuartil'] = pd.qcut(df[col], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
            cuartil_dist = df[f'{col}_cuartil'].value_counts().sort_index()
            print(f"   Distribucion: {cuartil_dist.to_dict()}")
            df.drop(f'{col}_cuartil', axis=1, inplace=True)
    
    # Analisis de outliers en datos numericos
    if len(num_cols) > 0:
        print(f"\nDETECCION DE OUTLIERS (Metodo IQR):")
        for col in num_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            print(f"   {col}: {len(outliers)} outliers ({len(outliers)/len(df)*100:.2f}%)")

# Aplicar analisis a cada dataset
analisis_exploratorio(catalog_orders, "Catalog_Orders")
analisis_exploratorio(web_orders, "Web_Orders")
analisis_exploratorio(products, "Products")

# Analisis adicional de relaciones entre datasets
print(f"\n{'='*80}")
print("ANALISIS DE RELACIONES ENTRE DATASETS")
print(f"{'='*80}")

print("\nColumnas comunes entre datasets:")
columnas_catalog = set(catalog_orders.columns)
columnas_web = set(web_orders.columns)
columnas_products = set(products.columns)

print(f"\nCatalog_Orders y Web_Orders comparten: {columnas_catalog.intersection(columnas_web)}")
print(f"Catalog_Orders y Products comparten: {columnas_catalog.intersection(columnas_products)}")
print(f"Web_Orders y Products comparten: {columnas_web.intersection(columnas_products)}")

# Buscar posibles columnas de llave para hacer joins
for col in columnas_catalog.intersection(columnas_web):
    catalog_unique = catalog_orders[col].nunique()
    web_unique = web_orders[col].nunique()
    print(f"\nAnalisis de columna compartida '{col}':")
    print(f"   Catalog_Orders: {catalog_unique} valores unicos")
    print(f"   Web_Orders: {web_unique} valores unicos")
    
    if catalog_unique < len(catalog_orders) and web_unique < len(web_orders):
        print(f"   Esta columna podria ser una llave para combinar datasets")
        print(f"   Ejemplos en Catalog_Orders: {catalog_orders[col].dropna().head(3).tolist()}")
        print(f"   Ejemplos en Web_Orders: {web_orders[col].dropna().head(3).tolist()}")