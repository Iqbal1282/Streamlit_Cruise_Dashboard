import streamlit as st
import pandas as pd
import plotly.express as px
import time

# 1. PAGE SETUP
st.set_page_config(
    page_title="Cruise Capacity Dashboard",
    page_icon="🚢",
    layout="wide"
)

# --- THEME DICTIONARIES ---
PIE_THEME_OPTIONS = {
    "Prism": px.colors.qualitative.Prism,
    "Pastel": px.colors.qualitative.Pastel,
    "Bold": px.colors.qualitative.Bold,
    "Safe": px.colors.qualitative.Safe,
    "Plotly": px.colors.qualitative.Plotly,
    "G10": px.colors.qualitative.G10
}

BAR_THEME_OPTIONS = {
    "Viridis": "Viridis",
    "Blues": "Blues",
    "Sunsetdark": "Sunsetdark",
    "Aggrnyl": "Aggrnyl",
    "Plasma": "Plasma",
    "Cividis": "Cividis"
}

# 2. HELPER FUNCTIONS (Logic)

def clean_capacity_column(series):
    """Removes commas, dollar signs, and converts to float."""
    return pd.to_numeric(series.astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')

def create_pie_chart(df, label_col, value_col, custom_order, theme_seq, watermark_text):
    """Generates the Pie Chart with 1-decimal percentage and watermarks."""
    if custom_order:
        df = df.set_index(label_col).reindex(custom_order).reset_index()

    fig = px.pie(
        df, values=value_col, names=label_col, hole=0.4,
        color=label_col, color_discrete_sequence=theme_seq,
        category_orders={label_col: df[label_col].tolist()}
    )

    fig.update_traces(
        textposition="auto",
        texttemplate='%{label}<br>%{percent:.1%}', 
        insidetextfont=dict(size=15, color="white", family="Arial", weight="normal"),
        insidetextorientation="horizontal", 
        #marker=dict(line=dict(color='#FFFFFF', width=2)),
        hovertemplate="<b>%{label}</b><br>Capacity: %{value:,}<br>%{percent:.1%}<extra></extra>"
    )

    fig.update_layout(
        width=900, height=600, showlegend=False,
        title={'text': "Cruise Line Capacity Distribution", 'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
        title_font_size=24,
        margin=dict(t=80, b=80, l=50, r=50), 
        uniformtext_minsize=14, uniformtext_mode="hide",
        annotations=[
            dict(text=watermark_text, showarrow=False, xref="paper", yref="paper", x=1, y=-0.1, xanchor="right", yanchor="bottom", font=dict(size=10, color="gray")), 
            dict(text=watermark_text, textangle=0, showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5, xanchor="center", yanchor="middle", font=dict(size=40, color="rgba(150, 150, 150, 0.12)"))
        ]
    )
    return fig

def create_bar_chart(df, x_col, y_col, theme_scale, watermark_text):
    """Generates the Bar Chart with custom scale and watermarks."""
    fig = px.bar(df, x=x_col, y=y_col, color=y_col, color_continuous_scale=theme_scale)
    
    fig.update_layout(
        title={'text': 'Caribbean Cruise Capacity by Year', 'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
        width=900, height=600, title_font_size=24,
        xaxis_title=str(x_col), yaxis_title=str(y_col),
        coloraxis_showscale=False, 
        xaxis=dict(tickmode='linear', dtick=1),
        yaxis=dict(tickformat=','),
        annotations=[
            dict(text=watermark_text, showarrow=False, xref="paper", yref="paper", x=1, y=-0.15, xanchor='right', yanchor='bottom', font=dict(size=10, color="gray")), 
            dict(text=watermark_text, textangle=0, showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5, xanchor="center", yanchor="middle", font=dict(size=40, color="rgba(150, 150, 150, 0.15)"))
        ]
    )
    return fig

# 3. MAIN APP INTERFACE
st.title("🚢 Cruise Capacity Dashboard")
st.markdown("---")

uploaded_file = st.file_uploader("Upload Excel Data", type=['xlsx', 'xls'])

if uploaded_file is not None:
    # --- DYNAMIC DATA HANDLING ---
    xl = pd.ExcelFile(uploaded_file)
    sheets = xl.sheet_names

    st.sidebar.header("📁 Data Source Mapping")
    pie_sheet_choice = st.sidebar.selectbox("Sheet for Pie Chart:", sheets, index=0)
    bar_sheet_choice = st.sidebar.selectbox("Sheet for Bar Chart:", sheets, index=min(1, len(sheets)-1))

    st.sidebar.markdown("---")
    st.sidebar.subheader("Data Structure")

    # Checkboxes to determine if headers exist
    pie_has_header = st.sidebar.checkbox("Pie Sheet has header row", value=True)
    bar_has_header = st.sidebar.checkbox("Bar Sheet has header row", value=True)

    # Read the data based on whether headers exist or not
    # header=0 uses the first row as names. header=None treats first row as data.
    df_pie_raw = pd.read_excel(xl, sheet_name=pie_sheet_choice, header=0 if pie_has_header else None)
    df_bar_raw = pd.read_excel(xl, sheet_name=bar_sheet_choice, header=0 if bar_has_header else None)

    # If no headers, pandas names columns 0, 1, 2... 
    # We can make them look nicer for the dropdown: "Column 0", "Column 1"
    if not pie_has_header:
        df_pie_raw.columns = [f"Column {i}" for i in range(len(df_pie_raw.columns))]
    if not bar_has_header:
        df_bar_raw.columns = [f"Column {i}" for i in range(len(df_bar_raw.columns))]

    st.sidebar.markdown("---")
    st.sidebar.subheader("Column Mapping")

    # Mapping dropdowns (will show "Column 0" if header is off)
    pie_label_col = st.sidebar.selectbox("Pie: Label Column", df_pie_raw.columns, index=0)
    pie_value_col = st.sidebar.selectbox("Pie: Value Column", df_pie_raw.columns, index=min(1, len(df_pie_raw.columns)-1))

    bar_x_col = st.sidebar.selectbox("Bar: Year (X)", df_bar_raw.columns, index=0)
    bar_y_col = st.sidebar.selectbox("Bar: Capacity (Y)", df_bar_raw.columns, index=min(1, len(df_bar_raw.columns)-1))

    # Sidebar: Customization
    st.sidebar.markdown("---")
    st.sidebar.header("Design & Branding")
    user_copyright = st.sidebar.text_input("Copyright / Watermark:", value="© Data: Cruise Industry News")
    p_theme = st.sidebar.selectbox("Pie Color Theme:", list(PIE_THEME_OPTIONS.keys()))
    b_theme = st.sidebar.selectbox("Bar Color Theme:", list(BAR_THEME_OPTIONS.keys()))
    
    # Final Data Preparation
    df_pie_final = df_pie_raw[[pie_label_col, pie_value_col]].dropna().copy()
    df_pie_final[pie_value_col] = clean_capacity_column(df_pie_final[pie_value_col])
    
    df_bar_final = df_bar_raw[[bar_x_col, bar_y_col]].dropna().copy()
    df_bar_final[bar_y_col] = clean_capacity_column(df_bar_final[bar_y_col])
    
    # Sidebar: Multi-select for Order (Pie Chart)
    all_companies = df_pie_final[pie_label_col].unique().tolist()
    selected_order = st.sidebar.multiselect("Set Display Order:", options=all_companies, default=all_companies)

    # --- CHART DISPLAY ---
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_pie_chart(
            df_pie_final, pie_label_col, pie_value_col, selected_order, 
            PIE_THEME_OPTIONS[p_theme], user_copyright
        ), use_container_width=True)

    with col2:
        st.plotly_chart(create_bar_chart(
            df_bar_final, bar_x_col, bar_y_col, 
            BAR_THEME_OPTIONS[b_theme], user_copyright
        ), use_container_width=True)
    
    # Data Preview
    with st.expander("📊 View Mapped Data Tables"):
        c_left, c_right = st.columns(2)
        c_left.write(f"Source: {pie_sheet_choice}")
        c_left.dataframe(df_pie_final, use_container_width=True)
        c_right.write(f"Source: {bar_sheet_choice}")
        c_right.dataframe(df_bar_final, use_container_width=True)

    if st.checkbox("Auto-refresh (30s)"):
        time.sleep(30)
        st.rerun()

else:
    st.info("👋 Welcome! Please upload an Excel file to start your analysis.")

# Footer
st.markdown("---")
st.caption(user_copyright if 'user_copyright' in locals() else "© Data: Cruise Industry News")