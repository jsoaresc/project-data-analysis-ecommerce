import streamlit as st
import plotly.express as px

st.title("📊 Análise Exploratória de Dados")
st.markdown("Nesta seção, exploramos as relações do banco de dados relacional da Olist.")

conn = st.connection("supabase", type="sql")

query_pagamentos = """
SELECT 
    p.payment_type AS "Método de Pagamento", 
    COUNT(p.order_id) AS "Quantidade de Pedidos",
    SUM(p.payment_value) AS "Valor Total Movimentado"
FROM olist_order_payments_dataset p
JOIN olist_orders_dataset o ON p.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY p.payment_type
ORDER BY "Quantidade de Pedidos" DESC;
"""

with st.spinner('Consultando o banco de dados...'):
    df_pagamentos = conn.query(query_pagamentos, ttl="10m")

st.subheader("Métodos de Pagamento Mais Utilizados")

col1, col2 = st.columns(2)

with col1:
    st.dataframe(df_pagamentos, use_container_width=True)

with col2:
    fig = px.pie(df_pagamentos, values="Quantidade de Pedidos", names="Método de Pagamento", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
