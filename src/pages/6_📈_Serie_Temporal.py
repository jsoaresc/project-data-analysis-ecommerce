import streamlit as st
import plotly.express as px
import pandas as pd
from utils.constants import ESTADOS_BR, PALETA
from utils.visuals import formatar_moeda
from utils.db_queries import obter_lista_categorias, obter_dados_serie_temporal

st.set_page_config(layout="wide", page_title="Série Temporal de Vendas")

st.title("📈 Análise Temporal de Vendas")
st.markdown("Acompanhamento da evolução de vendas e receitas ao longo do tempo, refinado por localização e categoria.")

conn = st.connection("supabase", type="sql")

st.sidebar.header("Filtros da Série Temporal")

estado_vendedor = st.sidebar.selectbox(
    "Estado Vendedor (Origem):", 
    ["Todos os Estados"] + ESTADOS_BR,
    index=0
)

estado_comprador = st.sidebar.selectbox(
    "Estado Comprador (Destino):", 
    ["Todos os Estados"] + ESTADOS_BR,
    index=0
)

with st.spinner('Carregando categorias...'):
    lista_categorias = obter_lista_categorias(conn)

categoria_selecionada = st.sidebar.selectbox(
    "Categoria de Produto:", 
    lista_categorias,
    index=0
)

metrica_y = st.sidebar.radio(
    "Métrica de Análise:",
    options=["Receita Total (R$)", "Volume de Itens Vendidos"]
)

with st.spinner('Processando dados temporais...'):
    df_temporal = obter_dados_serie_temporal(
        conn, 
        estado_vendedor, 
        estado_comprador, 
        categoria_selecionada
    )

if df_temporal.empty:
    st.warning("Não há registros de vendas para a combinação de filtros selecionada.")
else:
    df_temporal['mes_referencia'] = pd.to_datetime(df_temporal['mes_referencia'])
    
    if metrica_y == "Receita Total (R$)":
        coluna_y = "receita_total"
        titulo_y = "Receita Gerada (R$)"
        template_hover = "<b>Mês:</b> %{x|%b/%Y}<br><b>Receita:</b> R$ %{y:,.2f}<extra></extra>"
    else:
        coluna_y = "volume_vendas"
        titulo_y = "Quantidade de Itens"
        template_hover = "<b>Mês:</b> %{x|%b/%Y}<br><b>Volume:</b> %{y} itens<extra></extra>"

    idx_max = df_temporal[coluna_y].idxmax()
    idx_min = df_temporal[coluna_y].idxmin()

    mes_pico = df_temporal.loc[idx_max, 'mes_referencia'].strftime('%m/%Y')
    val_pico = df_temporal.loc[idx_max, coluna_y]

    mes_vale = df_temporal.loc[idx_min, 'mes_referencia'].strftime('%m/%Y')
    val_vale = df_temporal.loc[idx_min, coluna_y]

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    total_acumulado = df_temporal[coluna_y].sum()
    media_mensal = df_temporal[coluna_y].mean()
    
    if metrica_y == "Receita Total (R$)":
        col1.metric("Total Acumulado no Período", formatar_moeda(total_acumulado))
        col2.metric("Média Mensal", formatar_moeda(media_mensal))
    else:
        col1.metric("Total Acumulado no Período", f"{int(total_acumulado):,} itens".replace(",", "."))
        col2.metric("Média Mensal", f"{int(media_mensal):,} itens".replace(",", "."))
        
    col3.metric("Mês de Maior Desempenho", mes_pico)
    
    st.markdown("---")

    titulo_grafico = f"{metrica_y}: {estado_vendedor} ➔ {estado_comprador} | {categoria_selecionada}"

    fig = px.line(
        df_temporal, 
        x="mes_referencia", 
        y=coluna_y,
        markers=True,
        title=titulo_grafico,
        color_discrete_sequence=[PALETA["base"]]
    )

    fig.add_annotation(
        x=df_temporal.loc[idx_max, 'mes_referencia'],
        y=val_pico,
        text=f"⬆ Melhor Período: {mes_pico}",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40,
        font=dict(color=PALETA["selecionada"], size=12),
        arrowcolor=PALETA["selecionada"]
    )

    fig.add_annotation(
        x=df_temporal.loc[idx_min, 'mes_referencia'],
        y=val_vale,
        text=f"⬇ Pior Período: {mes_vale}",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=40,
        font=dict(color=PALETA["destaque"], size=12),
        arrowcolor=PALETA["destaque"]
    )

    fig.update_layout(
        xaxis_title="Período (Mês/Ano)",
        yaxis_title=titulo_y,
        hovermode="x unified",
        xaxis=dict(
            tickformat="%b\n%Y",
            showgrid=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(128, 128, 128, 0.2)'
        ),
        margin=dict(l=0, r=20, t=40, b=0),
        height=500
    )

    fig.update_traces(hovertemplate=template_hover)

    st.plotly_chart(fig, use_container_width=True)