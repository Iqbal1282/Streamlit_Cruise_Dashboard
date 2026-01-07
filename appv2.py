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

# Copyright text variable
COPYRIGHT_TEXT = "© Data: Cruise Industry News"

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

def create_pie_chart(df, custom_order=None):
    """Pie chart that honours the exact order given by the user."""
    # 1.  If caller gave an order, force the dataframe into that order
    if custom_order:
        df = (df.set_index("Cruise Line")             # make the names the index
                .reindex(custom_order)                # reorder exactly like this
                .reset_index())                       # back to normal column

    # 2.  Build the pie with Plotly Express BUT turn sorting off
    fig = px.pie(
        df,
        values="Capacity",
        names="Cruise Line",
        title="Cruise Line Capacity Distribution",
        hole=0.4,
        color="Cruise Line",                       # keeps colours stable
        color_discrete_sequence=px.colors.qualitative.Pastel,
        category_orders={"Cruise Line": df["Cruise Line"].tolist()}  # << LOCK ORDER
    )

    # 3.  Cosmetic tweaks (unchanged from your original)
    fig.update_traces(
        textposition="auto",
        textinfo="percent+label",
        insidetextfont=dict(size=16, color="white", family="Arial Black"),
        hovertemplate="<b>%{label}</b><br>Capacity: %{value:,}<br>%{percent}<extra></extra>"
    )
    fig.update_layout(
        width=900,
        height=600,
        title={
        'text': "Cruise Line Capacity Distribution",
        'y': 0.95,           # Sets the vertical position
        'x': 0.5,            # Sets the horizontal position (0.5 is center)
        'xanchor': 'center', # Ensures the anchor point is the middle of the text
        'yanchor': 'top'     # Ensures the anchor point is the top of the text
    },
        title_font_size=24,
        title_x=0.5,
        margin=dict(t=80, b=80, l=50, r=150),
        uniformtext_minsize=18,
        uniformtext_mode="hide",
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            traceorder="normal"
        ),
        annotations=[dict(
            text=COPYRIGHT_TEXT,
            showarrow=False,
            xref="paper", yref="paper",
            x=1, y=-0.1,
            xanchor="right", yanchor="bottom",
            font=dict(size=10, color="gray")
        ), 
        dict(
                text=COPYRIGHT_TEXT,
                textangle=-30, # Tilts the text for a watermark look
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                xanchor="center", yanchor="middle",
                font=dict(size=40, color="rgba(150, 150, 150, 0.15)"), # Very faint
                opacity=0.5 # Additional layer of transparency
            )]
    )
    return fig

def create_bar_chart(df):
    """Create bar chart for Caribbean cruise capacity by year"""
    fig = px.bar(
        df,
        x='Year',
        y='Capacity',
        title='Caribbean Cruise Capacity by Year',
        color='Capacity',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        title = {
        'text': 'Caribbean Cruise Capacity by Year',
        'y': 0.95,           # Sets the vertical position
        'x': 0.5,            # Sets the horizontal position (0.5 is center)
        'xanchor': 'center', # Ensures the anchor point is the middle of the text
        'yanchor': 'top'     # Ensures the anchor point is the top of the text
    },
        width=900,
        height=600, # 3:2 Ratio
        title_font_size=24,
        title_x=0.5,
        xaxis_title="Year",
        yaxis_title="Capacity",
        coloraxis_showscale=False, 
        xaxis=dict(tickmode='linear', tick0=2016, dtick=1),
        yaxis=dict(tickformat=','),
        annotations=[dict(
            text=COPYRIGHT_TEXT,
            showarrow=False,
            xref="paper", yref="paper",
            x=1, y=-0.15,
            xanchor='right', yanchor='bottom',
            font=dict(size=10, color="gray")
        ), 
         dict(
                text=COPYRIGHT_TEXT,
                textangle=-30, # Tilts the text for a watermark look
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                xanchor="center", yanchor="middle",
                font=dict(size=40, color="rgba(150, 150, 150, 0.15)"), # Very faint
                opacity=0.5 # Additional layer of transparency
            )]
    )
    
    return fig

# Main app logic
if uploaded_file is not None:
    df_cruise_lines, df_caribbean_yearly = load_data_from_excel(uploaded_file)
    
    if df_cruise_lines is not None and df_caribbean_yearly is not None:
        
        # Sidebar for controls
        st.sidebar.header("Chart Controls")
        all_companies = df_cruise_lines['Cruise Line'].unique().tolist()
        
        # Allow user to determine the order
        selected_order = st.sidebar.multiselect(
            "Select Order of Companies (Pie Chart):", 
            options=all_companies,
            default=all_companies
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_pie_chart(df_cruise_lines, selected_order), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_bar_chart(df_caribbean_yearly), use_container_width=True)
        
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
st.caption(COPYRIGHT_TEXT)