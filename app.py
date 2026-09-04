import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# ============================================================
# 1. PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="SMI Implied Volatility Surface",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. CUSTOM DESIGN
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #000000;
        color: #ffffff;
    }

    html, body, [class*="css"] {
        font-family: "Times New Roman", Times, serif;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: "Times New Roman", Times, serif !important;
        color: #ffffff !important;
    }

    p, span, label, div {
        font-family: "Times New Roman", Times, serif;
    }

    h1 {
        font-size: 2.7rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.3rem !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #080808;
        border-right: 1px solid #292929;
    }

    /* The empty Streamlit sidebar header otherwise reserves vertical space. */
    [data-testid="stSidebarHeader"] {
        display: none !important;
    }

    [data-testid="stSidebarContent"] {
        padding-top: 0 !important;
    }

    section[data-testid="stSidebar"] * {
        font-family: "Times New Roman", Times, serif !important;
        color: white;
    }

    /* Keep the settings sidebar permanently visible. */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #111111 !important;
        color: white !important;
        border: 1px solid #444444 !important;
        border-radius: 6px !important;
    }

    hr {
        border-color: #333333 !important;
    }

    .info-box {
        background-color: #0b0b0b;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 18px 20px;
        margin-top: 18px;
        margin-bottom: 20px;
        color: #dddddd;
        font-size: 15px;
    }

    .source-box {
        background-color: #080808;
        border: 1px solid #292929;
        border-radius: 7px;
        padding: 14px 18px;
        margin-top: 5px;
        margin-bottom: 20px;
        color: #cccccc;
        font-size: 14px;
    }

    [data-testid="stCaptionContainer"] {
        color: #cccccc !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 3. LOAD DATA
# ============================================================

FILE = "vol_surface_collection_template (1).xlsx"

df = pd.read_excel(
    FILE,
    sheet_name="raw_data"
)

df["date"] = df["date"].ffill()

df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)


# ============================================================
# 4. AVAILABLE MARKET DATES
# ============================================================

available_dates = (
    df["date"]
    .dropna()
    .drop_duplicates()
    .sort_values(ascending=False)
    .tolist()
)

date_labels = [
    date.strftime("%d %B %Y")
    for date in available_dates
]


# ============================================================
# 5. SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Visualization settings")

    st.markdown("---")

    st.subheader("Market date")

    selected_label = st.selectbox(
        "Select date",
        date_labels,
        label_visibility="collapsed"
    )

    selected_index = date_labels.index(selected_label)
    selected_date = available_dates[selected_index]

    st.markdown("---")

    st.subheader("Display")

    color_scale = st.selectbox(
        "Surface colour scale",
        [
            "Viridis",
            "Plasma",
            "Cividis",
            "Turbo"
        ]
    )

    show_contours = st.checkbox(
        "Show contour lines",
        value=False
    )

    st.markdown(
        """
        <div class="info-box">
        <b>How to explore the surface</b><br><br>

        • Click and drag to rotate.<br>
        • Scroll to zoom.<br>
        • Hover over the surface to inspect values.<br>
        • Select another market date above to update the surface.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 6. PAGE HEADER
# ============================================================

# ============================================================
# 7. FILTER SELECTED DATE
# ============================================================

surface = df[
    df["date"] == selected_date
].copy()


# ============================================================
# 8. MONEYNESS
# ============================================================

moneyness_labels = [
    "80.0%",
    "90.0%",
    "95.0%",
    "97.5%",
    "100.0%",
    "102.5%",
    "105.0%",
    "110.0%",
    "120.0%"
]

moneyness = np.array([
    80,
    90,
    95,
    97.5,
    100,
    102.5,
    105,
    110,
    120
])


# ============================================================
# 9. MATURITY
# ============================================================

tenor_to_months = {
    "1M": 1,
    "3M": 3,
    "6M": 6,
    "1Y": 12
}

surface["months"] = surface["tenor"].map(
    tenor_to_months
)

surface = (
    surface
    .dropna(subset=["months"])
    .sort_values("months")
)


# ============================================================
# 10. IMPLIED VOLATILITY MATRIX
# ============================================================

maturity = surface["months"].values

Z = (
    surface[moneyness_labels]
    .apply(pd.to_numeric, errors="coerce")
    .values
)


# ============================================================
# 11. DOWNLOAD DATA
# ============================================================

download_table = surface[
    ["tenor"] + moneyness_labels
].copy()

download_table = download_table.rename(
    columns={"tenor": "Maturity"}
)

csv_data = download_table.to_csv(
    index=False
).encode("utf-8")

with st.sidebar:

    st.markdown("---")

    st.subheader("Data")

    st.download_button(
        label="Download data (CSV)",
        data=csv_data,
        file_name=(
            "SMI_implied_volatility_"
            + selected_date.strftime("%Y-%m-%d")
            + ".csv"
        ),
        mime="text/csv",
        width="stretch"
    )

    st.caption("**Source:** Bloomberg OVDV data collected for the SMI.")


# ============================================================
# 12. CONTOUR SETTINGS
# ============================================================

if show_contours:

    contour_settings = dict(
        z=dict(
            show=True,
            usecolormap=True,
            highlightcolor="white",
            project_z=True
        )
    )

else:

    contour_settings = dict(
        z=dict(
            show=False
        )
    )


# ============================================================
# 13. CREATE INTERACTIVE 3D SURFACE
# ============================================================

fig = go.Figure(
    data=[
        go.Surface(
            x=moneyness,
            y=maturity,
            z=Z,
            colorscale=color_scale,
            contours=contour_settings,

            colorbar=dict(
                title=dict(
                    text="Implied volatility (%)",
                    font=dict(
                        family="Times New Roman",
                        color="white",
                        size=14
                    )
                ),

                tickfont=dict(
                    family="Times New Roman",
                    color="white",
                    size=12
                ),

                thickness=16,
                len=0.70,
                x=1.02
            ),

            hovertemplate=(
                "<b>Moneyness:</b> %{x:.1f}%<br>"
                "<b>Time to maturity:</b> %{y} months<br>"
                "<b>Implied volatility:</b> %{z:.2f}%"
                "<extra></extra>"
            )
        )
    ]
)


# ============================================================
# 14. PLOT DESIGN
# ============================================================

fig.update_layout(

    title=dict(
        text=(
            "SMI Implied Volatility Surface"
            f"<br><sup>{selected_date.strftime('%d %B %Y')}</sup>"
        ),
        x=0.5,
        xanchor="center",

        font=dict(
            family="Times New Roman",
            color="white",
            size=24
        )
    ),

    font=dict(
        family="Times New Roman",
        color="white",
        size=14
    ),

    paper_bgcolor="black",
    plot_bgcolor="black",

    scene=dict(

        bgcolor="black",

        xaxis=dict(
            title=dict(
                text="Moneyness (S/K, %)",
                font=dict(
                    family="Times New Roman",
                    color="white",
                    size=15
                )
            ),

            tickvals=[
                80,
                90,
                100,
                110,
                120
            ],

            ticktext=[
                "80%",
                "90%",
                "100%",
                "110%",
                "120%"
            ],

            tickfont=dict(
                family="Times New Roman",
                color="white",
                size=12
            ),

            gridcolor="#333333",
            zerolinecolor="#555555",
            backgroundcolor="black",
            showbackground=True
        ),

        yaxis=dict(
            title=dict(
                text="Time to maturity",
                font=dict(
                    family="Times New Roman",
                    color="white",
                    size=15
                )
            ),

            tickvals=[
                1,
                3,
                6,
                12
            ],

            ticktext=[
                "1M",
                "3M",
                "6M",
                "1Y"
            ],

            tickfont=dict(
                family="Times New Roman",
                color="white",
                size=12
            ),

            gridcolor="#333333",
            zerolinecolor="#555555",
            backgroundcolor="black",
            showbackground=True
        ),

        zaxis=dict(
            title=dict(
                text="Implied volatility (%)",
                font=dict(
                    family="Times New Roman",
                    color="white",
                    size=15
                )
            ),

            tickfont=dict(
                family="Times New Roman",
                color="white",
                size=12
            ),

            gridcolor="#333333",
            zerolinecolor="#555555",
            backgroundcolor="black",
            showbackground=True
        ),

        camera=dict(
            eye=dict(
                x=1.55,
                y=1.55,
                z=0.85
            )
        ),

        aspectmode="manual",

        aspectratio=dict(
            x=1.4,
            y=1.0,
            z=0.8
        )
    ),

    height=720,

    margin=dict(
        l=10,
        r=40,
        b=10,
        t=90
    )
)


# ============================================================
# 15. DISPLAY INTERACTIVE VISUALIZATION
# ============================================================

st.plotly_chart(
    fig,
    width="stretch",
    config={
        "displaylogo": False,
        "scrollZoom": True
    }
)


# ============================================================
# 16. OPTIONAL DATA TABLE
# ============================================================

with st.expander("View underlying volatility data"):

    st.dataframe(
        download_table,
        width="stretch",
        hide_index=True
    )
