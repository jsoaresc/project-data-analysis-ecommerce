import streamlit as st
import pandas as pd

st.set_page_config(page_title="Catálogo de Dados", page_icon="📋", layout="wide")

st.title("Catálogo de Tabelas")
st.markdown("""
Nesta página você pode explorar a estrutura das tabelas carregadas no Supabase. 
""")

conn = st.connection("supabase", type="sql")

query_metadata = """
SELECT 
    relname AS "Tabela", 
    reltuples::bigint AS "Linhas (Est.)", 
    pg_size_pretty(pg_total_relation_size(oid)) AS "Tamanho Total"
FROM pg_class 
WHERE relkind = 'r' 
AND relnamespace IN (SELECT oid FROM pg_namespace WHERE nspname = 'public')
ORDER BY relname ASC;
"""

@st.cache_data(ttl="1h")
def get_table_metadata():
    return conn.query(query_metadata)

df_meta = get_table_metadata()

st.divider()

m1, m2 = st.columns(2)
m1.metric("Total de Tabelas", len(df_meta))
m2.metric("Banco de Dados", "PostgreSQL/Supabase")

st.write("---")

for index, row in df_meta.iterrows():
    table_name = row['Tabela']
    rows_count = f"{row['Linhas (Est.)']:,}".replace(',', '.')
    size = row['Tamanho Total']
    
    with st.expander(f"**{table_name}** — `{rows_count} linhas` | `{size}`"):
        
        st.write(f"Visualizando as primeiras 5 linhas de `{table_name}`:")
        
        try:
            @st.cache_data(ttl="1h")
            def preview_table(name):
                return conn.query(f'SELECT * FROM "{name}" LIMIT 5;')
            
            df_preview = preview_table(table_name)
            st.dataframe(df_preview, use_container_width=True)
                        
        except Exception as e:
            st.error(f"Erro ao carregar preview da tabela {table_name}: {e}")