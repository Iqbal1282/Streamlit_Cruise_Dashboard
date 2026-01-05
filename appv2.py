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
COPYRIGHT_TEXT = "© 2024 Cruise Capacity Dashboard - Confidential"

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
        
        # Sort cruise lines by capacity for the legend order
        df_cruise_lines = df_cruise_lines.sort_values(by='Capacity', ascending=False)
        
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
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent',  # Show only % inside for clarity
        insidetextfont=dict(size=14, color='white'), # Larger, readable %
        hovertemplate='<b>%{label}</b><br>Capacity: %{value:,}<br>%{percent}<extra></extra>'
    )
    
    fig.update_layout(
        width=900,
        height=600, # 3:2 Ratio
        title_font_size=24,
        title_x=0.5,
        margin=dict(t=80, b=80, l=50, r=150), # Reduce blank space
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            traceorder="normal" # Follows the sorted dataframe order
        ),
        annotations=[dict(
            text=COPYRIGHT_TEXT,
            showarrow=False,
            xref="paper", yref="paper",
            x=1, y=-0.1,
            xanchor='right', yanchor='bottom',
            font=dict(size=10, color="gray")
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
    
    fig.update_traces(
        hovertemplate='<b>Year: %{x}</b><br>Capacity: %{y:,}<extra></extra>'
    )
    
    fig.update_layout(
        width=900,
        height=600, # 3:2 Ratio
        title_font_size=24,
        title_x=0.5,
        xaxis_title="Year",
        yaxis_title="Capacity",
        coloraxis_showscale=False, # Removes the capacity bar/legend on the right
        xaxis=dict(tickmode='linear', tick0=2016, dtick=1),
        yaxis=dict(tickformat=','),
        annotations=[dict(
            text=COPYRIGHT_TEXT,
            showarrow=False,
            xref="paper", yref="paper",
            x=1, y=-0.15,
            xanchor='right', yanchor='bottom',
            font=dict(size=10, color="gray")
        )]
    )
    
    return fig

# Main app logic
if uploaded_file is not None:
    df_cruise_lines, df_caribbean_yearly = load_data_from_excel(uploaded_file)
    
    if df_cruise_lines is not None and df_caribbean_yearly is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            # We wrap in a container to help maintain layout
            st.plotly_chart(create_pie_chart(df_cruise_lines), use_container_width=True)
        
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