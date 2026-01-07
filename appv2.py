import streamlit as st
import pandas as pd
import plotly.express as px
import time

# Page configuration
st.set_page_config(
    page_title="Cruise Capacity Dashboard",
    page_icon="🚢",
    layout="wide"
)

# --- THEME OPTIONS ---
PIE_THEME_OPTIONS = {
    "Prism": px.colors.qualitative.Prism,
    "Pastel": px.colors.qualitative.Pastel,
    "Bold": px.colors.qualitative.Bold,
    "Safe": px.colors.qualitative.Safe,
    "Plotly": px.colors.qualitative.Plotly,
    "G10": px.colors.qualitative.G10
}

BAR_THEME_OPTIONS = {
    "Blues": "Blues",
    "Viridis": "Viridis",
    "Sunsetdark": "Sunsetdark",
    "Aggrnyl": "Aggrnyl",
    "Plasma": "Plasma",
    "Cividis": "Cividis"
}

# Title
st.title("🚢 Cruise Capacity Dashboard")
st.markdown("---")

# File uploader
uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])

def load_data_from_excel(file_path_or_buffer):
    """Load data from Excel file with two sheets"""
    try:
        df_cruise_lines = pd.read_excel(file_path_or_buffer, sheet_name="Sheet1")
        df_caribbean_yearly = pd.read_excel(file_path_or_buffer, sheet_name="Caribbean")
        
        # Clean up data
        df_cruise_lines = df_cruise_lines[df_cruise_lines['Cruise Line'] != 'Cruise Line'].reset_index(drop=True)
        df_caribbean_yearly = df_caribbean_yearly[df_caribbean_yearly.iloc[:, 0] != 2016].reset_index(drop=True)
        
        df_caribbean_yearly.columns = ['Year', 'Capacity']
        df_caribbean_yearly['Capacity'] = pd.to_numeric(df_caribbean_yearly['Capacity'].astype(str).str.replace(',', ''), errors='coerce')
        
        return df_cruise_lines, df_caribbean_yearly
    except Exception as e:
        st.error(f"Error loading Excel file: {str(e)}")
        return None, None

def create_pie_chart(df, custom_order=None, theme_seq=px.colors.qualitative.Prism, watermark_text=""):
    """Pie chart with clean, non-bold horizontal text and dual watermarks."""
    if custom_order:
        df = (df.set_index("Cruise Line")
                .reindex(custom_order)
                .reset_index())

    fig = px.pie(
        df,
        values="Capacity",
        names="Cruise Line",
        hole=0.4,
        color="Cruise Line",
        color_discrete_sequence=theme_seq,
        category_orders={"Cruise Line": df["Cruise Line"].tolist()}
    )

    fig.update_traces(
        textposition="auto",
        textinfo="percent+label",
        texttemplate='%{label}<br>%{percent:.1%}',
        insidetextfont=dict(size=15, color="white", family="Arial", weight="normal"),
        insidetextorientation="horizontal", 
        hovertemplate="<b>%{label}</b><br>Capacity: %{value:,}<br>%{percent:.1%}<extra></extra>"
    )

    fig.update_layout(
        width=900,
        height=600,
        showlegend=False, 
        title={
            'text': "Cruise Line Capacity Distribution",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        title_font_size=24,
        margin=dict(t=80, b=80, l=50, r=50), 
        uniformtext_minsize=14,
        uniformtext_mode="hide",
        annotations=[
            dict(
                text=watermark_text,
                showarrow=False,
                xref="paper", yref="paper",
                x=1, y=-0.1,
                xanchor="right", yanchor="bottom",
                font=dict(size=10, color="gray")
            ), 
            dict(
                text=watermark_text,
                textangle=0,
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                xanchor="center", yanchor="middle",
                font=dict(size=40, color="rgba(150, 150, 150, 0.12)"),
            )
        ]
    )
    return fig

def create_bar_chart(df, theme_scale='Blues', watermark_text=""):
    """Create bar chart for Caribbean cruise capacity by year"""
    fig = px.bar(
        df,
        x='Year',
        y='Capacity',
        title='Caribbean Cruise Capacity by Year',
        color='Capacity',
        color_continuous_scale=theme_scale
    )
    
    fig.update_layout(
        title = {
            'text': 'Caribbean Cruise Capacity by Year',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        width=900,
        height=600,
        title_font_size=24,
        xaxis_title="Year",
        yaxis_title="Capacity",
        coloraxis_showscale=False, 
        xaxis=dict(tickmode='linear', tick0=2016, dtick=1),
        yaxis=dict(tickformat=','),
        annotations=[
            dict(
                text=watermark_text,
                showarrow=False,
                xref="paper", yref="paper",
                x=1, y=-0.15,
                xanchor='right', yanchor='bottom',
                font=dict(size=10, color="gray")
            ), 
            dict(
                text=watermark_text,
                textangle=0,
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                xanchor="center", yanchor="middle",
                font=dict(size=40, color="rgba(150, 150, 150, 0.15)"),
            )
        ]
    )
    return fig

# Main app logic
if uploaded_file is not None:
    df_cruise_lines, df_caribbean_yearly = load_data_from_excel(uploaded_file)
    
    if df_cruise_lines is not None and df_caribbean_yearly is not None:
        
        # Sidebar for controls
        st.sidebar.header("Chart Controls")
        
        # New independent copyright input
        user_copyright = st.sidebar.text_input("Copyright Text:", value="© Data: Cruise Industry News")
        
        # Independent theme selectors
        pie_theme = st.sidebar.selectbox("Pie Chart Theme:", list(PIE_THEME_OPTIONS.keys()))
        bar_theme = st.sidebar.selectbox("Bar Chart Theme:", list(BAR_THEME_OPTIONS.keys()))
        
        all_companies = df_cruise_lines['Cruise Line'].unique().tolist()
        
        # Allow user to determine the order
        selected_order = st.sidebar.multiselect(
            "Select Order of Companies (Pie Chart):", 
            options=all_companies,
            default=all_companies
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_pie_chart(df_cruise_lines, selected_order, PIE_THEME_OPTIONS[pie_theme], user_copyright), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_bar_chart(df_caribbean_yearly, BAR_THEME_OPTIONS[bar_theme], user_copyright), use_container_width=True)
        
        with st.expander("View Raw Data"):
            col3, col4 = st.columns(2)
            with col3:
                st.subheader("Cruise Line Capacity")
                st.dataframe(df_cruise_lines)
            with col4:
                st.subheader("Caribbean Yearly Capacity")
                st.dataframe(df_caribbean_yearly)
        
        if st.checkbox("Auto-refresh every 30 seconds"):
            time.sleep(30)
            st.rerun()

else:
    st.warning("Please upload the Excel file to view the dashboard.")

# Footer
st.markdown("---")
# Ensure caption updates with user input
st.caption(user_copyright if 'user_copyright' in locals() else "© Data: Cruise Industry News")