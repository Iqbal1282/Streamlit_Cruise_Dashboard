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

# --- DARK THEME COLORS (Always used) ---
THEME_COLORS = {
    "bg_color": "#0E1117",
    "text_color": "#FAFAFA",
    "sidebar_bg": "#262730",
    "sidebar_text": "#FAFAFA",
    "sidebar_header": "#4FC3F7",
    "sidebar_input_text": "#FAFAFA",
    "sidebar_input_bg": "#1E1E1E",
    "card_bg": "#1E1E1E",
    "border_color": "#110E0E",
    "chart_paper_bg": "#1E1E1E",
    "chart_plot_bg": "#1F1E1E",
    "default_font_color": "#FAFAFA",
    "default_axis_color": "#4FC3F7",
    "file_uploader_color": "#4FC3F7"
}

# 2. HELPER FUNCTIONS (Logic)

def clean_capacity_column(series):
    """Removes commas, dollar signs, and converts to float."""
    return pd.to_numeric(series.astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')


def create_pie_chart(df, label_col, value_col, custom_order, theme_seq, watermark_text, 
                    title_text="Cruise Line Capacity Distribution", 
                    title_y_adjustment=0.0, 
                    label_font_size_multiplier=1.0,
                    font_color_inside="white",
                    font_color_outside="#2c3e50",  # Original color
                    title_font_color="#1f77b4",  # Original color
                    width=900,
                    height=600,
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    watermark_x=1.0,
                    watermark_y=-0.05):
    """
    Generates a Pie Chart with dynamic 'Safety Gutters' on all sides and a 
    dynamically positioned title that tracks the pie chart's movement.
    """
    if custom_order:
        df = df.set_index(label_col).reindex(custom_order).reset_index()

    # 1. ANALYZE DATA COMPLEXITY
    num_slices = len(df)
    max_label_len = df[label_col].astype(str).map(len).max()
    
    # 2. CALCULATE DYNAMIC "SAFETY GUTTERS" (Percentage of figure space)
    # Horizontal Gutter (Left & Right) - Reduced slightly
    h_gutter = min(0.25, 0.10 + (max_label_len * 0.005) + (num_slices * 0.002))
    
    # Vertical Gutter Top - Reduced with adaptive scaling
    # Less aggressive growth for fewer slices
    if num_slices <= 8:
        v_gutter_t = min(0.20, 0.10 + (num_slices * 0.005) + (max_label_len * 0.001))
    elif num_slices <= 15:
        v_gutter_t = min(0.25, 0.12 + (num_slices * 0.006) + (max_label_len * 0.0015))
    else:
        v_gutter_t = min(0.30, 0.15 + (num_slices * 0.007) + (max_label_len * 0.002))
    
    # Vertical Gutter Bottom - Slightly reduced
    v_gutter_b = min(0.12, 0.05 + (num_slices * 0.002))

    # Define the allowed drawing area for the pie circle
    x_domain = [h_gutter, 1 - h_gutter]
    y_domain = [v_gutter_b, 1 - v_gutter_t]
    
    # 3. DYNAMIC TITLE POSITIONING - Optimized
    # Place title closer to the pie chart while ensuring clearance
    y_pie_top = y_domain[1]
    
    # Adaptive title positioning based on number of labels
    if num_slices <= 8:
        # Few labels, title can be closer
        base_title_y_pos = y_pie_top + (v_gutter_t * 0.35)
    elif num_slices <= 15:
        # Moderate labels, medium spacing
        base_title_y_pos = y_pie_top + (v_gutter_t * 0.50)
    else:
        # Many labels, need more clearance
        base_title_y_pos = y_pie_top + (v_gutter_t * 0.60)
    
    # Apply user adjustment (-1 to +1 scale, mapped to -0.5 to +0.5 of v_gutter_t)
    adjusted_title_y_pos = base_title_y_pos + (title_y_adjustment * v_gutter_t * 0.5)
    
    # Ensure title doesn't get too close to figure edge
    adjusted_title_y_pos = min(max(adjusted_title_y_pos, 0.02), 0.98)
    
    # Center calculation for the watermark
    pie_center_y = (y_domain[0] + y_domain[1]) / 2

    # 4. CONSTRUCT THE CHART
    fig = px.pie(
        df, values=value_col, names=label_col, hole=0.4,
        color=label_col, color_discrete_sequence=theme_seq,
        category_orders={label_col: df[label_col].tolist()}
    )

    # Adaptive label positioning to prevent overlap
    if num_slices <= 10:
        textposition = "auto"
    else:
        # For more slices, use a mix of inside/outside positioning
        textposition = "outside"
    
    # Adaptive font sizes based on density with user multiplier
    if num_slices < 10:
        base_inside_font_size = 14
        base_outside_font_size = 12
    elif num_slices < 15:
        base_inside_font_size = 12
        base_outside_font_size = 10
    else:
        base_inside_font_size = 10
        base_outside_font_size = 9
    
    # Apply user font size multiplier
    inside_font_size = int(base_inside_font_size * label_font_size_multiplier)
    outside_font_size = int(base_outside_font_size * label_font_size_multiplier)

    fig.update_traces(
        textposition=textposition,
        texttemplate='<b>%{label}</b><br>%{percent:.1%}',
        
        # Adaptive font size based on slice density with user multiplier
        insidetextfont=dict(size=inside_font_size, color=font_color_inside),
        outsidetextfont=dict(size=outside_font_size, color=font_color_outside),
        
        # Pull out slices slightly for better label visibility
        #pull=[0.02 if num_slices > 8 else 0 for _ in range(num_slices)],
        
        # APPLY DYNAMIC DOMAIN
        domain=dict(x=x_domain, y=y_domain),
        
        #marker=dict(line=dict(color='#FFFFFF', width=1.5)),
        hovertemplate="<b>%{label}</b><br>Capacity: %{value:,}<br>%{percent:.1%}<extra></extra>"
    )

    # Add padding only if needed for many labels
    margin_top = max(40, num_slices * 2)
    
    fig.update_layout(
        width=width, 
        height=height,
        showlegend=False,
        title={
            'text': title_text,
            'y': adjusted_title_y_pos,    # USER-ADJUSTABLE: Title position
            'x': 0.5,
            'xanchor': 'center', 
            'yanchor': 'bottom',
            'font': dict(size=24, color=title_font_color)
        },
        
        # Dynamic margins based on content
        margin=dict(t=margin_top, b=50, l=10, r=10),
        
        # Adjust uniform text settings for better label management
        uniformtext_minsize=8, 
        uniformtext_mode="hide",
        
        # Apply background colors
        paper_bgcolor=paper_bgcolor,
        plot_bgcolor=plot_bgcolor,
        
        # Control label positioning to prevent overlap
        annotations=[
            dict(
                text=watermark_text, showarrow=False, xref="paper", yref="paper", 
                x=watermark_x, y=watermark_y, xanchor="right", yanchor="bottom", 
                font=dict(size=10, color="gray")
            ), 
            dict(
                text=watermark_text, textangle=0, showarrow=False, xref="paper", yref="paper", 
                x=0.5, 
                y=pie_center_y, # Stays centered in the hole as the pie moves
                xanchor="center", yanchor="middle", 
                font=dict(size=45, color="rgba(150, 150, 150, 0.1)")
            )
        ]
    )
    
    # Additional adjustment: If labels are outside, adjust layout for better spacing
    if textposition == "outside":
        fig.update_layout(
            # Add more horizontal space for outside labels
            margin=dict(t=margin_top, b=50, l=50, r=50),
        )
    
    return fig

def create_bar_chart(df, x_col, y_col, theme_scale, watermark_text, 
                    title_text="Caribbean Cruise Capacity by Year",
                    x_label=None,
                    y_label=None,
                    title_font_color="#1f77b4",  # Original color
                    axis_font_color="#1f77b4",  # Original color
                    width=900,
                    height=600,
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    watermark_x=1.0,
                    watermark_y=-0.15):
    """Generates the Bar Chart with custom scale and watermarks."""
    fig = px.bar(df, x=x_col, y=y_col, color=y_col, color_continuous_scale=theme_scale)
    
    # Use custom labels if provided, otherwise use column names
    x_label = x_label if x_label is not None else str(x_col)
    y_label = y_label if y_label is not None else str(y_col)
    
    fig.update_layout(
        title={
            'text': title_text, 
            'y': 0.95, 
            'x': 0.5, 
            'xanchor': 'center', 
            'yanchor': 'top',
            'font': dict(color=title_font_color)
        },
        width=width, 
        height=height, 
        title_font_size=24,
        xaxis_title=x_label,
        yaxis_title=y_label,
        xaxis=dict(
            title_font=dict(color=axis_font_color),
            tickfont=dict(color=axis_font_color),
            tickmode='linear', 
            dtick=1
        ),
        yaxis=dict(
            title_font=dict(color=axis_font_color),
            tickfont=dict(color=axis_font_color),
            gridcolor="#0C0C0C",              # ✅ DARK gridlines
            tickformat=','
        ),
        coloraxis_showscale=False, 
        # Apply background colors
        paper_bgcolor=paper_bgcolor,
        plot_bgcolor=plot_bgcolor,
        annotations=[
            dict(
                text=watermark_text, showarrow=False, xref="paper", yref="paper", 
                x=watermark_x, y=watermark_y, xanchor='right', yanchor='bottom', 
                font=dict(size=10, color="gray")
            ), 
            dict(
                text=watermark_text, textangle=0, showarrow=False, xref="paper", yref="paper", 
                x=0.5, y=0.5, xanchor="center", yanchor="middle", 
                font=dict(size=40, color="rgba(150, 150, 150, 0.15)")
            )
        ]
    )
    return fig

# 3. MAIN APP INTERFACE
st.title("🚢 Cruise Capacity Dashboard")
st.markdown("---")

st.markdown(f"""
<style>

/* =====================
   WIDGET LABELS
===================== */

label,
legend {{
    color: #E6E6E6 !important;
    font-weight: 500;
}}

/* =====================
   FILE UPLOADER (FIXED)
===================== */

div[data-testid="stFileUploader"] * {{
    color: #DADADA !important;
}}

/* =====================
   MARKDOWN TEXT (SAFE)
===================== */

/* Only markdown body text — no spans */
div[data-testid="stMarkdownContainer"] p {{
    color: #E0E0E0;
}}

/* =====================
   HEADERS (NO CONFLICT)
===================== */

h1 {{
    color: {THEME_COLORS['text_color']} !important;
}}

h2 {{
    color: #F5F5F5 !important;
}}

h3 {{
    color: #EDEDED !important;
}}

h4, h5 {{
    color: #E0E0E0 !important;
}}

/* =====================
   SLIDER VALUE TEXT
===================== */

div[data-testid="stSlider"] span {{
    color: #E6E6E6 !important;
}}

/* =========================
   BASE APP + BODY
========================= */

.stApp {{
    background-color: {THEME_COLORS['bg_color']} !important;
    color: {THEME_COLORS['text_color']} !important;
}}

.block-container {{
    background-color: {THEME_COLORS['bg_color']} !important;
    padding-top: 3.5rem;
    padding-bottom: 2rem;
}}

/* =========================
   TOP HEADER
========================= */

header[data-testid="stHeader"] {{
    background-color: {THEME_COLORS['bg_color']} !important;
    border-bottom: 1px solid {THEME_COLORS['border_color']};
}}

/* =========================
   SIDEBAR (COMPLETE)
========================= */

section[data-testid="stSidebar"] {{
    background-color: {THEME_COLORS['sidebar_bg']} !important;
    border-right: 1px solid {THEME_COLORS['border_color']};
}}

section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] legend {{
    color: {THEME_COLORS['sidebar_text']} !important;
}}

/* Sidebar inputs */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] select {{
    background-color: {THEME_COLORS['sidebar_input_bg']} !important;
    color: {THEME_COLORS['sidebar_input_text']} !important;
    border: 1px solid {THEME_COLORS['border_color']} !important;
    border-radius: 6px;
}}

/* Sidebar buttons */
section[data-testid="stSidebar"] button {{
    background-color: {THEME_COLORS['sidebar_input_bg']} !important;
    color: {THEME_COLORS['sidebar_text']} !important;
    border: 1px solid {THEME_COLORS['border_color']} !important;
}}

/* =========================
   SECTION SEPARATORS
========================= */

hr {{
    border: 1px solid {THEME_COLORS['border_color']} !important;
}}

/* =========================
   PLOTLY (VISIBILITY)
========================= */

.stPlotlyChart {{
    background-color: {THEME_COLORS['card_bg']} !important;
    border-radius: 10px;
    padding: 0.5rem;
    border: 1px solid {THEME_COLORS['border_color']};
}}

.stPlotlyChart iframe {{
    background-color: {THEME_COLORS['card_bg']} !important;
}}

/* =========================
   EXPANDERS
========================= */

details {{
    background-color: {THEME_COLORS['card_bg']} !important;
    border: 1px solid {THEME_COLORS['border_color']} !important;
    border-radius: 8px;
}}

details summary {{
    color: {THEME_COLORS['text_color']} !important;
    font-weight: 600;
}}

/* =========================
   DATAFRAME
========================= */

.stDataFrame {{
    background-color: {THEME_COLORS['card_bg']} !important;
    border-radius: 8px;
    border: 1px solid {THEME_COLORS['border_color']};
}}

/* =========================
   INFO / ALERTS
========================= */

.stAlert {{
    background-color: {THEME_COLORS['card_bg']} !important;
    color: {THEME_COLORS['text_color']} !important;
    border: 1px solid {THEME_COLORS['border_color']} !important;
}}

</style>
""", unsafe_allow_html=True)




# ----------  FILE UPLOADS  ----------
pie_file = st.sidebar.file_uploader("📊 Upload Pie-Chart Excel", type=["xlsx", "xls"], key="pie")
bar_file = st.sidebar.file_uploader("📊 Upload Bar-Chart Excel", type=["xlsx", "xls"], key="bar")

# ----------  ADVANCED SETTINGS (Expanded) ----------
st.sidebar.markdown("### ⚙️ Advanced Settings")
show_advanced = st.sidebar.checkbox("Show Advanced Settings", value=False)

# Initialize session state for advanced settings
if 'pie_title_y_adjustment' not in st.session_state:
    st.session_state.pie_title_y_adjustment = 0.0
if 'pie_label_font_multiplier' not in st.session_state:
    st.session_state.pie_label_font_multiplier = 1.0
if 'pie_title_text' not in st.session_state:
    st.session_state.pie_title_text = "Cruise Line Capacity Distribution"
if 'bar_title_text' not in st.session_state:
    st.session_state.bar_title_text = "Caribbean Cruise Capacity by Year"
if 'pie_font_color_inside' not in st.session_state:
    st.session_state.pie_font_color_inside = "#FFFFFF"
if 'pie_font_color_outside' not in st.session_state:
    st.session_state.pie_font_color_outside = "#E0E0E0"  # Changed for dark theme visibility
if 'pie_title_font_color' not in st.session_state:
    st.session_state.pie_title_font_color = "#4FC3F7"  # Changed for dark theme
if 'bar_title_font_color' not in st.session_state:
    st.session_state.bar_title_font_color = "#4FC3F7"  # Changed for dark theme
if 'bar_x_label' not in st.session_state:
    st.session_state.bar_x_label = ""
if 'bar_y_label' not in st.session_state:
    st.session_state.bar_y_label = ""
if 'bar_axis_font_color' not in st.session_state:
    st.session_state.bar_axis_font_color = "#4FC3F7"  # Changed for dark theme
if 'pie_aspect_ratio' not in st.session_state:
    st.session_state.pie_aspect_ratio = "3:2"
if 'bar_aspect_ratio' not in st.session_state:
    st.session_state.bar_aspect_ratio = "3:2"
if 'chart_size_multiplier' not in st.session_state:
    st.session_state.chart_size_multiplier = 1.0
if 'pie_watermark_x' not in st.session_state:
    st.session_state.pie_watermark_x = 1.0
if 'pie_watermark_y' not in st.session_state:
    st.session_state.pie_watermark_y = -0.05
if 'bar_watermark_x' not in st.session_state:
    st.session_state.bar_watermark_x = 1.0
if 'bar_watermark_y' not in st.session_state:
    st.session_state.bar_watermark_y = -0.15

# Aspect ratio options
ASPECT_RATIO_OPTIONS = {
    "1:1": (1, 1),
    "4:3": (4, 3),
    "3:2": (3, 2),
    "16:9": (16, 9),
    "16:10": (16, 10),
    "Custom": None
}

if show_advanced:
    # Chart Size Settings
    st.sidebar.markdown("#### 📏 Chart Size Settings")
    
    st.session_state.chart_size_multiplier = st.sidebar.slider(
        "Chart Size Multiplier",
        min_value=0.5,
        max_value=2.0,
        value=st.session_state.chart_size_multiplier,
        step=0.1,
        help="Adjust overall chart size (0.5 = 50% smaller, 2.0 = 200% larger)"
    )
    
    # Pie Chart Aspect Ratio
    st.sidebar.markdown("##### Pie Chart Aspect Ratio")
    st.session_state.pie_aspect_ratio = st.sidebar.selectbox(
        "Pie Chart Ratio",
        options=list(ASPECT_RATIO_OPTIONS.keys()),
        index=list(ASPECT_RATIO_OPTIONS.keys()).index(st.session_state.pie_aspect_ratio),
        key="pie_aspect_ratio_select",
        help="Select aspect ratio for pie chart"
    )
    
    # Bar Chart Aspect Ratio
    st.sidebar.markdown("##### Bar Chart Aspect Ratio")
    st.session_state.bar_aspect_ratio = st.sidebar.selectbox(
        "Bar Chart Ratio",
        options=list(ASPECT_RATIO_OPTIONS.keys()),
        index=list(ASPECT_RATIO_OPTIONS.keys()).index(st.session_state.bar_aspect_ratio),
        key="bar_aspect_ratio_select",
        help="Select aspect ratio for bar chart"
    )
    
    # Pie Chart Advanced Settings
    st.sidebar.markdown("#### 🥧 Pie Chart Settings")
    
    # Title text input
    st.session_state.pie_title_text = st.sidebar.text_input(
        "Pie Chart Title", 
        value=st.session_state.pie_title_text,
        key="pie_title_input"
    )
    
    # Title position adjustment slider
    st.session_state.pie_title_y_adjustment = st.sidebar.slider(
        "Title Vertical Position",
        min_value=-1.0,
        max_value=1.0,
        value=st.session_state.pie_title_y_adjustment,
        step=0.1,
        help="Adjust title position (-1 moves down, +1 moves up)"
    )
    
    # Label font size multiplier
    st.session_state.pie_label_font_multiplier = st.sidebar.slider(
        "Label Font Size Multiplier",
        min_value=0.5,
        max_value=2.0,
        value=st.session_state.pie_label_font_multiplier,
        step=0.1,
        help="Multiplier for label font sizes (0.5 = 50% smaller, 2.0 = 200% larger)"
    )
    
    # Watermark position for pie chart
    st.sidebar.markdown("##### Copyright Position")
    col_wm1, col_wm2 = st.sidebar.columns(2)
    with col_wm1:
        st.session_state.pie_watermark_x = st.sidebar.slider(
            "Pie Copyright X",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.pie_watermark_x,
            step=0.05,
            help="X position of copyright (0=left, 1=right)"
        )
    with col_wm2:
        st.session_state.pie_watermark_y = st.sidebar.slider(
            "Pie Copyright Y",
            min_value=-0.5,
            max_value=1.0,
            value=st.session_state.pie_watermark_y,
            step=0.05,
            help="Y position of copyright"
        )
    
    # Font color pickers for pie chart
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.session_state.pie_font_color_inside = st.color_picker(
            "Inside Label Color",
            value=st.session_state.pie_font_color_inside,
            key="pie_color_inside"
        )
    with col2:
        st.session_state.pie_font_color_outside = st.color_picker(
            "Outside Label Color",
            value=st.session_state.pie_font_color_outside,
            key="pie_color_outside"
        )
    
    st.session_state.pie_title_font_color = st.color_picker(
        "Pie Title Color",
        value=st.session_state.pie_title_font_color,
        key="pie_title_color"
    )
    
    # Bar Chart Advanced Settings
    st.sidebar.markdown("#### 📊 Bar Chart Settings")
    
    # Bar chart title text input
    st.session_state.bar_title_text = st.sidebar.text_input(
        "Bar Chart Title", 
        value=st.session_state.bar_title_text,
        key="bar_title_input"
    )
    
    # Watermark position for bar chart
    st.sidebar.markdown("##### Copyright Position")
    col_wm3, col_wm4 = st.sidebar.columns(2)
    with col_wm3:
        st.session_state.bar_watermark_x = st.sidebar.slider(
            "Bar Copyright X",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.bar_watermark_x,
            step=0.05,
            help="X position of copyright (0=left, 1=right)"
        )
    with col_wm4:
        st.session_state.bar_watermark_y = st.sidebar.slider(
            "Bar Copyright Y",
            min_value=-0.5,
            max_value=1.0,
            value=st.session_state.bar_watermark_y,
            step=0.05,
            help="Y position of copyright"
        )
    
    # Bar chart X and Y axis labels
    st.session_state.bar_x_label = st.sidebar.text_input(
        "X-axis Label (Optional)", 
        value=st.session_state.bar_x_label,
        key="bar_x_label_input",
        help="Leave empty to use column name"
    )
    
    st.session_state.bar_y_label = st.sidebar.text_input(
        "Y-axis Label (Optional)", 
        value=st.session_state.bar_y_label,
        key="bar_y_label_input",
        help="Leave empty to use column name"
    )
    
    col3, col4 = st.sidebar.columns(2)
    with col3:
        st.session_state.bar_title_font_color = st.color_picker(
            "Bar Title Color",
            value=st.session_state.bar_title_font_color,
            key="bar_title_color"
        )
    with col4:
        st.session_state.bar_axis_font_color = st.color_picker(
            "Axis Labels Color",
            value=st.session_state.bar_axis_font_color,
            key="bar_axis_color"
        )
    
    # Reset button
    if st.sidebar.button("Reset to Defaults"):
        st.session_state.pie_title_y_adjustment = 0.0
        st.session_state.pie_label_font_multiplier = 1.0
        st.session_state.pie_title_text = "Cruise Line Capacity Distribution"
        st.session_state.bar_title_text = "Caribbean Cruise Capacity by Year"
        st.session_state.pie_font_color_inside = "#FFFFFF"
        st.session_state.pie_font_color_outside = "#E0E0E0"
        st.session_state.pie_title_font_color = "#4FC3F7"
        st.session_state.bar_title_font_color = "#4FC3F7"
        st.session_state.bar_x_label = ""
        st.session_state.bar_y_label = ""
        st.session_state.bar_axis_font_color = "#4FC3F7"
        st.session_state.pie_aspect_ratio = "3:2"
        st.session_state.bar_aspect_ratio = "3:2"
        st.session_state.chart_size_multiplier = 1.0
        st.session_state.pie_watermark_x = 1.0
        st.session_state.pie_watermark_y = -0.05
        st.session_state.bar_watermark_x = 1.0
        st.session_state.bar_watermark_y = -0.15
        st.rerun()

# ----------  SIDEBAR HELPERS  ----------
def build_sidebar(chart_key, df_raw, sheets):
    """Draw the sidebar controls for one chart and return the cleaned df + settings."""
    st.sidebar.markdown(f"### {chart_key.title()} settings")
    sheet = st.sidebar.selectbox(f"{chart_key} sheet:", sheets, key=f"{chart_key}_sheet")
    has_header = st.sidebar.checkbox(f"{chart_key} sheet has header", value=True, key=f"{chart_key}_head")

    df = pd.read_excel(df_raw, sheet_name=sheet, header=0 if has_header else None)
    if not has_header:
        df.columns = [f"Column {i}" for i in range(len(df.columns))]

    label = st.sidebar.selectbox(f"{chart_key} label column:", df.columns, key=f"{chart_key}_label")
    value = st.sidebar.selectbox(f"{chart_key} value column:", df.columns, key=f"{chart_key}_value", index=1)
    theme = st.sidebar.selectbox(f"{chart_key} colour theme:",
                                 list(PIE_THEME_OPTIONS.keys()) if chart_key == "pie" else list(BAR_THEME_OPTIONS.keys()),
                                 key=f"{chart_key}_theme")
    copyright = st.sidebar.text_input(f"{chart_key} watermark:", value="© Data: Cruise Industry News", key=f"{chart_key}_copy")

    cleaned = df[[label, value]].dropna().copy()
    cleaned[value] = clean_capacity_column(cleaned[value])

    order = None
    if chart_key == "pie":
        all_labs = cleaned[label].unique().tolist()
        order = st.sidebar.multiselect(f"{chart_key} display order:", options=all_labs, default=all_labs, key=f"{chart_key}_order")

    return cleaned, label, value, theme, copyright, order

# ----------  COLLECT USER CHOICES & DATA  ----------
pie_ready = pie_file is not None
bar_ready = bar_file is not None

pie_df = pie_label = pie_value = pie_theme = pie_copy = pie_order = None
bar_df = bar_x = bar_y = bar_theme = bar_copy = None

if pie_ready:
    xl_pie = pd.ExcelFile(pie_file)
    pie_df, pie_label, pie_value, pie_theme, pie_copy, pie_order = build_sidebar("pie", xl_pie, xl_pie.sheet_names)

if bar_ready:
    xl_bar = pd.ExcelFile(bar_file)
    bar_df, bar_x, bar_y, bar_theme, bar_copy, _ = build_sidebar("bar", xl_bar, xl_bar.sheet_names)

# ----------  CHART RENDERING  ----------
charts_drawn = 0

# Calculate chart dimensions based on aspect ratio and multiplier
def calculate_dimensions(aspect_ratio_key, multiplier=1.0):
    """Calculate width and height based on aspect ratio and multiplier."""
    base_width = 900
    
    if aspect_ratio_key in ASPECT_RATIO_OPTIONS:
        ratio = ASPECT_RATIO_OPTIONS[aspect_ratio_key]
        if ratio:
            width = int(base_width * multiplier)
            height = int(width * ratio[1] / ratio[0])
            return width, height
    
    # Default to 3:2 if not found
    width = int(base_width * multiplier)
    height = int(width * 2 / 3)
    return width, height

if pie_ready:
    # Calculate pie chart dimensions
    pie_width, pie_height = calculate_dimensions(
        st.session_state.pie_aspect_ratio, 
        st.session_state.chart_size_multiplier
    )
    
    fig_pie = create_pie_chart(
        pie_df, 
        pie_label, 
        pie_value, 
        pie_order, 
        PIE_THEME_OPTIONS[pie_theme], 
        pie_copy,
        title_text=st.session_state.pie_title_text,
        title_y_adjustment=st.session_state.pie_title_y_adjustment,
        label_font_size_multiplier=st.session_state.pie_label_font_multiplier,
        font_color_inside=st.session_state.pie_font_color_inside,
        font_color_outside=st.session_state.pie_font_color_outside,
        title_font_color=st.session_state.pie_title_font_color,
        width=pie_width,
        height=pie_height,
        paper_bgcolor=THEME_COLORS['chart_paper_bg'],
        plot_bgcolor=THEME_COLORS['chart_plot_bg'],
        watermark_x=st.session_state.pie_watermark_x,
        watermark_y=st.session_state.pie_watermark_y
    )
    charts_drawn += 1
    
if bar_ready:
    # Calculate bar chart dimensions
    bar_width, bar_height = calculate_dimensions(
        st.session_state.bar_aspect_ratio, 
        st.session_state.chart_size_multiplier
    )
    
    # Get custom labels or use empty strings (which will be handled as None in the function)
    custom_x_label = st.session_state.bar_x_label if st.session_state.bar_x_label.strip() != "" else None
    custom_y_label = st.session_state.bar_y_label if st.session_state.bar_y_label.strip() != "" else None
    
    fig_bar = create_bar_chart(
        bar_df, 
        bar_x, 
        bar_y, 
        BAR_THEME_OPTIONS[bar_theme], 
        bar_copy,
        title_text=st.session_state.bar_title_text,
        x_label=custom_x_label,
        y_label=custom_y_label,
        title_font_color=st.session_state.bar_title_font_color,
        axis_font_color=st.session_state.bar_axis_font_color,
        width=bar_width,
        height=bar_height,
        paper_bgcolor=THEME_COLORS['chart_paper_bg'],
        plot_bgcolor=THEME_COLORS['chart_plot_bg'],
        watermark_x=st.session_state.bar_watermark_x,
        watermark_y=st.session_state.bar_watermark_y
    )
    charts_drawn += 1

# Display current advanced settings
if show_advanced and (pie_ready or bar_ready):
    with st.expander("📋 Current Advanced Settings"):
        st.write(f"**Dashboard Theme:** Dark (Always)")
        st.write(f"**Chart Size Multiplier:** {st.session_state.chart_size_multiplier}")
        
        if pie_ready:
            st.write("**Pie Chart Settings:**")
            st.write(f"- Aspect Ratio: {st.session_state.pie_aspect_ratio}")
            st.write(f"- Dimensions: {pie_width} × {pie_height} pixels")
            st.write(f"- Title Position Adjustment: {st.session_state.pie_title_y_adjustment}")
            st.write(f"- Label Font Multiplier: {st.session_state.pie_label_font_multiplier}")
            st.write(f"- Inside Label Color: {st.session_state.pie_font_color_inside}")
            st.write(f"- Outside Label Color: {st.session_state.pie_font_color_outside}")
            st.write(f"- Title Color: {st.session_state.pie_title_font_color}")
            st.write(f"- Copyright Position: X={st.session_state.pie_watermark_x}, Y={st.session_state.pie_watermark_y}")
        
        if bar_ready:
            st.write("**Bar Chart Settings:**")
            st.write(f"- Aspect Ratio: {st.session_state.bar_aspect_ratio}")
            st.write(f"- Dimensions: {bar_width} × {bar_height} pixels")
            st.write(f"- Title Color: {st.session_state.bar_title_font_color}")
            st.write(f"- Axis Labels Color: {st.session_state.bar_axis_font_color}")
            st.write(f"- X-axis Label: '{st.session_state.bar_x_label or 'Using column name'}'")
            st.write(f"- Y-axis Label: '{st.session_state.bar_y_label or 'Using column name'}'")
            st.write(f"- Copyright Position: X={st.session_state.bar_watermark_x}, Y={st.session_state.bar_watermark_y}")

# Decide layout
if charts_drawn == 0:
    st.info("👋 Upload at least one Excel file to begin.")
elif charts_drawn == 1:
    # single chart → full width
    if pie_ready:
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    # both → two columns
    c1, c2 = st.columns(2)
    c1.plotly_chart(fig_pie, use_container_width=True)
    c2.plotly_chart(fig_bar, use_container_width=True)

# ----------  DATA PREVIEW  ----------
if pie_ready or bar_ready:
    with st.expander("📊 View mapped data"):
        if pie_ready:
            st.write("Pie source data")
            st.dataframe(pie_df, use_container_width=True)
        if bar_ready:
            st.write("Bar source data")
            st.dataframe(bar_df, use_container_width=True)

# ----------  AUTO-REFRESH  ----------
if st.sidebar.checkbox("Auto-refresh (30 s)"):
    time.sleep(30)
    st.rerun()

# ----------  FOOTER  ----------
st.markdown("---")
st.caption("© Data: Cruise Industry News")