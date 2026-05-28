import streamlit as st
import plotly.express as px
import pandas as pd
from utils.constants import ESTADOS_BR, PALETA
from utils.visuals import formatar_moeda, aplicar_regra_storytelling, aplicar_layout_padrao
from utils.db_queries import obter_lista_categorias, obter_dados_serie_temporal, obter_ranking_categorias_meses

st.set_page_config(layout="wide", page_title="Série Temporal de Vendas")

st.title("📈 Análise Temporal de Vendas")
st.markdown("Acompanhamento da evolução de vendas e receitas ao longo do tempo, com base em localização e categoria.")

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
        
    col3.metric("Mês de Maior Desempenho (Histórico)", mes_pico)
    
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
        text=f"⬆ Pico: {mes_pico}",
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
        text=f"⬇ Vale: {mes_vale}",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=40,
        font=dict(color=PALETA["alerta"], size=12),
        arrowcolor=PALETA["alerta"]
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
        height=450
    )

    fig.update_traces(hovertemplate=template_hover)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Quais são os melhores e piores meses para vender?")
    st.markdown("Esta visão mostra a média de vendas de cada mês, juntando todos os anos analisados. Isso ajuda a descobrir em quais épocas do ano o comércio é naturalmente mais forte ou mais fraco.")
    st.caption(f"**Filtros aplicados:** Categoria: {categoria_selecionada} | Origem (Vendedor): {estado_vendedor} | Destino (Comprador): {estado_comprador}")

    df_sazonal = df_temporal.groupby(df_temporal['mes_referencia'].dt.month)[coluna_y].mean().reset_index()
    
    meses_map = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun', 
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    df_sazonal['mes_nome'] = df_sazonal['mes_referencia'].map(meses_map)

    val_max_sazonal = df_sazonal[coluna_y].max()
    val_min_sazonal = df_sazonal[coluna_y].min()

    df_sazonal['Cor'] = [
        PALETA["selecionada"] if val == val_max_sazonal 
        else (PALETA["alerta"] if val == val_min_sazonal else PALETA["base"]) 
        for val in df_sazonal[coluna_y]
    ]

    if metrica_y == "Receita Total (R$)":
        df_sazonal['texto_formatado'] = df_sazonal[coluna_y].apply(formatar_moeda)
    else:
        df_sazonal['texto_formatado'] = df_sazonal[coluna_y].apply(lambda x: f"{int(x):,} itens".replace(",", "."))

    fig_sazonal = px.bar(
        df_sazonal,
        x='mes_nome',
        y=coluna_y,
        text='texto_formatado'
    )

    fig_sazonal.update_traces(
        marker_color=df_sazonal['Cor'], 
        textposition='outside'
    )

    fig_sazonal.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False, showticklabels=False), 
        margin=dict(l=0, r=20, t=20, b=0),
        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig_sazonal, use_container_width=True)

    st.markdown("---")
    st.subheader("Ranking de Categorias por Período Específico")
    st.markdown("Selecione um ou mais meses abaixo para identificar quais categorias de produtos se destacam durante essa época específica do ano.")
    st.markdown("*Nota: Este ranking ignora propositalmente o filtro de categoria da barra lateral para permitir a comparação entre todos os produtos.*")

    meses_inverso_map = {v: k for k, v in meses_map.items()}
    
    meses_selecionados_nomes = st.multiselect(
        "Selecione os meses para a análise:",
        options=list(meses_map.values()),
        default=['Nov']
    )

    if meses_selecionados_nomes:
        meses_selecionados_numeros = [meses_inverso_map[m] for m in meses_selecionados_nomes]
        
        with st.spinner('Processando ranking de categorias...'):
            df_ranking_cat = obter_ranking_categorias_meses(
                conn, 
                estado_vendedor, 
                estado_comprador, 
                meses_selecionados_numeros
            )
            
        if not df_ranking_cat.empty:
            df_ranking_cat = df_ranking_cat.sort_values(by=coluna_y, ascending=False).head(10)
            df_ranking_cat = df_ranking_cat.sort_values(by=coluna_y, ascending=True).reset_index(drop=True)
            
            df_ranking_cat['Cor'] = aplicar_regra_storytelling(len(df_ranking_cat), PALETA["base"], PALETA["destaque"])

            if metrica_y == "Receita Total (R$)":
                df_ranking_cat['texto_formatado'] = df_ranking_cat[coluna_y].apply(formatar_moeda)
            else:
                df_ranking_cat['texto_formatado'] = df_ranking_cat[coluna_y].apply(lambda x: f"{int(x):,} itens".replace(",", "."))

            fig_ranking = px.bar(
                df_ranking_cat,
                x=coluna_y,
                y="Categoria",
                orientation='h',
                text='texto_formatado'
            )
            
            fig_ranking.update_traces(marker_color=df_ranking_cat['Cor'], textposition='outside')
            fig_ranking = aplicar_layout_padrao(fig_ranking, titulo_x=titulo_y, titulo_y="Categoria do Produto")
            
            st.plotly_chart(fig_ranking, use_container_width=True)
        else:
            st.info("Não há vendas registradas para os filtros e meses selecionados.")
    else:
        st.info("Selecione pelo menos um mês no filtro acima para visualizar o ranking.")