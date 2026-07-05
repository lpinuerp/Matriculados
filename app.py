import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN GENERAL Y ESTILO
# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Educación Superior Chile · 2017-2025",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta propia (no la default de Streamlit) inspirada en sellos y diplomas académicos
NAVY = "#1B2A4A"
INK = "#33415C"
GOLD = "#C7A252"
SAGE = "#6E8F71"
BRICK = "#B5533C"
SLATE = "#8592A6"
PAPER = "#FAF8F3"
CARD = "#FFFFFF"

PALETTE_CATEGORICAL = [NAVY, GOLD, SAGE, BRICK, SLATE, "#3E6478", "#9C7A3C", "#4F7A63"]

px.defaults.color_discrete_sequence = PALETTE_CATEGORICAL

PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter, sans-serif", color=INK, size=13),
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        colorway=PALETTE_CATEGORICAL,
        title=dict(font=dict(family="Fraunces, serif", size=20, color=NAVY)),
        xaxis=dict(gridcolor="#E7E2D6", zerolinecolor="#E7E2D6"),
        yaxis=dict(gridcolor="#E7E2D6", zerolinecolor="#E7E2D6"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=60, l=10, r=10, b=10),
    )
)

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    h1, h2, h3 {{
        font-family: 'Fraunces', serif !important;
        color: {NAVY} !important;
    }}
    .stApp {{
        background-color: {PAPER};
    }}
    section[data-testid="stSidebar"] {{
        background-color: {NAVY};
    }}
    section[data-testid="stSidebar"] * {{
        color: {PAPER} !important;
    }}
    [data-testid="stMetric"] {{
        background-color: {CARD};
        border: 1px solid #E7E2D6;
        border-left: 4px solid {GOLD};
        border-radius: 6px;
        padding: 14px 16px;
    }}
    [data-testid="stMetricLabel"] {{
        color: {INK} !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: 'Fraunces', serif;
        font-size: 15px;
    }}
    .insight-card {{
        background-color: {CARD};
        border: 1px solid #E7E2D6;
        border-left: 4px solid {SAGE};
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────
# CARGA DE DATOS
# ──────────────────────────────────────────────────────────────────────────
COL_TOTAL = "TOTAL MATRÍCULA"
COL_MUJ = "TOTAL MATRÍCULA MUJERES"
COL_HOM = "TOTAL MATRÍCULA HOMBRES"
COL_1ER = "TOTAL MATRÍCULA PRIMER AÑO"
COL_TIPO1 = "CLASIFICACIÓN INSTITUCIÓN NIVEL 1"
COL_TIPO2 = "CLASIFICACIÓN INSTITUCIÓN NIVEL 2"
COL_INST = "NOMBRE INSTITUCIÓN"
COL_ACRED_INST = "ACREDITACIÓN INSTITUCIONAL"
COL_REGION = "REGIÓN"
COL_CARRERA = "NOMBRE CARRERA"
COL_AREA = "ÁREA DEL CONOCIMIENTO"
COL_NIVEL_GLOBAL = "NIVEL GLOBAL"
COL_AREA_GENERICA = "ÁREA CARRERA GENÉRICA"
COL_MODALIDAD = "MODALIDAD"
COL_JORNADA = "JORNADA"
COL_EDAD_PROM = "PROMEDIO EDAD CARRERA"
COL_EDAD_MUJ = "PROMEDIO EDAD MUJER"
COL_EDAD_HOM = "PROMEDIO EDAD HOMBRE"
COL_COBERTURA_TES = "% COBERTURA TES"
RANGOS_EDAD = [
    "RANGO DE EDAD 15 A 19 AÑOS", "RANGO DE EDAD 20 A 24 AÑOS",
    "RANGO DE EDAD 25 A 29 AÑOS", "RANGO DE EDAD 30 A 34 AÑOS",
    "RANGO DE EDAD 35 A 39 AÑOS", "RANGO DE EDAD 40 Y MÁS AÑOS",
]
TES_COLS = [
    "TES MUNICIPAL", "TES PARTICULAR SUBVENCIONADO",
    "TES PARTICULAR PAGADO", "TES CORP. DE ADMINISTRACIÓN DELEGADA",
]


@st.cache_data(show_spinner="Cargando base de matrícula 2017-2025...")
def load_data():
    df = pd.read_parquet("matricula.parquet")
    return df


df_raw = load_data()

# ──────────────────────────────────────────────────────────────────────────
# SIDEBAR — FILTROS GLOBALES (afectan todas las secciones)
# ──────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🎓 Filtros")
st.sidebar.caption("Estos filtros se aplican a todas las secciones del panel.")

tipos = sorted(df_raw[COL_TIPO1].dropna().unique().tolist())
sel_tipos = st.sidebar.multiselect("Tipo de institución", tipos, default=tipos)

regiones = sorted(df_raw[COL_REGION].dropna().unique().tolist())
sel_regiones = st.sidebar.multiselect("Región", regiones, default=regiones)

niveles = sorted(df_raw[COL_NIVEL_GLOBAL].dropna().unique().tolist())
sel_niveles = st.sidebar.multiselect("Nivel de estudios", niveles, default=niveles)

df = df_raw[
    df_raw[COL_TIPO1].isin(sel_tipos)
    & df_raw[COL_REGION].isin(sel_regiones)
    & df_raw[COL_NIVEL_GLOBAL].isin(sel_niveles)
].copy()

st.sidebar.markdown("---")
st.sidebar.caption(
    f"Registros seleccionados: **{len(df):,}** de {len(df_raw):,}".replace(",", ".")
)

if df.empty:
    st.warning("No hay datos para la combinación de filtros seleccionada. Ajusta los filtros en la barra lateral.")
    st.stop()

YEARS = sorted(df[COL_MODALIDAD].index) if False else sorted(df["AÑO"].unique())


def fmt_n(x):
    return f"{x:,.0f}".replace(",", ".")


def fmt_pct(x, digits=1):
    return f"{x:.{digits}f}%"


def wavg(frame, value_col, weight_col):
    d = frame[[value_col, weight_col]].dropna()
    if d[weight_col].sum() == 0:
        return np.nan
    return (d[value_col] * d[weight_col]).sum() / d[weight_col].sum()


# ──────────────────────────────────────────────────────────────────────────
# ENCABEZADO
# ──────────────────────────────────────────────────────────────────────────
st.title("Radiografía de la Educación Superior en Chile")
st.caption("Matrícula 2017 – 2025 · Universidades, Institutos Profesionales y Centros de Formación Técnica")

tab_overview, tab_regional, tab_inst, tab_areas, tab_cdg, tab_genero, tab_etario, tab_tes, tab_explorer, tab_conclusion = st.tabs(
    [
        "📊 Panorama",
        "🗺️ Regiones",
        "🏛️ Instituciones",
        "📚 Áreas del conocimiento",
        "🎯 Control de Gestión",
        "⚖️ Género",
        "👥 Perfil etario",
        "💳 Financiamiento",
        "🔎 Explorador",
        "🚀 Conclusiones",
    ]
)

# ──────────────────────────────────────────────────────────────────────────
# TAB 1 · PANORAMA GENERAL
# ──────────────────────────────────────────────────────────────────────────
with tab_overview:
    by_year = df.groupby("AÑO").agg(
        total=(COL_TOTAL, "sum"),
        primer_anio=(COL_1ER, "sum"),
        mujeres=(COL_MUJ, "sum"),
        hombres=(COL_HOM, "sum"),
    ).reset_index()

    year_min, year_max = by_year["AÑO"].min(), by_year["AÑO"].max()
    total_min = by_year.loc[by_year["AÑO"] == year_min, "total"].iloc[0]
    total_max = by_year.loc[by_year["AÑO"] == year_max, "total"].iloc[0]
    crecimiento = (total_max / total_min - 1) * 100 if total_min else np.nan

    if 2019 in by_year["AÑO"].values and 2020 in by_year["AÑO"].values:
        t2019 = by_year.loc[by_year["AÑO"] == 2019, "total"].iloc[0]
        t2020 = by_year.loc[by_year["AÑO"] == 2020, "total"].iloc[0]
        caida_covid = (t2020 / t2019 - 1) * 100
    else:
        caida_covid = np.nan

    ultimo = by_year.iloc[-1]
    pct_mujeres_ultimo = ultimo["mujeres"] / (ultimo["mujeres"] + ultimo["hombres"]) * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Matrícula total {int(year_max)}", fmt_n(total_max), f"{crecimiento:+.1f}% vs {int(year_min)}")
    c2.metric(f"Matrícula 1er año {int(year_max)}", fmt_n(ultimo["primer_anio"]))
    c3.metric("Caída matrícula 2020 (COVID)", fmt_pct(caida_covid) if not np.isnan(caida_covid) else "s/d")
    c4.metric(f"% Mujeres {int(year_max)}", fmt_pct(pct_mujeres_ultimo))

    st.markdown("### Evolución de la matrícula total")
    fig = px.line(by_year, x="AÑO", y="total", markers=True)
    fig.update_traces(line_color=NAVY, line_width=3, marker=dict(size=8, color=GOLD))
    if not np.isnan(caida_covid):
        fig.add_annotation(
            x=2020, y=t2020, text="Caída COVID-19", showarrow=True, arrowhead=2,
            ax=40, ay=-40, font=dict(color=BRICK), arrowcolor=BRICK,
        )
    fig.update_layout(template=PLOTLY_TEMPLATE, yaxis_title="Matrícula total", height=420)
    st.plotly_chart(fig, width='stretch')

    st.markdown("### Participación de mercado por tipo de institución")
    share = df.groupby(["AÑO", COL_TIPO1])[COL_TOTAL].sum().reset_index()
    share["pct"] = share.groupby("AÑO")[COL_TOTAL].transform(lambda x: x / x.sum() * 100)
    fig2 = px.area(share, x="AÑO", y="pct", color=COL_TIPO1, groupnorm=None)
    fig2.update_layout(
        template=PLOTLY_TEMPLATE, yaxis_title="% de la matrícula total", legend_title="",
        height=420,
    )
    st.plotly_chart(fig2, width='stretch')

# ──────────────────────────────────────────────────────────────────────────
# TAB 2 · REGIONES
# ──────────────────────────────────────────────────────────────────────────
with tab_regional:
    st.markdown("### Matrícula por región")
    year_sel = st.select_slider("Año", options=sorted(df["AÑO"].unique()), value=int(df["AÑO"].max()), key="year_region")

    reg_year = df[df["AÑO"] == year_sel].groupby(COL_REGION)[COL_TOTAL].sum().sort_values(ascending=True).reset_index()
    fig = px.bar(reg_year, x=COL_TOTAL, y=COL_REGION, orientation="h")
    fig.update_traces(marker_color=NAVY)
    fig.update_layout(template=PLOTLY_TEMPLATE, height=550, xaxis_title="Matrícula total", yaxis_title="")
    st.plotly_chart(fig, width='stretch')

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Concentración en la Región Metropolitana")
        conc = df.groupby("AÑO").apply(
            lambda g: g.loc[g[COL_REGION] == "Metropolitana", COL_TOTAL].sum() / g[COL_TOTAL].sum() * 100
        ).reset_index(name="pct_rm")
        fig3 = px.line(conc, x="AÑO", y="pct_rm", markers=True)
        fig3.update_traces(line_color=BRICK, marker=dict(color=BRICK))
        fig3.update_layout(template=PLOTLY_TEMPLATE, yaxis_title="% matrícula nacional en RM", height=380)
        st.plotly_chart(fig3, width='stretch')

    with col_b:
        st.markdown(f"### Crecimiento por región ({int(df['AÑO'].min())}-{int(df['AÑO'].max())})")
        piv = df.groupby(["AÑO", COL_REGION])[COL_TOTAL].sum().reset_index()
        first_y, last_y = piv["AÑO"].min(), piv["AÑO"].max()
        p0 = piv[piv["AÑO"] == first_y].set_index(COL_REGION)[COL_TOTAL]
        p1 = piv[piv["AÑO"] == last_y].set_index(COL_REGION)[COL_TOTAL]
        growth = ((p1 / p0 - 1) * 100).dropna().sort_values().reset_index()
        growth.columns = [COL_REGION, "crecimiento"]
        fig4 = px.bar(growth, x="crecimiento", y=COL_REGION, orientation="h")
        fig4.update_traces(marker_color=[SAGE if v >= 0 else BRICK for v in growth["crecimiento"]])
        fig4.update_layout(template=PLOTLY_TEMPLATE, height=380, xaxis_title="Crecimiento (%)", yaxis_title="")
        st.plotly_chart(fig4, width='stretch')

    st.markdown("### Composición institucional por región")
    treemap_df = df[df["AÑO"] == year_sel].groupby([COL_REGION, COL_TIPO1])[COL_TOTAL].sum().reset_index()
    fig5 = px.treemap(treemap_df, path=[COL_REGION, COL_TIPO1], values=COL_TOTAL)
    fig5.update_layout(template=PLOTLY_TEMPLATE, height=500, margin=dict(t=20, l=10, r=10, b=10))
    st.plotly_chart(fig5, width='stretch')

# ──────────────────────────────────────────────────────────────────────────
# TAB 3 · INSTITUCIONES
# ──────────────────────────────────────────────────────────────────────────
with tab_inst:
    st.markdown("### Evolución por subtipo de institución")
    share2 = df.groupby(["AÑO", COL_TIPO2])[COL_TOTAL].sum().reset_index()
    share2["pct"] = share2.groupby("AÑO")[COL_TOTAL].transform(lambda x: x / x.sum() * 100)
    fig = px.area(share2, x="AÑO", y="pct", color=COL_TIPO2)
    fig.update_layout(template=PLOTLY_TEMPLATE, yaxis_title="% de la matrícula", legend_title="", height=420)
    st.plotly_chart(fig, width='stretch')

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"### Top 15 instituciones · {int(df['AÑO'].max())}")
        top_inst = (
            df[df["AÑO"] == df["AÑO"].max()]
            .groupby(COL_INST)[COL_TOTAL].sum()
            .sort_values(ascending=True).tail(15).reset_index()
        )
        fig2 = px.bar(top_inst, x=COL_TOTAL, y=COL_INST, orientation="h")
        fig2.update_traces(marker_color=NAVY)
        fig2.update_layout(template=PLOTLY_TEMPLATE, height=520, xaxis_title="Matrícula", yaxis_title="")
        st.plotly_chart(fig2, width='stretch')

    with col_b:
        st.markdown("### Acreditación institucional en el tiempo")
        acred = df.groupby(["AÑO", COL_ACRED_INST])[COL_TOTAL].sum().reset_index()
        acred["pct"] = acred.groupby("AÑO")[COL_TOTAL].transform(lambda x: x / x.sum() * 100)
        fig3 = px.bar(acred, x="AÑO", y="pct", color=COL_ACRED_INST, barmode="stack")
        fig3.update_layout(template=PLOTLY_TEMPLATE, yaxis_title="% matrícula", legend_title="", height=520)
        st.plotly_chart(fig3, width='stretch')

# ──────────────────────────────────────────────────────────────────────────
# TAB 4 · ÁREAS DEL CONOCIMIENTO
# ──────────────────────────────────────────────────────────────────────────
with tab_areas:
    st.markdown("### Ranking de áreas del conocimiento: 2017 vs 2025")
    piv_area = df.groupby(["AÑO", COL_AREA])[COL_TOTAL].sum().reset_index()
    y0, y1 = piv_area["AÑO"].min(), piv_area["AÑO"].max()
    a0 = piv_area[piv_area["AÑO"] == y0].set_index(COL_AREA)[COL_TOTAL].rank(ascending=False)
    a1 = piv_area[piv_area["AÑO"] == y1].set_index(COL_AREA)[COL_TOTAL].rank(ascending=False)
    ranks = pd.DataFrame({str(y0): a0, str(y1): a1}).dropna()

    fig = go.Figure()
    for area in ranks.index:
        fig.add_trace(go.Scatter(
            x=[str(y0), str(y1)], y=[ranks.loc[area, str(y0)], ranks.loc[area, str(y1)]],
            mode="lines+markers+text", name=area,
            text=[area, area], textposition=["middle left", "middle right"],
            line=dict(width=2), marker=dict(size=8),
        ))
    fig.update_yaxes(autorange="reversed", title="Ranking (1 = mayor matrícula)", showticklabels=False)
    fig.update_layout(template=PLOTLY_TEMPLATE, showlegend=False, height=520, xaxis_title="")
    st.plotly_chart(fig, width='stretch')

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown(f"### Composición por área · {int(y1)}")
        area_carrera = df[df["AÑO"] == y1].groupby([COL_AREA, "CARRERA CLASIFICACIÓN NIVEL 1"])[COL_TOTAL].sum().reset_index()
        fig2 = px.treemap(area_carrera, path=[COL_AREA, "CARRERA CLASIFICACIÓN NIVEL 1"], values=COL_TOTAL)
        fig2.update_layout(template=PLOTLY_TEMPLATE, height=480, margin=dict(t=10, l=5, r=5, b=5))
        st.plotly_chart(fig2, width='stretch')

    with col_b:
        st.markdown(f"### Variación de matrícula por área ({int(y0)}-{int(y1)})")
        var = ((piv_area[piv_area["AÑO"] == y1].set_index(COL_AREA)[COL_TOTAL]
                / piv_area[piv_area["AÑO"] == y0].set_index(COL_AREA)[COL_TOTAL] - 1) * 100).dropna().sort_values().reset_index()
        var.columns = [COL_AREA, "variacion"]
        fig3 = px.bar(var, x="variacion", y=COL_AREA, orientation="h")
        fig3.update_traces(marker_color=[SAGE if v >= 0 else BRICK for v in var["variacion"]])
        fig3.update_layout(template=PLOTLY_TEMPLATE, height=480, xaxis_title="Variación (%)", yaxis_title="")
        st.plotly_chart(fig3, width='stretch')

# ──────────────────────────────────────────────────────────────────────────
# TAB 5 · CONTROL DE GESTIÓN Y CARRERAS AFINES
# ──────────────────────────────────────────────────────────────────────────
with tab_cdg:
    st.markdown("### Foco: Control de Gestión y carreras afines")
    st.caption(
        "El SIES agrupa \"Ingeniería en Control de Gestión\" como carrera genérica propia. "
        "Aquí se aísla ese grupo y se compara con familias afines de administración, "
        "contabilidad y finanzas. Ajusta la selección según lo que quieras enfatizar."
    )

    CDG_PURA = ["Ingeniería en Control de Gestión"]
    AFINES_DEFAULT = [
        "Contador Auditor",
        "Ingeniería Comercial",
        "Administración de Empresas e Ing. Asociadas",
        "Ingeniería en Finanzas",
        "Ingeniería en Gestión y Control de Calidad",
        "Técnico en Contabilidad General",
        "Técnico en Contabilidad Computacional",
        "Técnico en Contabilidad Tributaria",
        "Técnico en Administración Financiera y Finanzas",
        "Técnico en Administración de Empresas",
        "Técnico en Gestión y Control de Calidad",
    ]
    opciones_genericas = sorted(df[COL_AREA_GENERICA].dropna().unique().tolist())

    sel_afines = st.multiselect(
        "Carreras afines a incluir junto con Control de Gestión",
        [o for o in opciones_genericas if o not in CDG_PURA],
        default=[o for o in AFINES_DEFAULT if o in opciones_genericas],
    )
    grupo_generico = CDG_PURA + sel_afines

    df_cdg = df[df[COL_AREA_GENERICA].isin(grupo_generico)].copy()
    df_pura = df[df[COL_AREA_GENERICA].isin(CDG_PURA)].copy()

    if df_cdg.empty:
        st.warning("No hay datos para esta selección con los filtros actuales de la barra lateral.")
    else:
        last_y = df_cdg["AÑO"].max()
        first_y = df_cdg["AÑO"].min()
        tot_last = df_cdg.loc[df_cdg["AÑO"] == last_y, COL_TOTAL].sum()
        tot_first = df_cdg.loc[df_cdg["AÑO"] == first_y, COL_TOTAL].sum()
        crec_cdg = (tot_last / tot_first - 1) * 100 if tot_first else np.nan
        tot_nacional_last = df.loc[df["AÑO"] == last_y, COL_TOTAL].sum()
        pct_nacional = tot_last / tot_nacional_last * 100 if tot_nacional_last else np.nan
        tot_pura_last = df_pura.loc[df_pura["AÑO"] == last_y, COL_TOTAL].sum()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"Matrícula del grupo · {int(last_y)}", fmt_n(tot_last), f"{crec_cdg:+.1f}% vs {int(first_y)}")
        c2.metric("Ingeniería en Control de Gestión (pura)", fmt_n(tot_pura_last))
        c3.metric("% del total nacional", fmt_pct(pct_nacional))
        c4.metric("N° de programas distintos", df_cdg[COL_CARRERA].nunique())

        st.markdown("### Evolución de matrícula por carrera genérica")
        eng_year = df_cdg.groupby(["AÑO", COL_AREA_GENERICA])[COL_TOTAL].sum().reset_index()
        fig = px.area(eng_year, x="AÑO", y=COL_TOTAL, color=COL_AREA_GENERICA)
        fig.update_layout(template=PLOTLY_TEMPLATE, yaxis_title="Matrícula", legend_title="", height=440)
        st.plotly_chart(fig, width='stretch')

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"### Instituciones que imparten estos programas · {int(last_y)}")
            top_inst_cdg = (
                df_cdg[df_cdg["AÑO"] == last_y]
                .groupby(COL_INST)[COL_TOTAL].sum()
                .sort_values(ascending=True).tail(15).reset_index()
            )
            fig2 = px.bar(top_inst_cdg, x=COL_TOTAL, y=COL_INST, orientation="h")
            fig2.update_traces(marker_color=GOLD)
            fig2.update_layout(template=PLOTLY_TEMPLATE, height=460, xaxis_title="Matrícula", yaxis_title="")
            st.plotly_chart(fig2, width='stretch')

        with col_b:
            st.markdown(f"### Distribución regional · {int(last_y)}")
            reg_cdg = df_cdg[df_cdg["AÑO"] == last_y].groupby(COL_REGION)[COL_TOTAL].sum().sort_values(ascending=True).reset_index()
            fig3 = px.bar(reg_cdg, x=COL_TOTAL, y=COL_REGION, orientation="h")
            fig3.update_traces(marker_color=NAVY)
            fig3.update_layout(template=PLOTLY_TEMPLATE, height=460, xaxis_title="Matrícula", yaxis_title="")
            st.plotly_chart(fig3, width='stretch')

        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown(f"### Universidad, IP o CFT · {int(last_y)}")
            tipo_cdg = df_cdg[df_cdg["AÑO"] == last_y].groupby(COL_TIPO1)[COL_TOTAL].sum().reset_index()
            fig4 = px.pie(tipo_cdg, names=COL_TIPO1, values=COL_TOTAL, hole=0.5)
            fig4.update_layout(template=PLOTLY_TEMPLATE, height=380, legend_title="")
            st.plotly_chart(fig4, width='stretch')

        with col_d:
            st.markdown(f"### Brecha de género en el grupo · {int(last_y)}")
            gen_cdg = df_cdg[df_cdg["AÑO"] == last_y].agg({COL_MUJ: "sum", COL_HOM: "sum"})
            pct_muj_cdg = gen_cdg[COL_MUJ] / (gen_cdg[COL_MUJ] + gen_cdg[COL_HOM]) * 100
            gen_nac = df[df["AÑO"] == last_y].agg({COL_MUJ: "sum", COL_HOM: "sum"})
            pct_muj_nac = gen_nac[COL_MUJ] / (gen_nac[COL_MUJ] + gen_nac[COL_HOM]) * 100
            comp = pd.DataFrame({
                "grupo": ["Control de Gestión y afines", "Promedio nacional"],
                "pct_mujeres": [pct_muj_cdg, pct_muj_nac],
            })
            fig5 = px.bar(comp, x="grupo", y="pct_mujeres")
            fig5.update_traces(marker_color=[GOLD, SLATE])
            fig5.add_hline(y=50, line_dash="dot", line_color=BRICK, annotation_text="Paridad")
            fig5.update_layout(template=PLOTLY_TEMPLATE, height=380, yaxis_title="% mujeres", xaxis_title="")
            st.plotly_chart(fig5, width='stretch')

        st.markdown(f"### Detalle de programas · {int(last_y)}")
        detalle = (
            df_cdg[df_cdg["AÑO"] == last_y]
            .groupby([COL_AREA_GENERICA, COL_CARRERA])
            .agg(matricula=(COL_TOTAL, "sum"), instituciones=(COL_INST, "nunique"))
            .sort_values("matricula", ascending=False)
            .reset_index()
        )
        st.dataframe(detalle, width='stretch', hide_index=True)

# ──────────────────────────────────────────────────────────────────────────
# TAB 6 · GÉNERO
# ──────────────────────────────────────────────────────────────────────────
with tab_genero:
    st.markdown("### Evolución de la proporción de mujeres")
    gyear = df.groupby("AÑO").agg(mujeres=(COL_MUJ, "sum"), hombres=(COL_HOM, "sum")).reset_index()
    gyear["pct_mujeres"] = gyear["mujeres"] / (gyear["mujeres"] + gyear["hombres"]) * 100
    fig = px.line(gyear, x="AÑO", y="pct_mujeres", markers=True)
    fig.add_hline(y=50, line_dash="dot", line_color=SLATE, annotation_text="Paridad (50%)")
    fig.update_traces(line_color=BRICK, marker=dict(color=BRICK))
    fig.update_layout(template=PLOTLY_TEMPLATE, yaxis_title="% mujeres sobre matrícula total", height=400)
    st.plotly_chart(fig, width='stretch')

    st.markdown(f"### Brecha de género por área del conocimiento · {int(df['AÑO'].max())}")
    gen_area = df[df["AÑO"] == df["AÑO"].max()].groupby(COL_AREA).agg(
        mujeres=(COL_MUJ, "sum"), hombres=(COL_HOM, "sum")
    ).reset_index()
    gen_area["pct_mujeres"] = gen_area["mujeres"] / (gen_area["mujeres"] + gen_area["hombres"]) * 100
    gen_area["brecha"] = gen_area["pct_mujeres"] - 50
    gen_area = gen_area.sort_values("brecha")
    fig2 = px.bar(gen_area, x="brecha", y=COL_AREA, orientation="h")
    fig2.update_traces(marker_color=[GOLD if v >= 0 else NAVY for v in gen_area["brecha"]])
    fig2.add_vline(x=0, line_color=SLATE)
    fig2.update_layout(
        template=PLOTLY_TEMPLATE, height=480,
        xaxis_title="Puntos porcentuales respecto a la paridad (50%) · dorado = mayoría mujeres",
        yaxis_title="",
    )
    st.plotly_chart(fig2, width='stretch')

    st.markdown(f"### Mujeres y hombres por tipo de institución · {int(df['AÑO'].max())}")
    gen_tipo = df[df["AÑO"] == df["AÑO"].max()].groupby(COL_TIPO1).agg(
        mujeres=(COL_MUJ, "sum"), hombres=(COL_HOM, "sum")
    ).reset_index().melt(id_vars=COL_TIPO1, value_vars=["mujeres", "hombres"], var_name="sexo", value_name="matricula")
    fig3 = px.bar(gen_tipo, x=COL_TIPO1, y="matricula", color="sexo", barmode="group",
                  color_discrete_map={"mujeres": GOLD, "hombres": NAVY})
    fig3.update_layout(template=PLOTLY_TEMPLATE, height=400, xaxis_title="", legend_title="")
    st.plotly_chart(fig3, width='stretch')

# ──────────────────────────────────────────────────────────────────────────
# TAB 7 · PERFIL ETARIO
# ──────────────────────────────────────────────────────────────────────────
with tab_etario:
    st.markdown("### Edad promedio de la matrícula en el tiempo")
    edad_year = df.groupby("AÑO").apply(
        lambda g: pd.Series({
            "promedio": wavg(g, COL_EDAD_PROM, COL_TOTAL),
            "mujer": wavg(g, COL_EDAD_MUJ, COL_MUJ),
            "hombre": wavg(g, COL_EDAD_HOM, COL_HOM),
        })
    ).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edad_year["AÑO"], y=edad_year["promedio"], name="Promedio general",
                              mode="lines+markers", line=dict(color=NAVY, width=3)))
    fig.add_trace(go.Scatter(x=edad_year["AÑO"], y=edad_year["mujer"], name="Mujeres",
                              mode="lines+markers", line=dict(color=GOLD, dash="dot")))
    fig.add_trace(go.Scatter(x=edad_year["AÑO"], y=edad_year["hombre"], name="Hombres",
                              mode="lines+markers", line=dict(color=SLATE, dash="dot")))
    fig.update_layout(template=PLOTLY_TEMPLATE, yaxis_title="Edad promedio", height=420, legend_title="")
    st.plotly_chart(fig, width='stretch')

    st.markdown("### Distribución por tramo etario en el tiempo")
    edad_dist = df.groupby("AÑO")[RANGOS_EDAD].sum().reset_index()
    edad_dist_pct = edad_dist.copy()
    edad_dist_pct[RANGOS_EDAD] = edad_dist_pct[RANGOS_EDAD].div(edad_dist_pct[RANGOS_EDAD].sum(axis=1), axis=0) * 100
    edad_long = edad_dist_pct.melt(id_vars="AÑO", value_vars=RANGOS_EDAD, var_name="tramo", value_name="pct")
    edad_long["tramo"] = edad_long["tramo"].str.replace("RANGO DE EDAD ", "").str.replace(" AÑOS", "")
    fig2 = px.bar(edad_long, x="AÑO", y="pct", color="tramo", barmode="stack")
    fig2.update_layout(template=PLOTLY_TEMPLATE, yaxis_title="% de la matrícula", height=450, legend_title="Tramo etario")
    st.plotly_chart(fig2, width='stretch')

# ──────────────────────────────────────────────────────────────────────────
# TAB 8 · FINANCIAMIENTO / TES (vulnerabilidad socioeconómica de origen)
# ──────────────────────────────────────────────────────────────────────────
with tab_tes:
    st.markdown("### Tipo de establecimiento de origen (TES) en el tiempo")
    st.caption("TES describe el tipo de colegio (municipal, subvencionado, particular pagado o de administración delegada) del que provienen los estudiantes matriculados.")
    tes_year = df.groupby("AÑO")[TES_COLS].sum().reset_index()
    tes_long = tes_year.melt(id_vars="AÑO", value_vars=TES_COLS, var_name="tes", value_name="total")
    tes_long["tes"] = tes_long["tes"].str.replace("TES ", "").str.title()
    tes_long["pct"] = tes_long.groupby("AÑO")["total"].transform(lambda x: x / x.sum() * 100)
    fig = px.area(tes_long, x="AÑO", y="pct", color="tes")
    fig.update_layout(template=PLOTLY_TEMPLATE, yaxis_title="% de estudiantes con TES informado", height=440, legend_title="")
    st.plotly_chart(fig, width='stretch')

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Cobertura TES promedio nacional")
        cob_year = df.groupby("AÑO").apply(lambda g: wavg(g, COL_COBERTURA_TES, "TOTAL TES")).reset_index(name="cobertura")
        fig2 = px.line(cob_year, x="AÑO", y="cobertura", markers=True)
        fig2.update_traces(line_color=SAGE, marker=dict(color=SAGE))
        fig2.update_layout(template=PLOTLY_TEMPLATE, yaxis_title="% cobertura TES", height=380)
        st.plotly_chart(fig2, width='stretch')

    with col_b:
        st.markdown(f"### Cobertura TES por región · {int(df['AÑO'].max())}")
        cob_region = df[df["AÑO"] == df["AÑO"].max()].groupby(COL_REGION).apply(
            lambda g: wavg(g, COL_COBERTURA_TES, "TOTAL TES")
        ).dropna().sort_values().reset_index(name="cobertura")
        fig3 = px.bar(cob_region, x="cobertura", y=COL_REGION, orientation="h")
        fig3.update_traces(marker_color=SAGE)
        fig3.update_layout(template=PLOTLY_TEMPLATE, height=480, xaxis_title="% cobertura TES", yaxis_title="")
        st.plotly_chart(fig3, width='stretch')

# ──────────────────────────────────────────────────────────────────────────
# TAB 9 · EXPLORADOR INTERACTIVO
# ──────────────────────────────────────────────────────────────────────────
with tab_explorer:
    st.markdown("### Explora los datos filtrados")
    st.caption("Además de los filtros de la barra lateral, puedes acotar por carrera y por año aquí.")

    col1, col2 = st.columns(2)
    with col1:
        year_range = st.slider(
            "Rango de años", int(df["AÑO"].min()), int(df["AÑO"].max()),
            (int(df["AÑO"].min()), int(df["AÑO"].max())),
        )
    with col2:
        areas_sel = st.multiselect("Área del conocimiento", sorted(df[COL_AREA].unique()), default=[])

    df_exp = df[(df["AÑO"] >= year_range[0]) & (df["AÑO"] <= year_range[1])]
    if areas_sel:
        df_exp = df_exp[df_exp[COL_AREA].isin(areas_sel)]

    st.markdown(f"**{len(df_exp):,}** filas seleccionadas".replace(",", "."))

    top_carreras = df_exp.groupby(COL_CARRERA)[COL_TOTAL].sum().sort_values(ascending=True).tail(15).reset_index()
    fig = px.bar(top_carreras, x=COL_TOTAL, y=COL_CARRERA, orientation="h")
    fig.update_traces(marker_color=NAVY)
    fig.update_layout(template=PLOTLY_TEMPLATE, height=500, xaxis_title="Matrícula", yaxis_title="")
    st.plotly_chart(fig, width='stretch')

    with st.expander("Ver tabla de datos filtrados"):
        st.dataframe(df_exp, width='stretch')

    st.download_button(
        "⬇️ Descargar datos filtrados (CSV)",
        data=df_exp.to_csv(index=False).encode("utf-8"),
        file_name="matricula_filtrada.csv",
        mime="text/csv",
    )

# ──────────────────────────────────────────────────────────────────────────
# TAB 10 · CONCLUSIONES Y PROPUESTA DE MEJORA FUTURA
# ──────────────────────────────────────────────────────────────────────────
with tab_conclusion:
    st.markdown("### Principales hallazgos")

    top_growth_area = var.set_index(COL_AREA)["variacion"].idxmax() if 'var' in dir() else None

    insights = [
        f"La matrícula total creció **{crecimiento:+.1f}%** entre {int(year_min)} y {int(year_max)}, "
        f"con una caída puntual de **{caida_covid:.1f}%** en 2020 producto de la pandemia.",
        f"Las mujeres representan hoy el **{pct_mujeres_ultimo:.1f}%** de la matrícula total, "
        f"pero la brecha varía fuertemente por área del conocimiento (ver pestaña Género).",
        f"La Región Metropolitana concentra una parte significativa de la matrícula nacional, "
        f"aunque su participación relativa ha variado en el período analizado (ver pestaña Regiones).",
        "La composición por tipo de establecimiento de origen (TES) permite observar cambios en el "
        "perfil socioeconómico de quienes acceden a la educación superior a lo largo del tiempo.",
        "La matrícula de Ingeniería en Control de Gestión y carreras afines (contabilidad, auditoría, "
        "finanzas, ingeniería comercial) muestra una dinámica propia que se detalla en la pestaña "
        "dedicada, con foco en su crecimiento, distribución institucional y regional.",
    ]
    for ins in insights:
        st.markdown(f'<div class="insight-card">{ins}</div>', unsafe_allow_html=True)

    st.markdown("### Propuesta de mejora y expansión futura")
    st.markdown(
        """
        - **Modelo predictivo de matrícula**: usar la serie 2017-2025 para proyectar matrícula 2026-2028 por
          tipo de institución y área del conocimiento (ej. regresión o modelos de series de tiempo).
        - **Indicador de riesgo de deserción**: cruzar esta base con datos de retención/titulación para
          identificar carreras o instituciones con mayor riesgo, priorizando políticas de acompañamiento.
        - **Panel institucional personalizado**: permitir que cada institución cargue sus credenciales y
          vea solo sus propios datos comparados con el promedio de su tipo (benchmark).
        - **Integración geográfica**: incorporar un mapa real de Chile (geojson por región/comuna) para
          un análisis territorial más preciso que el treemap actual.
        - **Actualización automática**: conectar la app a la fuente oficial (SIES) para que se actualice
          cada año sin intervención manual.
        """
    )

    st.info(
        "Este panel fue construido sobre datos ya limpiados y agrupados en Google Colab, "
        "enfocando el trabajo en Streamlit exclusivamente en la exploración visual e interactiva."
    )