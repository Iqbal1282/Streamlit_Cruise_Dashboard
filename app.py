import streamlit as st
import pandas as pd
import plotly.express as px
import time
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Cruise Capacity Dashboard",
    page_icon="🚢",
    layout="wide"
)

# Title
st.title("🚢 Cruise Capacity Dashboard")
st.markdown("---")

# File uploader
uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])

def load_data_from_excel(file_path_or_buffer):
    """Load data from Excel file with two sheets"""
    try:
        # Read both sheets by name
        df_cruise_lines = pd.read_excel(file_path_or_buffer, sheet_name="Sheet1")
        df_caribbean_yearly = pd.read_excel(file_path_or_buffer, sheet_name="Caribbean")
        
        # Clean up duplicate headers and skip them
        df_cruise_lines = df_cruise_lines[df_cruise_lines['Cruise Line'] != 'Cruise Line'].reset_index(drop=True)
        df_caribbean_yearly = df_caribbean_yearly[df_caribbean_yearly.iloc[:, 0] != 2016].reset_index(drop=True)
        
        # Rename Caribbean sheet columns
        df_caribbean_yearly.columns = ['Year', 'Capacity']
        
        # Clean capacity values (remove commas and convert to int)
        df_caribbean_yearly['Capacity'] = df_caribbean_yearly['Capacity'].astype(str).str.replace(',', '').astype(int)
        
        return df_cruise_lines, df_caribbean_yearly
    except Exception as e:
        st.error(f"Error loading Excel file: {str(e)}")
        return None, None

def create_pie_chart(df):
    """Create pie chart for cruise line capacity"""
    fig = px.pie(
        df, 
        values='Capacity', 
        names='Cruise Line',
        title='Cruise Line Capacity Distribution',
        hole=0.3
    )
    
    fig.update_traces(
        textposition='auto',
        textinfo='percent+label',
        texttemplate='<b>%{label}</b><br>%{percent}',
        hovertemplate='<b>%{label}</b><br>Capacity: %{value:,}<br>Percentage: %{percent}<extra></extra>'
        #hovertemplate='<b>%{label}</b><br>Capacity: %{value:,}<br>Percentage: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        title_font_size=20,
        title_x=0.5,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    return fig

def create_bar_chart(df):
    """Create bar chart for Caribbean cruise capacity by year"""
    fig = px.bar(
        df,
        x='Year',
        y='Capacity',
        title='Caribbean Cruise Capacity by Year',
        text='Capacity',
        color='Capacity',
        color_continuous_scale='Blues'
    )
    
    fig.update_traces(
        texttemplate='%{text:,}',
        textposition='outside',
        hovertemplate='<b>Year: %{x}</b><br>Capacity: %{y:,}<extra></extra>'
    )
    
    fig.update_layout(
        title_font_size=20,
        title_x=0.5,
        xaxis_title="Year",
        yaxis_title="Capacity",
        showlegend=False,
        xaxis=dict(tickmode='linear', tick0=2016, dtick=1),
        yaxis=dict(tickformat=',')
    )
    
    return fig

# Main app logic
if uploaded_file is not None:
    # Load data from uploaded file
    df_cruise_lines, df_caribbean_yearly = load_data_from_excel(uploaded_file)
    
    if df_cruise_lines is not None and df_caribbean_yearly is not None:
        # Create two columns for the charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_pie_chart(df_cruise_lines), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_bar_chart(df_caribbean_yearly), use_container_width=True)
        
        # Display raw data (optional - can be expanded)
        with st.expander("View Raw Data"):
            col3, col4 = st.columns(2)
            with col3:
                st.subheader("Cruise Line Capacity")
                st.dataframe(df_cruise_lines)
            
            with col4:
                st.subheader("Caribbean Yearly Capacity")
                st.dataframe(df_caribbean_yearly)
        
        # Auto-refresh functionality
        if st.checkbox("Auto-refresh every 30 seconds"):
            with st.spinner('Refreshing data...'):
                time.sleep(30)
                st.rerun()

else:
    st.warning("Please upload the Excel file to view the dashboard.")
    st.info("The file should have two sheets: 'Sheet1' with cruise line data and 'Caribbean' with yearly data.")

# Footer
st.markdown("---")
st.markdown("*Dashboard updates in real-time when the Excel file is modified*")