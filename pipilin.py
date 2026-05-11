import pandas as pd
from sqlalchemy import create_engine, text

# 1. CONEXIÓN
engine = create_engine('postgresql://postgres:@localhost:5432/laboratorio_etl')

def run_etl():
    try:
        # --- EXTRACCIÓN ---
        print("Leyendo archivos...")
        df_catalog = pd.read_csv('Catalog_Orders.txt') 
        df_web = pd.read_csv('Web_orders.txt', sep=';')
        df_products = pd.read_csv('products.txt')

        # --- TRANSFORMACIÓN ---
        print("Transformando datos...")
        
        # A. Limpieza Productos
        df_products = df_products.rename(columns={
            'TYPE': 'category_type', 'DESCRIP': 'description',
            'PRICE': 'price', 'COST': 'cost', 'PCODE': 'pcode'
        })
        # Normalizamos pcode a mayúsculas y quitamos espacios
        df_products['pcode'] = df_products['pcode'].str.strip().str.upper()
        
        cols_db_products = ['pcode', 'description', 'category_type', 'price', 'cost', 'supplier']
        df_products = df_products[cols_db_products].drop_duplicates(subset=['pcode'])

        # B. Corrección de Fechas
        df_catalog['DATE'] = pd.to_datetime(df_catalog['DATE'], format='mixed', errors='coerce')
        df_web['DATE'] = pd.to_datetime(df_web['DATE'], format='mixed', errors='coerce')

        # C. Dimensión Tiempo
        all_dates = pd.concat([df_catalog['DATE'], df_web['DATE']]).dropna().unique()
        df_time = pd.DataFrame({'date_key': all_dates})
        df_time['day'] = df_time['date_key'].dt.day
        df_time['month'] = df_time['date_key'].dt.month
        df_time['year'] = df_time['date_key'].dt.year
        df_time['quarter'] = df_time['date_key'].dt.quarter

        # D. Integración de Hechos
        df_catalog['channel_id'] = 1 
        df_web['channel_id'] = 2     
        cols_source = ['INV', 'DATE', 'PCODE', 'QTY', 'custnum', 'channel_id']
        df_fact = pd.concat([df_catalog[cols_source], df_web[cols_source]])
        df_fact.columns = ['invoice_num', 'date_key', 'pcode', 'quantity', 'customer_info', 'channel_id']

        # --- LIMPIEZA CRÍTICA ---
        # 1. Normalizar códigos de producto en ventas
        df_fact['pcode'] = df_fact['pcode'].str.strip().str.upper()
        # 2. Corregir el error común de 'O' por '0' en los códigos
        df_fact['pcode'] = df_fact['pcode'].str.replace('OO', '00')
        
        # 3. FILTRO DE INTEGRIDAD: Solo dejamos ventas de productos que existen en df_products
        productos_validos = df_products['pcode'].unique()
        df_fact = df_fact[df_fact['pcode'].isin(productos_validos)]
        
        # 4. Limpiar nulos y tipos
        df_fact['quantity'] = pd.to_numeric(df_fact['quantity'], errors='coerce')
        df_fact = df_fact.dropna(subset=['quantity', 'date_key', 'pcode'])

        # --- CARGA ---
        print("Cargando a PostgreSQL...")
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE fact_orders, dim_products, dim_time RESTART IDENTITY CASCADE;"))

        df_products.to_sql('dim_products', engine, if_exists='append', index=False)
        df_time.to_sql('dim_time', engine, if_exists='append', index=False)
        df_fact.to_sql('fact_orders', engine, if_exists='append', index=False)
        

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_etl()