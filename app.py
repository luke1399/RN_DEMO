from __future__ import annotations

import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st

from utils.generate_mock_data import DATA_PATH, generate_measurements


st.set_page_config(page_title="Radio Networks Research Dashboard", layout="wide")

RSRP_COLUMNS = [f"RSRP_{idx}" for idx in range(1, 6)]


@st.cache_data
def load_measurements() -> pd.DataFrame:
    if not DATA_PATH.exists():
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        generate_measurements().to_csv(DATA_PATH, index=False)

    return pd.read_csv(DATA_PATH)


def rsrp_to_color(value: float) -> list[int]:
    if value >= -85:
        return [34, 197, 94, 180]
    if value >= -95:
        return [132, 204, 22, 180]
    if value >= -105:
        return [250, 204, 21, 180]
    if value >= -115:
        return [249, 115, 22, 180]
    return [239, 68, 68, 180]


def prepare_map_frame(df: pd.DataFrame, signal_column: str) -> pd.DataFrame:
    frame = df.copy()
    frame["color"] = frame[signal_column].apply(rsrp_to_color)
    return frame


def build_distribution_chart(df: pd.DataFrame):
    long_df = df.melt(
        id_vars=["LATITUDE", "LONGITUDE"],
        value_vars=RSRP_COLUMNS,
        var_name="Signal",
        value_name="RSRP",
    )

    fig = px.histogram(
        long_df,
        x="RSRP",
        color="Signal",
        nbins=40,
        opacity=0.6,
        barmode="overlay",
        title="Signal Strength Distribution",
    )
    fig.update_layout(
        xaxis_title="RSRP (dBm)",
        yaxis_title="Samples",
        legend_title="Signal",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def build_map(df: pd.DataFrame, signal_column: str) -> pdk.Deck:
    map_df = prepare_map_frame(df, signal_column)

    view_state = pdk.ViewState(
        latitude=map_df["LATITUDE"].mean(),
        longitude=map_df["LONGITUDE"].mean(),
        zoom=11,
        pitch=35,
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[LONGITUDE, LATITUDE]",
        get_fill_color="color",
        get_radius=180,
        radius_min_pixels=5,
        radius_max_pixels=16,
        pickable=True,
        stroked=True,
        get_line_color=[20, 20, 20, 120],
        line_width_min_pixels=1,
    )

    return pdk.Deck(
        map_style="dark",
        initial_view_state=view_state,
        layers=[layer],
        tooltip={
            "html": (
                "<b>Location</b><br/>Lat: {LATITUDE}<br/>Lon: {LONGITUDE}"
                f"<br/><b>{signal_column}</b>: " + "{" + signal_column + "} dBm"
            )
        },
    )


def main() -> None:
    st.title("Radio Networks Research Dashboard")
    st.caption("Interactive exploration of synthetic RSRP measurements with spatial fading patterns.")

    df = load_measurements()

    st.sidebar.header("Filters")
    selected_signal = st.sidebar.selectbox("Signal on map", RSRP_COLUMNS, index=0)
    threshold = st.sidebar.slider("Minimum RSRP threshold (dBm)", -140, -65, -105)

    filtered_df = df[df[selected_signal] >= threshold].copy()

    st.sidebar.metric("Visible samples", len(filtered_df))
    st.sidebar.metric("Average selected RSRP", f"{filtered_df[selected_signal].mean():.1f} dBm" if not filtered_df.empty else "N/A")

    metric_columns = st.columns(3)
    metric_columns[0].metric("Total samples", len(df))
    metric_columns[1].metric("Filtered samples", len(filtered_df))
    metric_columns[2].metric(
        f"{selected_signal} mean",
        f"{filtered_df[selected_signal].mean():.1f} dBm" if not filtered_df.empty else "N/A",
    )

    if filtered_df.empty:
        st.warning("No samples match the current RSRP threshold. Lower the threshold to see coverage.")
        return

    left_col, right_col = st.columns([1.35, 1])

    with left_col:
        st.subheader("Coverage Map")
        st.pydeck_chart(build_map(filtered_df, selected_signal), width="stretch")

    with right_col:
        st.subheader("Signal Distribution")
        st.plotly_chart(build_distribution_chart(filtered_df), width="stretch")

    st.subheader("Filtered Measurements")
    st.dataframe(filtered_df, width="stretch")


if __name__ == "__main__":
    main()
