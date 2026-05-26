import streamlit as st

@st.cache_data(ttl="1h")
def obter_lista_categorias(_conn):
    query = """
    SELECT DISTINCT product_category_name 
    FROM olist_products_dataset 
    WHERE product_category_name IS NOT NULL
    ORDER BY product_category_name;
    """
    df = _conn.query(query)
    return ["Todas as Categorias"] + list(df["product_category_name"])


@st.cache_data(ttl="5m")
def obter_dados_oferta_demanda(_conn, categoria_selecionada, ocultar_sp):
    condicoes = ["o.order_status = 'delivered'"]

    if categoria_selecionada != "Todas as Categorias":
        condicoes.append(f"prod.product_category_name = '{categoria_selecionada}'")

    if ocultar_sp:
        condicoes.append("NOT (c.customer_state = 'SP' AND s.seller_state = 'SP')")

    where_clause = " AND ".join(condicoes)

    query = f"""
    SELECT 
        c.customer_state AS "Estado_Cliente", 
        s.seller_state AS "Estado_Vendedor", 
        COUNT(oi.order_item_id) AS "Volume_Vendas"
    FROM olist_order_items_dataset oi
    JOIN olist_orders_dataset o ON oi.order_id = o.order_id
    JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
    JOIN olist_sellers_dataset s ON oi.seller_id = s.seller_id
    JOIN olist_products_dataset prod ON oi.product_id = prod.product_id
    WHERE {where_clause}
    GROUP BY c.customer_state, s.seller_state;
    """
    return _conn.query(query)


@st.cache_data(ttl="5m")
def obter_matriz_por_estado(_conn, estado_selecionado, categoria_selecionada, excluir_fluxo_interno):
    condicoes_base_compras = [f"c.customer_state = '{estado_selecionado}'"]
    condicoes_base_vendas = [f"s.seller_state = '{estado_selecionado}'"]

    if excluir_fluxo_interno:
        condicoes_base_compras.append(f"s.seller_state != '{estado_selecionado}'")
        condicoes_base_vendas.append(f"c.customer_state != '{estado_selecionado}'")

    where_geral_compras = " AND ".join(condicoes_base_compras)
    where_geral_vendas = " AND ".join(condicoes_base_vendas)

    condicoes_filtro_compras = list(condicoes_base_compras)
    condicoes_filtro_vendas = list(condicoes_base_vendas)

    if categoria_selecionada != "Todas as Categorias":
        filtra_categoria = f"prod.product_category_name = '{categoria_selecionada}'"
        condicoes_filtro_compras.append(filtra_categoria)
        condicoes_filtro_vendas.append(filtra_categoria)

    where_filtrado_compras = " AND ".join(condicoes_filtro_compras)
    where_filtrado_vendas = " AND ".join(condicoes_filtro_vendas)

    query_compras = f"""
    SELECT s.seller_state AS "Estado_Origem", COUNT(oi.order_item_id) AS "Volume", SUM(oi.price) AS "Valor_Total"
    FROM olist_order_items_dataset oi
    JOIN olist_orders_dataset o ON oi.order_id = o.order_id
    JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
    JOIN olist_sellers_dataset s ON oi.seller_id = s.seller_id
    JOIN olist_products_dataset prod ON oi.product_id = prod.product_id
    WHERE o.order_status = 'delivered' AND {where_filtrado_compras}
    GROUP BY s.seller_state;
    """

    query_vendas = f"""
    SELECT c.customer_state AS "Estado_Destino", COUNT(oi.order_item_id) AS "Volume", SUM(oi.price) AS "Valor_Total"
    FROM olist_order_items_dataset oi
    JOIN olist_orders_dataset o ON oi.order_id = o.order_id
    JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
    JOIN olist_sellers_dataset s ON oi.seller_id = s.seller_id
    JOIN olist_products_dataset prod ON oi.product_id = prod.product_id
    WHERE o.order_status = 'delivered' AND {where_filtrado_vendas}
    GROUP BY c.customer_state;
    """

    query_cat_compradas = f"""
    SELECT COALESCE(prod.product_category_name, 'não informada') AS "Categoria", COUNT(oi.order_item_id) AS "Volume", SUM(oi.price) AS "Valor_Total"
    FROM olist_order_items_dataset oi
    JOIN olist_orders_dataset o ON oi.order_id = o.order_id
    JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
    JOIN olist_sellers_dataset s ON oi.seller_id = s.seller_id
    LEFT JOIN olist_products_dataset prod ON oi.product_id = prod.product_id
    WHERE o.order_status = 'delivered' AND {where_geral_compras}
    GROUP BY prod.product_category_name;
    """

    query_cat_vendidas = f"""
    SELECT COALESCE(prod.product_category_name, 'não informada') AS "Categoria", COUNT(oi.order_item_id) AS "Volume", SUM(oi.price) AS "Valor_Total"
    FROM olist_order_items_dataset oi
    JOIN olist_orders_dataset o ON oi.order_id = o.order_id
    JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
    JOIN olist_sellers_dataset s ON oi.seller_id = s.seller_id
    LEFT JOIN olist_products_dataset prod ON oi.product_id = prod.product_id
    WHERE o.order_status = 'delivered' AND {where_geral_vendas}
    GROUP BY prod.product_category_name;
    """

    df_compras = _conn.query(query_compras)
    df_vendas = _conn.query(query_vendas)
    df_cat_compradas = _conn.query(query_cat_compradas)
    df_cat_vendidas = _conn.query(query_cat_vendidas)

    return df_compras, df_vendas, df_cat_compradas, df_cat_vendidas

@st.cache_data(ttl="5m")
def obter_dados_serie_temporal(_conn, estado_vendedor, estado_comprador, categoria_selecionada):
    condicoes = ["o.order_status = 'delivered'"]

    if estado_vendedor != "Todos os Estados":
        condicoes.append(f"s.seller_state = '{estado_vendedor}'")

    if estado_comprador != "Todos os Estados":
        condicoes.append(f"c.customer_state = '{estado_comprador}'")

    if categoria_selecionada != "Todas as Categorias":
        condicoes.append(f"prod.product_category_name = '{categoria_selecionada}'")

    clausula_where = " AND ".join(condicoes)

    query = f"""
    SELECT 
        DATE_TRUNC('month', CAST(o.order_purchase_timestamp AS TIMESTAMP)) AS mes_referencia,
        SUM(oi.price) AS receita_total,
        COUNT(oi.order_item_id) AS volume_vendas
    FROM olist_order_items_dataset oi
    JOIN olist_orders_dataset o ON oi.order_id = o.order_id
    JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
    JOIN olist_sellers_dataset s ON oi.seller_id = s.seller_id
    JOIN olist_products_dataset prod ON oi.product_id = prod.product_id
    WHERE {clausula_where}
    GROUP BY DATE_TRUNC('month', CAST(o.order_purchase_timestamp AS TIMESTAMP))
    ORDER BY mes_referencia;
    """
    
    return _conn.query(query)

@st.cache_data(ttl="5m")
def obter_serie_temporal_rota(_conn, estado_origem, estado_destino, categoria_selecionada):
    condicoes = [
        "o.order_status = 'delivered'",
        f"s.seller_state = '{estado_origem}'",
        f"c.customer_state = '{estado_destino}'"
    ]

    if categoria_selecionada != "Todas as Categorias":
        condicoes.append(f"prod.product_category_name = '{categoria_selecionada}'")

    where_clause = " AND ".join(condicoes)

    query = f"""
    SELECT 
        DATE_TRUNC('month', CAST(o.order_purchase_timestamp AS TIMESTAMP)) AS mes_referencia,
        COUNT(oi.order_item_id) AS volume_vendas
    FROM olist_order_items_dataset oi
    JOIN olist_orders_dataset o ON oi.order_id = o.order_id
    JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
    JOIN olist_sellers_dataset s ON oi.seller_id = s.seller_id
    JOIN olist_products_dataset prod ON oi.product_id = prod.product_id
    WHERE {where_clause}
    GROUP BY DATE_TRUNC('month', CAST(o.order_purchase_timestamp AS TIMESTAMP))
    ORDER BY mes_referencia;
    """
    return _conn.query(query)