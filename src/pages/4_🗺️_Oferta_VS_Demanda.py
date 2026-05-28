import streamlit as st
import plotly.express as px
from utils.visuals import aplicar_regra_storytelling
from utils.db_queries import obter_lista_categorias, obter_dados_oferta_demanda

st.title("🗺️ Análise Interativa de Oferta vs Demanda")
st.markdown("Nesta seção, exploram-se as relações logísticas e comerciais entre os estados brasileiros.")

conn = st.connection("supabase", type="sql")

st.sidebar.header("Filtros de Análise")
st.sidebar.markdown("Utilize os controles abaixo para segmentar os dados da página.")

with st.spinner('Carregando filtros...'):
    lista_categorias = obter_lista_categorias(conn)

categoria_selecionada = st.sidebar.selectbox(
    "Categoria de Produto:", 
    lista_categorias,
    index=0
)

# ocultar_sp = st.sidebar.checkbox("Ocultar fluxo interno (SP ➔ SP)", value=False)

# st.sidebar.markdown("---")
# st.sidebar.info("A seleção acima afeta automaticamente todos os gráficos desta página.")

with st.spinner('Processando dados do banco...'):
    df_dados = obter_dados_oferta_demanda(conn, categoria_selecionada, ocultar_sp=False)

if not df_dados.empty:

    # st.subheader("Densidade de Fluxo Logístico")
    # st.markdown("""
    # O eixo **X (Demanda)** indica o estado do comprador e o eixo **Y (Oferta)** indica o estado do vendedor.
    # """)
    
    # fig_heatmap = px.density_heatmap(
    #     df_dados, 
    #     x="Estado_Cliente",
    #     y="Estado_Vendedor",
    #     z="Volume_Vendas",
    #     color_continuous_scale="Oranges",
    #     labels={
    #         "Estado_Cliente": "Estado do Cliente (Demanda)",
    #         "Estado_Vendedor": "Estado do Vendedor (Oferta)",
    #         "Volume_Vendas": "Itens Vendidos"
    #     }
    # )

    # fig_heatmap.update_layout(
    #     xaxis_title="Destino do Produto (Demanda / Comprador)",
    #     yaxis_title="Origem do Produto (Oferta / Vendedor)",
    #     coloraxis_colorbar=dict(title="Volume"),
    #     margin=dict(l=40, r=40, t=20, b=40)
    # )

    # fig_heatmap.update_xaxes(categoryorder='category ascending')
    # fig_heatmap.update_yaxes(categoryorder='category ascending')

    # st.plotly_chart(fig_heatmap, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Ranking de Volume por Estado")
    st.markdown("Top estados em destaque contra os demais.")

    df_oferta = df_dados.groupby("Estado_Vendedor", as_index=False)["Volume_Vendas"].sum()
    df_demanda = df_dados.groupby("Estado_Cliente", as_index=False)["Volume_Vendas"].sum()

    df_oferta = df_oferta.sort_values(by="Volume_Vendas", ascending=True).reset_index(drop=True)
    df_demanda = df_demanda.sort_values(by="Volume_Vendas", ascending=True).reset_index(drop=True)

    cor_destaque = "#F39C12" 
    cor_base = "#3498DB"     

    df_oferta['Cor_Barra'] = aplicar_regra_storytelling(len(df_oferta), cor_base, cor_destaque)
    df_demanda['Cor_Barra'] = aplicar_regra_storytelling(len(df_demanda), cor_base, cor_destaque)

    col_grafico1, col_grafico2 = st.columns(2)

    with col_grafico1:
        fig_oferta = px.bar(
            df_oferta, 
            x="Volume_Vendas", 
            y="Estado_Vendedor", 
            orientation='h',
            text="Volume_Vendas",
            title="Maiores Ofertantes (Vendedores)"
        )
        fig_oferta.update_traces(
            marker_color=df_oferta['Cor_Barra'], 
            textposition='outside'
        )
        fig_oferta.update_layout(
            xaxis_title="Total de Itens Vendidos",
            yaxis_title="Estado",
            height=600,
            margin=dict(l=0, r=20, t=40, b=0),
            xaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_oferta, use_container_width=True)

    with col_grafico2:
        fig_demanda = px.bar(
            df_demanda, 
            x="Volume_Vendas", 
            y="Estado_Cliente", 
            orientation='h',
            text="Volume_Vendas",
            title="Maiores Demandantes (Compradores)"
        )
        fig_demanda.update_traces(
            marker_color=df_demanda['Cor_Barra'], 
            textposition='outside'
        )
        fig_demanda.update_layout(
            xaxis_title="Total de Itens Comprados",
            yaxis_title="Estado",
            height=600,
            margin=dict(l=0, r=20, t=40, b=0),
            xaxis=dict(showgrid=False) 
        )
        st.plotly_chart(fig_demanda, use_container_width=True)

else:
    st.info("Nenhuma venda registrada com os filtros atuais.")