import streamlit as st
import pandas as pd
import plotly.express as px

# ------------ FONT, PAGE, BACKGROUND ---------------
st.set_page_config(page_title="Netflix Interactive Dashboard", layout="wide", page_icon="🎬")
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
            background: linear-gradient(180deg,#191c27 0%,#131418 100%) !important;
        }
        div[data-testid="stSidebar"] {width: 300px; min-width: 270px;}
        .block-container {padding-top: 12px;}
        hr {border: none; border-top: 1.8px solid #21244b; margin:18px 0;}
    </style>
    """, unsafe_allow_html=True)

# ------------ DATA LOADING ---------------
@st.cache_data
def load_data():
    return pd.read_csv("netflix_movies_cleaned.csv")
df = load_data()

# ------------ SIDEBAR ----------------
with st.sidebar:
    st.markdown("""
        <style>
            .stSlider, .stSelectbox, .stMultiSelect {margin-bottom:22px !important;}
            .stMultiSelect > div:first-child {border-radius:12px !important;}
            label, .stSlider {font-size:17px !important;}
            .css-nahz7x {color:#b7badc;}
        </style>
    """, unsafe_allow_html=True)
    genre_list = sorted({g for gl in df['Genre'].apply(eval) for g in gl})
    genre_select = st.multiselect("Select Genre(s)", genre_list, default=genre_list[:5])
    year_range = st.slider("Release Year", int(df['Release_Year'].min()), int(df['Release_Year'].max()),
                          (2010, int(df['Release_Year'].max())), step=1)
    rating_range = st.slider("Rating Range", float(df['Vote_Average'].min()), float(df['Vote_Average'].max()),
                          (float(df['Vote_Average'].min()), float(df['Vote_Average'].max())), step=0.1)
    st.markdown("""
        <div style="position: fixed; bottom: 32px; left: 22px; width:260px; text-align:center; color:#b7badc; font-weight:700; font-size:15.5px;">
        Personalized Netflix dashboard by Harshita Goyal
        </div>
    """, unsafe_allow_html=True)

# ------------ DATA FILTERING ----------------
filtered_df = df[
    (df['Release_Year'] >= year_range[0]) &
    (df['Release_Year'] <= year_range[1]) &
    (df['Vote_Average'] >= rating_range[0]) &
    (df['Vote_Average'] <= rating_range[1])
]
if genre_select:
    filtered_df = filtered_df[filtered_df['Genre'].apply(lambda gl: any(g in eval(gl) for g in genre_select))]

# ------------ METRIC CARD FUNCTION ---------------
def metric_card(label, value, icon):
    return f"""
        <div style="background:#1a1f2b;padding:26px 0 20px 0;min-width:190px;max-width:250px;border-radius:20px;
        box-shadow:0 2px 17px #2224;display:flex;flex-direction:column;align-items:center;
        justify-content:center;text-align:center;margin:0 14px;">
            <span style="font-size:40px;">{icon}</span>
            <span style="color:#c5cae8;font-weight:700;font-size:17px;margin-top:3px;">{label}</span>
            <span style="color:#f6f7fd;font-weight:800;font-size:32px;letter-spacing:0.5px;">{value}</span>
        </div>
    """

# ----------- TOP METRICS (HORIZONTAL ROW, LARGER) -------------
colm1, colm2, colm3, colm4 = st.columns([1,1,1,1])
with colm1:
    st.markdown(metric_card("Total Movies", len(filtered_df), "📊"), unsafe_allow_html=True)
with colm2:
    st.markdown(metric_card("Avg Rating", f"{filtered_df['Vote_Average'].mean():.2f}", "⭐"), unsafe_allow_html=True)
with colm3:
    st.markdown(metric_card("Avg Popularity", f"{filtered_df['Popularity'].mean():.1f}", "🔥"), unsafe_allow_html=True)
with colm4:
    st.markdown(metric_card("Year Range", f"{year_range[0]} - {year_range[1]}", "📅"), unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ------------ MAIN CHARTS (2x2 GRID, LARGE) -------------
chart1, chart2 = st.columns([1,1])
with chart1:
    st.markdown("<div style='background:#1a1f2b;padding:23px 21px 17px 21px;border-radius:16px;box-shadow:0 2px 16px #2223;margin-bottom:17px;'>", unsafe_allow_html=True)
    st.subheader("Genre Distribution (Top 7)")
    genre_flat = [g for gl in filtered_df['Genre'].apply(eval) for g in gl]
    genres, counts = zip(*pd.Series(genre_flat).value_counts().iloc[:7].items()) if genre_flat else ([], [])
    pie_df = pd.DataFrame({'Genre': genres, 'Count': counts})
    pastel = ['#ffe1be','#dbf5ce','#d8d7f6','#c7e8f7','#fec3c7','#f6e3f6','#e9d9fd']
    fig_pie = px.pie(
        pie_df, names='Genre', values='Count',
        color_discrete_sequence=pastel, height=370)
    fig_pie.update_traces(textinfo='percent+label', pull=0.06)
    fig_pie.update_layout(
        margin=dict(t=25,r=12,b=18,l=12),
        font=dict(family='Inter', size=15),
        hoverlabel=dict(bgcolor="#24273a", font_size=16),
        annotations=[dict(text="💡 Tip: Click a genre slice to filter dashboard", font_size=14,
                          font_color="#db8a37", showarrow=False, x=0.5, y=0.52)]
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with chart2:
    st.markdown("<div style='background:#1a1f2b;padding:23px 21px 17px 21px;border-radius:16px;box-shadow:0 2px 16px #2223;margin-bottom:17px;'>", unsafe_allow_html=True)
    st.subheader("Movies Released Per Year (+ Examples)")
    line_df = (
        filtered_df.groupby('Release_Year')['Title']
        .apply(lambda x: ', '.join([str(i) for i in x.dropna().unique()][:3]))
        .reset_index(name='Examples')
    )
    line_df['Count'] = filtered_df.groupby('Release_Year')['Title'].size().values
    fig_line = px.line(
        line_df, x='Release_Year', y='Count', markers=True,
        hover_data=['Examples'], color_discrete_sequence=['#fec3c7'], height=370)
    fig_line.update_traces(marker_size=7)
    fig_line.update_layout(
        margin=dict(t=25,r=12,b=18,l=12),
        font=dict(family='Inter', size=15),
        hoverlabel=dict(bgcolor="#24273a", font_size=15)
    )
    st.plotly_chart(fig_line, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

chart3, chart4 = st.columns([1,1])
with chart3:
    st.markdown("<div style='background:#1a1f2b;padding:23px 21px 14px 21px;border-radius:16px;box-shadow:0 2px 16px #2223;margin-bottom:7px;'>", unsafe_allow_html=True)
    st.subheader("💯 Popularity vs Average Rating")
    fig_scatter = px.scatter(
        filtered_df, x='Vote_Average', y='Popularity',
        hover_data=['Title', 'Release_Year'], color='Popularity',
        color_continuous_scale=['#ffe1be','#fec3c7','#d8d7f6','#dee3fa'], height=350)
    fig_scatter.update_traces(marker=dict(size=5, color="#fec3c7"))
    fig_scatter.update_layout(
        margin=dict(t=22,r=10,b=15,l=12), font=dict(family='Inter', size=14),
        hoverlabel=dict(bgcolor="#24273a", font_size=13)
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with chart4:
    st.markdown("<div style='background:#1a1f2b;padding:23px 21px 14px 21px;border-radius:16px;box-shadow:0 2px 16px #2223;margin-bottom:7px;'>", unsafe_allow_html=True)
    st.subheader("Avg Popularity by Genre")
    df_exploded = filtered_df.explode('Genre')
    avg_pop = df_exploded.groupby('Genre')['Popularity'].mean().sort_values(ascending=False).iloc[:7]
    fig_bar = px.bar(
        avg_pop, x=avg_pop.values, y=avg_pop.index, orientation='h',
        text_auto=".1f", color=avg_pop.values, color_continuous_scale=['#dbf5ce','#d8d7f6','#fec3c7','#f6e3f6'], height=350)
    fig_bar.update_layout(
        yaxis_title=None, xaxis_title="Avg Popularity", coloraxis_showscale=False,
        margin=dict(t=18,r=10,b=14,l=15), font=dict(family='Inter', size=14), hoverlabel=dict(bgcolor="#24273a", font_size=13), bargap=0.35)
    fig_bar.update_yaxes(tickfont=dict(size=13), automargin=True, title=None)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:17px'></div>", unsafe_allow_html=True)

# ------------ FOOTER -------------
st.markdown("""
    <hr>
    <div style='color:#d2d6ff;text-align:center;font-weight:600;font-size:17px;margin-bottom:20px;margin-top:12px;'>
        Crafted by Harshita Goyal | Powered by Streamlit ✦ Plotly
    </div>
""", unsafe_allow_html=True)









