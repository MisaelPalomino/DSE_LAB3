import pandas as pd
try:
    df_cat = pd.read_csv('Catalog_Orders.txt', sep=',', quotechar='"')
    df_web = pd.read_csv('Web_orders.txt', sep=';', quotechar='"')
    df_prod = pd.read_csv('products.txt', sep=',', quotechar='"')
    print(">>> se cargo bien \n")
except Exception as e:
    print(f">>> error manito {e}")

def auditoria_calidad(df, nombre):
    print(f" reporte de calidad  {nombre}")

    #parte I
    nulos = df.isnull().sum()
    print("\n1. valoren que falten ")
    if nulos.sum() > 0:
        for col, cant in nulos[nulos > 0].items():
            ids = df[df[col].isnull()]['ID'].tolist()
            print(f"   [!] columna  '{col}': {cant} valores faltantes en IDs: {ids}")
    else:
        print(" completo mi pana ")

    #parte II
    print("\n2. analisis especifico de  'CATALOG':")
    if 'CATALOG' in df.columns:
        # Detectar Desplazamiento de Columnas (Fechas en Catalog)
        errores_fecha = df[df['CATALOG'].astype(str).str.contains(r'/|:', na=False)]
        
        # fallos ortograficos o valores no permitidos  
        cat_validos = df_prod['TYPE'].unique()
        invalidos = df[~df['CATALOG'].isin(cat_validos) & ~df.index.isin(errores_fecha.index)]

        # i. 
        total_err = len(errores_fecha) + len(invalidos)
        porcentaje = (total_err / len(df)) * 100
        print(f"   i. Frecuencia: Se hallaron {total_err} errores ({porcentaje:.2f}% del total).")

        # ii. 
        print("   ii. Representación de errores:")
        if not errores_fecha.empty:
            print(f"       - [ESTRUCTURA]: Fechas desplazadas (ej: '{errores_fecha['CATALOG'].iloc[0]}')")
        if not invalidos.empty:
            print(f"       - [ORTOGRAFÍA/MAESTRO]: Valores no reconocidos: {invalidos['CATALOG'].unique()}")
        if df['CATALOG'].isnull().any():
            print("       - [NULOS]: Hay celdas vacías en la columna.")

    # iii. ¿Dónde ocurren?
    print("   iii. Ubicación (IDs con errores):")
    condicion_error = (~df['CATALOG'].isin(cat_validos)) | (df['CATALOG'].isnull())
    ids_err = df[condicion_error]['ID'].tolist()
    
    if len(ids_err) > 0:
        if len(ids_err) > 15:
            print(f"IDs afectados : {ids_err[:15]}...")
        else:
            print(f"IDs afectados: {ids_err}")
    else:
        print("no se detecta errores ")

    print("\n3. valores no permitidos ")
    if 'QTY' in df.columns:
        negativos = df[df['QTY'] <= 0]
        if not negativos.empty:
            print(f"   [!] Se detectaron QTY <= 0 en IDs: {negativos['ID'].tolist()}")
        else:
            print("   [ok] No hay cantidades negativas o en cero.")

auditoria_calidad(df_cat, "Catalog_Orders.txt")
auditoria_calidad(df_web, "Web_orders.txt")
auditoria_calidad(df_prod, "products.txt")
