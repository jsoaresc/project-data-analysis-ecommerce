def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")

def aplicar_regra_storytelling(tamanho, cor_padrao="#3498DB", cor_realce="#F39C12"):
    if tamanho <= 1:
        return [cor_padrao] * tamanho
    elif tamanho <= 5:
        top_n = 1
    elif tamanho <= 10:
        top_n = 3
    else:
        top_n = 5
        
    return [cor_padrao if i < tamanho - top_n else cor_realce for i in range(tamanho)]

def aplicar_layout_padrao(fig, titulo_x=None, titulo_y=None, altura=600):
    fig.update_layout(
        xaxis_title=titulo_x,
        yaxis_title=titulo_y,
        height=altura,
        margin=dict(l=0, r=20, t=40, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig



