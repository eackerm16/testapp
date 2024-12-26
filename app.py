import streamlit as st
import pandas as pd
from anthropic import Anthropic
import plotly.express as px
from datetime import datetime

# Initialize Anthropic client
client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

def read_excel_file(uploaded_file):
    """Safely read Excel file"""
    try:
        return pd.read_excel(uploaded_file, engine='openpyxl')
    except Exception as e:
        st.error(f"Error reading Excel file: {str(e)}")
        return None

def generate_insights(data: pd.DataFrame) -> str:
    """Generate AI insights from the data"""
    prompt = f"""
    You are a business analyst. Please analyze this data and provide key insights:
    
    Data Summary:
    {data.describe()}
    
    Please provide:
    1. Key trends and patterns
    2. Notable observations
    3. Business recommendations
    4. Areas of opportunity
    
    Format your response in clear sections with bullet points.
    """
    
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    
    return response.content[0].text

def main():
    st.set_page_config(page_title="AI Report Generator")
    
    st.title("AI Report Generator")
    st.write("Upload your Excel file and get AI-powered insights")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])
    
    if uploaded_file:
        # Read Excel file
        data = read_excel_file(uploaded_file)
        
        if data is not None:
            st.success("File uploaded successfully!")
            
            # Show data preview
            st.subheader("Data Preview")
            st.dataframe(data.head())
            
            if st.button("Generate Report"):
                with st.spinner("Analyzing data..."):
                    try:
                        # Generate insights
                        insights = generate_insights(data)
                        
                        # Display insights
                        st.subheader("AI Insights")
                        st.write(insights)
                        
                        # Create visualizations
                        st.subheader("Data Visualization")
                        numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
                        
                        if len(numeric_cols) > 0:
                            # Create a simple bar chart
                            fig = px.bar(
                                data,
                                y=numeric_cols[0],
                                title=f"Analysis of {numeric_cols[0]}"
                            )
                            st.plotly_chart(fig)
                            
                            # Create a histogram
                            fig2 = px.histogram(
                                data,
                                x=numeric_cols[0],
                                title=f"Distribution of {numeric_cols[0]}"
                            )
                            st.plotly_chart(fig2)
                            
                    except Exception as e:
                        st.error(f"Error generating analysis: {str(e)}")

if __name__ == "__main__":
    main()
