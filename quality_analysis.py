import pandas as pd
import re


catalog_orders = pd.read_csv("Catalog_Orders.txt", sep=",")
products = pd.read_csv("products.txt", sep=",")

web_orders = pd.read_csv(
    "Web_orders.txt",
    sep=";",
    header=0,
    names=["ID", "INV", "PCODE", "DATE", "CATALOG", "QTY", "custnum"]
)


def reporte_calidad_general(df, nombre):
    print("\n" + "=" * 80)
    print(f"REPORTE GENERAL DE CALIDAD - {nombre}")
    print("=" * 80)

    print(f"\nCantidad de registros: {len(df)}")
    print(f"Cantidad de columnas: {len(df.columns)}")

    print("\nColumnas:")
    print(df.columns.tolist())

    print("\nValores faltantes por columna:")
    print(df.isnull().sum())

    print("\nPorcentaje de valores faltantes por columna:")
    print((df.isnull().mean() * 100).round(2))

    print("\nRegistros duplicados:")
    print(df.duplicated().sum())

    print("\nTipos de datos:")
    print(df.dtypes)


def analizar_catalog(df, nombre):
    print("\n" + "=" * 80)
    print(f"ANÁLISIS DE CALIDAD DEL ATRIBUTO CATALOG - {nombre}")
    print("=" * 80)

    categorias_validas = {
        "Gardening",
        "Pets",
        "Sports",
        "Toys",
        "Software",
        "Collectibles"
    }

    catalog = df["CATALOG"].astype(str).str.strip()

    errores_catalog = df[~catalog.isin(categorias_validas)]

    print("\nCategorías válidas esperadas:")
    print(categorias_validas)

    print("\nValores únicos encontrados en CATALOG:")
    print(sorted(catalog.unique()))

    print("\nCantidad de errores en CATALOG:")
    print(len(errores_catalog))

    print("\nPorcentaje de errores en CATALOG:")
    print(round(len(errores_catalog) / len(df) * 100, 2), "%")

    print("\n¿Cómo están representados los errores?")
    print(catalog[~catalog.isin(categorias_validas)].value_counts())

    print("\n¿Dónde ocurren los errores? Primeros registros:")
    print(errores_catalog[["ID", "INV", "DATE", "CATALOG", "PCODE", "QTY", "custnum"]].head(20))

    return errores_catalog


def analizar_pcode(df, nombre, products):
    print("\n" + "=" * 80)
    print(f"ANÁLISIS DE CALIDAD DEL ATRIBUTO PCODE - {nombre}")
    print("=" * 80)

    pcode = df["PCODE"].astype(str).str.strip()

    patron_pcode = r"^[A-Z]{2}\d{4}$"

    pcode_formato_invalido = df[~pcode.str.match(patron_pcode, na=False)]

    print("\nCantidad de PCODE con formato inválido:")
    print(len(pcode_formato_invalido))

    print("\nPorcentaje de PCODE con formato inválido:")
    print(round(len(pcode_formato_invalido) / len(df) * 100, 2), "%")

    print("\nEjemplos de PCODE con formato inválido:")
    print(pcode[~pcode.str.match(patron_pcode, na=False)].value_counts().head(20))

    pcode_minusculas = df[pcode.str.contains(r"[a-z]", regex=True, na=False)]

    print("\nCantidad de PCODE con letras minúsculas:")
    print(len(pcode_minusculas))

    print("\nEjemplos de PCODE con minúsculas:")
    print(pcode[pcode.str.contains(r"[a-z]", regex=True, na=False)].value_counts().head(10))

    pcode_con_o = df[pcode.str[2:].str.contains("O", na=False)]

    print("\nCantidad de PCODE con letra 'O' en la parte numérica:")
    print(len(pcode_con_o))

    print("\nEjemplos de PCODE con posible confusión O/0:")
    print(pcode[pcode.str[2:].str.contains("O", na=False)].value_counts().head(20))

    productos_validos = set(products["PCODE"].astype(str).str.upper().str.strip())

    pcode_normalizado = (
        pcode
        .str.upper()
        .str.replace("O", "0", regex=False)
    )

    no_existen_en_products = df[~pcode_normalizado.isin(productos_validos)]

    print("\nCantidad de PCODE que no existen en products.txt luego de normalizar:")
    print(len(no_existen_en_products))

    print("\nPorcentaje de PCODE inexistentes en products.txt:")
    print(round(len(no_existen_en_products) / len(df) * 100, 2), "%")

    print("\nEjemplos de PCODE inexistentes en products.txt:")
    print(pcode_normalizado[~pcode_normalizado.isin(productos_validos)].value_counts().head(20))

    return pcode_formato_invalido, no_existen_en_products


def analizar_fechas(df, nombre, formato=None):
    print("\n" + "=" * 80)
    print(f"ANÁLISIS DE CALIDAD DEL ATRIBUTO DATE - {nombre}")
    print("=" * 80)

    fechas_originales = df["DATE"].astype(str).str.strip()

    fechas_parseadas = pd.to_datetime(
        fechas_originales,
        errors="coerce",
        dayfirst=True
    )

    fechas_invalidas = df[fechas_parseadas.isna()]

    print("\nCantidad de fechas inválidas o no parseables:")
    print(len(fechas_invalidas))

    print("\nPorcentaje de fechas inválidas:")
    print(round(len(fechas_invalidas) / len(df) * 100, 2), "%")

    print("\nRango de fechas parseadas:")
    print("Fecha mínima:", fechas_parseadas.min())
    print("Fecha máxima:", fechas_parseadas.max())

    print("\nEjemplos de fechas inválidas:")
    print(fechas_originales[fechas_parseadas.isna()].head(20))

    return fechas_invalidas


def analizar_qty(df, nombre):
    print("\n" + "=" * 80)
    print(f"ANÁLISIS DE CALIDAD DEL ATRIBUTO QTY - {nombre}")
    print("=" * 80)

    qty = pd.to_numeric(df["QTY"], errors="coerce")

    qty_invalidos = df[qty.isna() | (qty <= 0)]

    print("\nCantidad de QTY inválidos, nulos o menores/iguales a cero:")
    print(len(qty_invalidos))

    print("\nPorcentaje de QTY inválidos:")
    print(round(len(qty_invalidos) / len(df) * 100, 2), "%")

    print("\nDistribución de QTY:")
    print(qty.describe())

    print("\nEjemplos de registros con QTY inválido:")
    print(qty_invalidos.head(20))

    return qty_invalidos


def analizar_products(products):
    print("\n" + "=" * 80)
    print("ANÁLISIS DE CALIDAD - PRODUCTS")
    print("=" * 80)

    print("\nValores faltantes:")
    print(products.isnull().sum())

    print("\nPCODE duplicados:")
    print(products["PCODE"].duplicated().sum())

    productos_precio_invalido = products[
        (products["PRICE"] <= 0) |
        (products["COST"] < 0) |
        (products["COST"] > products["PRICE"])
    ]

    print("\nProductos con precio/costo inválido:")
    print(len(productos_precio_invalido))

    print("\nTipos de productos encontrados:")
    print(products["TYPE"].value_counts())

    print("\nProveedores encontrados:")
    print(products["supplier"].value_counts().head(20))

    return productos_precio_invalido


reporte_calidad_general(catalog_orders, "Catalog_Orders")
reporte_calidad_general(web_orders, "Web_Orders")
reporte_calidad_general(products, "Products")

errores_catalog_catalog = analizar_catalog(catalog_orders, "Catalog_Orders")
errores_catalog_web = analizar_catalog(web_orders, "Web_Orders")

errores_pcode_catalog, pcode_no_products_catalog = analizar_pcode(
    catalog_orders,
    "Catalog_Orders",
    products
)

errores_pcode_web, pcode_no_products_web = analizar_pcode(
    web_orders,
    "Web_Orders",
    products
)

fechas_invalidas_catalog = analizar_fechas(catalog_orders, "Catalog_Orders")
fechas_invalidas_web = analizar_fechas(web_orders, "Web_Orders")

qty_invalidos_catalog = analizar_qty(catalog_orders, "Catalog_Orders")
qty_invalidos_web = analizar_qty(web_orders, "Web_Orders")

productos_invalidos = analizar_products(products)