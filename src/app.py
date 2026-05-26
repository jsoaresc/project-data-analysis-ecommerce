import streamlit as st

st.set_page_config(
    page_title="Dashboard Olist | E-Commerce",
    page_icon="📦",
    layout="wide"
)

st.title("📦 E-Commerce Brasileiro: Análise do Dataset Olist")

st.markdown("""
Bem-vindo ao dashboard interativo desenvolvido para explorar o Brazilian E-Commerce Public Dataset fornecido pela Olist.

Disponível em: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
            
### 📖 Sobre o Dataset
Este conjunto de dados contém informações detalhadas de aproximadamente **100 mil pedidos** realizados entre **2016 e 2018** em múltiplos marketplaces no Brasil. Trata-se de dados comerciais reais que foram anonimizados.

O dataset permite investigar o e-commerce sob múltiplas dimensões, como:
Status do pedido, preço, desempenho de pagamento e frete.
Localização geográfica de clientes e vendedores.

### 🏢 Contexto da Operação (Olist)
A Olist conecta pequenas empresas de todo o Brasil a grandes canais de venda com um único contrato. Os lojistas vendem seus produtos através da *Olist Store* e enviam as mercadorias diretamente aos clientes usando a malha logística parceira da Olist. Após a entrega ou vencimento do prazo, o cliente recebe uma pesquisa de satisfação para avaliar a experiência.

---

### 🧭 Guia de Navegação
Utilize o menu lateral para explorar as diferentes frentes de análise deste projeto:

📋 **Tabelas:** Consulta estruturada aos dados brutos das transações.
            
📊 **Exploração:** Ainda incompleto.
            
🗺️ **Oferta VS Demanda:** Mapeamento do fluxo logístico intermunicipal e estadual.
            
🏛️ **Análise Por Estado:** Desempenho financeiro e volume de vendas focado em regiões específicas.
            
📈 **Série Temporal:** Acompanhamento da evolução de métricas de receita e volume ao longo do tempo.

""")