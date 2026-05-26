import streamlit as st
import plotly.express as px
from utils.constants import ESTADOS_BR, PALETA
from utils.visuals import formatar_moeda, aplicar_regra_storytelling
from utils.db_queries import obter_lista_categorias, obter_matriz_por_estado

st.set_page_config(layout="wide", page_title="Análise por Estado")

st.title("🏛️ Análise Individualizada por Estado")
st.markdown("Investigação das relações logísticas de compra e venda por estado, segmentadas por categoria de produto.")

conn = st.connection("supabase", type="sql")

if "categoria_ativa" not in st.session_state:
    st.session_state["categoria_ativa"] = "Todas as Categorias"

st.sidebar.header("Parâmetros da Análise")

estado_selecionado = st.sidebar.selectbox(
    "Estado de Referência:", 
    ESTADOS_BR,
    index=ESTADOS_BR.index('SP')
)

with st.spinner('Carregando categorias...'):
    lista_categorias = obter_lista_categorias(conn)

try:
    indice_categoria = lista_categorias.index(st.session_state["categoria_ativa"])
except ValueError:
    indice_categoria = 0

categoria_selecionada_ui = st.sidebar.selectbox(
    "Categoria de Produto:", 
    lista_categorias,
    index=indice_categoria
)

if categoria_selecionada_ui != st.session_state["categoria_ativa"]:
    st.session_state["categoria_ativa"] = categoria_selecionada_ui
    st.rerun()

categoria_selecionada = st.session_state["categoria_ativa"]

excluir_fluxo_interno = st.sidebar.checkbox(
    f"Ocultar fluxo logístico interno ({estado_selecionado} ➔ {estado_selecionado})", 
    value=False
)

with st.spinner('Processando matriz de dados...'):
    df_compras, df_vendas, df_cat_compradas, df_cat_vendidas = obter_matriz_por_estado(
        _conn=conn,
        estado_selecionado=estado_selecionado,
        categoria_selecionada=categoria_selecionada,
        excluir_fluxo_interno=excluir_fluxo_interno
    )

cor_destaque = PALETA["destaque"]    
cor_base = PALETA["base"]        
cor_neutra = PALETA["neutra"]      
cor_selecionada = PALETA["selecionada"]

st.markdown("---")

total_comprado_geral = float(df_cat_compradas['Valor_Total'].sum()) if not df_cat_compradas.empty else 0.0
total_vendido_geral = float(df_cat_vendidas['Valor_Total'].sum()) if not df_cat_vendidas.empty else 0.0
balanca_geral = total_vendido_geral - total_comprado_geral

label_balanca_geral = "Balança Comercial"
if balanca_geral > 0:
    texto_delta_geral = "Superávit"
    cor_delta_geral = "normal"
elif balanca_geral < 0:
    texto_delta_geral = "- Déficit" 
    cor_delta_geral = "normal"
else:
    texto_delta_geral = None 
    cor_delta_geral = "off"
    label_balanca_geral = "Balança Comercial (Equilíbrio)"

st.markdown(f"#### Balanço Geral | Todas as Categorias  | {estado_selecionado}")
col_geral1, col_geral2, col_geral3 = st.columns(3)
col_geral1.metric(label="Valor Comprado Total", value=formatar_moeda(total_comprado_geral))
col_geral2.metric(label="Valor Vendido Total", value=formatar_moeda(total_vendido_geral))
col_geral3.metric(
    label=label_balanca_geral, 
    value=formatar_moeda(abs(balanca_geral)), 
    delta=texto_delta_geral,
    delta_color=cor_delta_geral
)

if categoria_selecionada != "Todas as Categorias":
    st.markdown("<br>", unsafe_allow_html=True)
    
    total_comprado_cat = float(df_compras['Valor_Total'].sum()) if not df_compras.empty else 0.0
    total_vendido_cat = float(df_vendas['Valor_Total'].sum()) if not df_vendas.empty else 0.0
    balanca_cat = total_vendido_cat - total_comprado_cat

    label_balanca_cat = "Balança Comercial Específica"
    if balanca_cat > 0:
        texto_delta_cat = "Superávit"
        cor_delta_cat = "normal"
    elif balanca_cat < 0:
        texto_delta_cat = "- Déficit" 
        cor_delta_cat = "normal"
    else:
        texto_delta_cat = None 
        cor_delta_cat = "off"
        label_balanca_cat = "Balança Comercial (Equilíbrio)"

    st.markdown(f"#### Balanço Exclusivo | {categoria_selecionada} | {estado_selecionado}")
    col_cat_kpi1, col_cat_kpi2, col_cat_kpi3 = st.columns(3)
    col_cat_kpi1.metric(label=f"Valor Comprado ({categoria_selecionada})", value=formatar_moeda(total_comprado_cat))
    col_cat_kpi2.metric(label=f"Valor Vendido ({categoria_selecionada})", value=formatar_moeda(total_vendido_cat))
    col_cat_kpi3.metric(
        label=label_balanca_cat, 
        value=formatar_moeda(abs(balanca_cat)), 
        delta=texto_delta_cat,
        delta_color=cor_delta_cat
    )

st.markdown("---")
col_controle, _ = st.columns([1, 1])
with col_controle:
    metrica_graficos = st.radio(
        "Métrica de exibição dos gráficos:",
        options=["Quantidade de Itens", "Valor Financeiro (R$)"],
        horizontal=True
    )

if metrica_graficos == "Quantidade de Itens":
    coluna_alvo = "Volume"
    titulo_eixo = "Volume (Qtd de Itens)"
    formato_texto = '%{text}'
else:
    coluna_alvo = "Valor_Total"
    titulo_eixo = "Valor Total (R$)"
    formato_texto = 'R$ %{text:,.2f}'


col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown(f"**Origem das Compras - {categoria_selecionada} (De onde {estado_selecionado} importa)**")
    if not df_compras.empty:
        df_compras = df_compras.sort_values(by=coluna_alvo, ascending=True).reset_index(drop=True)
        
        df_compras['Cor'] = aplicar_regra_storytelling(len(df_compras), cor_base, cor_destaque)

        fig_compras = px.bar(df_compras, x=coluna_alvo, y="Estado_Origem", orientation='h', text=coluna_alvo)
        fig_compras.update_traces(marker_color=df_compras['Cor'], textposition='outside', texttemplate=formato_texto)
        fig_compras.update_layout(xaxis_title=titulo_eixo, yaxis_title="Estado Fornecedor", height=600, xaxis=dict(showgrid=False), margin=dict(l=0, r=20, t=20, b=0))
        st.plotly_chart(fig_compras, use_container_width=True)
    else:
        st.info("Sem registro de compras com os parâmetros atuais.")

with col_graf2:
    st.markdown(f"**Destino das Vendas - {categoria_selecionada} (Para onde {estado_selecionado} exporta)**")
    if not df_vendas.empty:
        df_vendas = df_vendas.sort_values(by=coluna_alvo, ascending=True).reset_index(drop=True)
        
        df_vendas['Cor'] = aplicar_regra_storytelling(len(df_vendas), cor_base, cor_destaque)

        fig_vendas = px.bar(df_vendas, x=coluna_alvo, y="Estado_Destino", orientation='h', text=coluna_alvo)
        fig_vendas.update_traces(marker_color=df_vendas['Cor'], textposition='outside', texttemplate=formato_texto)
        fig_vendas.update_layout(xaxis_title=titulo_eixo, yaxis_title="Estado Consumidor", height=600, xaxis=dict(showgrid=False), margin=dict(l=0, r=20, t=20, b=0))
        st.plotly_chart(fig_vendas, use_container_width=True)
    else:
        st.info("Sem registro de vendas com os parâmetros atuais.")



st.markdown("---")
st.markdown("💡 *Dica: Clique em uma das barras de categoria abaixo para refinar os indicadores gerais.*")
col_cat1, col_cat2 = st.columns(2)

with col_cat1:
    st.markdown(f"**Top Categorias Compradas por {estado_selecionado}**")
    if not df_cat_compradas.empty:
        df_plot_compradas = df_cat_compradas.sort_values(by=coluna_alvo, ascending=False).head(15)
        df_plot_compradas = df_plot_compradas.sort_values(by=coluna_alvo, ascending=True).reset_index(drop=True)
        
        if categoria_selecionada == "Todas as Categorias":
            df_plot_compradas['Cor'] = aplicar_regra_storytelling(len(df_plot_compradas), cor_base, cor_destaque)
        else:
            df_plot_compradas['Cor'] = [cor_selecionada if cat == categoria_selecionada else cor_neutra for cat in df_plot_compradas['Categoria']]

        fig_cat_compradas = px.bar(df_plot_compradas, x=coluna_alvo, y="Categoria", orientation='h', text=coluna_alvo)
        fig_cat_compradas.update_traces(marker_color=df_plot_compradas['Cor'], textposition='outside', texttemplate=formato_texto)
        fig_cat_compradas.update_layout(xaxis_title=titulo_eixo, yaxis_title="Categoria", height=500, xaxis=dict(showgrid=False), margin=dict(l=0, r=20, t=20, b=0))
        
        evento_clique_compras = st.plotly_chart(fig_cat_compradas, use_container_width=True, on_select="rerun")
        
        if evento_clique_compras and len(evento_clique_compras.selection.get("points", [])) > 0:
            categoria_clicada = evento_clique_compras.selection["points"][0]["y"]
            if st.session_state["categoria_ativa"] != categoria_clicada:
                st.session_state["categoria_ativa"] = categoria_clicada
                st.rerun()
    else:
        st.info("Sem registro de categorias compradas com os parâmetros atuais.")

with col_cat2:
    st.markdown(f"**Top Categorias Vendidas por {estado_selecionado}**")
    if not df_cat_vendidas.empty:
        df_plot_vendidas = df_cat_vendidas.sort_values(by=coluna_alvo, ascending=False).head(15)
        df_plot_vendidas = df_plot_vendidas.sort_values(by=coluna_alvo, ascending=True).reset_index(drop=True)
        
        if categoria_selecionada == "Todas as Categorias":
            df_plot_vendidas['Cor'] = aplicar_regra_storytelling(len(df_plot_vendidas), cor_base, cor_destaque)
        else:
            df_plot_vendidas['Cor'] = [cor_selecionada if cat == categoria_selecionada else cor_neutra for cat in df_plot_vendidas['Categoria']]

        fig_cat_vendidas = px.bar(df_plot_vendidas, x=coluna_alvo, y="Categoria", orientation='h', text=coluna_alvo)
        fig_cat_vendidas.update_traces(marker_color=df_plot_vendidas['Cor'], textposition='outside', texttemplate=formato_texto)
        fig_cat_vendidas.update_layout(xaxis_title=titulo_eixo, yaxis_title="Categoria", height=500, xaxis=dict(showgrid=False), margin=dict(l=0, r=20, t=20, b=0))
        
        evento_clique_vendas = st.plotly_chart(fig_cat_vendidas, use_container_width=True, on_select="rerun")
        
        if evento_clique_vendas and len(evento_clique_vendas.selection.get("points", [])) > 0:
            categoria_clicada = evento_clique_vendas.selection["points"][0]["y"]
            if st.session_state["categoria_ativa"] != categoria_clicada:
                st.session_state["categoria_ativa"] = categoria_clicada
                st.rerun()
    else:
        st.info("Sem registro de categorias vendidas com os parâmetros atuais.")