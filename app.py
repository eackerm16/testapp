import streamlit as st
import pandas as pd
from anthropic import Anthropic
import plotly.express as px
from datetime import datetime
import io
import numpy as np

# Initialize Anthropic client
client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

def validate_data(data: pd.DataFrame) -> bool:
    """Validate the uploaded data"""
    if data.empty:
        st.error("The uploaded file contains no data")
        return False
    
    # Check if there are numeric columns
    numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_columns) == 0:
        st.error("The data must contain at least one numeric column")
        return False
    
    return True

def generate_insights(data: pd.DataFrame) -> str:
    """Generate AI insights from the data"""
    prompt = f"""
    You are a business analyst. Please analyze this data and provide key insights:
    
    Data Summary:
    {data.describe()}
    
    Columns in the dataset:
    {', '.join(data.columns)}
    
    Please provide:
    1. Key trends and patterns in the data
    2. Notable observations
    3. Business recommendations based on the data
    4. Potential areas of concern or opportunity
    
    Format your response in clear sections with bullet points where appropriate.
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

def generate_visualizations(data: pd.DataFrame):
    """Generate visualizations based on data types"""
    numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns
    figures = []
    
    if len(numeric_columns) > 0:
        # Time series if there's a date column
        date_columns = data.select_dtypes(include=['datetime64']).columns
        if len(date_columns) > 0:
            date_col = date_columns[0]
            for num_col in numeric_columns:
                fig = px.line(data, x=date_col, y=num_col, 
                            title=f'{num_col} Over Time')
                figures.append(fig)
        
        # Distribution for numeric columns
        for col in numeric_columns:
            fig = px.histogram(data, x=col, 
                             title=f'Distribution of {col}')
            figures.append(fig)
    
    return figures

def generate_report(data: pd.DataFrame) -> str:
    """Generate HTML report"""
    insights = generate_insights(data)
    figures = generate_visualizations(data)
    
    # Generate HTML report
    report = f"""
    <html>
        <head>
            <title>Business Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .section {{ margin-bottom: 30px; }}
                .insights {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Business Analysis Report</h1>
            <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <div class="section">
                <h2>AI Insights</h2>
                <div class="insights">
                    {insights}
                </div>
            </div>
            
            <div class="section">
                <h2>Data Visualization</h2>
                {"".join([fig.to_html() for fig in figures])}
            </div>
            
            <div class="section">
                <h2>Data Summary</h2>
                {data.describe().to_html()}
            </div>
        </body>
    </html>
    """
    return report

def main():
    st.set_page_config(page_title="AI Report Generator", layout="wide")
    
    st.title("AI Report Generator")
    st.write("Upload your data file and get AI-powered insights")
    
    # Add sample data option
    if st.button("Use Sample Data"):
        # Create sample data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        data = pd.DataFrame({
            'Date': dates,
            'Sales': np.random.uniform(1000, 10000, len(dates)),
            'Units': np.random.randint(50, 500, len(dates))
        })
        st.session_state['data'] = data
        st.success("Sample data loaded!")
    
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file:
        try:
            # Read the file
            if uploaded_file.name.endswith('.csv'):
                data = pd.read_csv(uploaded_file)
            else:
                data = pd.read_excel(uploaded_file)
            
            # Convert date columns
            for col in data.columns:
                if data[col].dtype == 'object':
                    try:
                        data[col] = pd.to_datetime(data[col])
                    except:
                        pass
            
            st.session_state['data'] = data
            st.success("File uploaded successfully!")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return
    
    if 'data' in st.session_state:
        data = st.session_state['data']
        
        # Show data preview
        st.subheader("Data Preview")
        st.dataframe(data.head())
        
        # Show column info
        st.subheader("Column Information")
        col_info = pd.DataFrame({
            'Type': data.dtypes,
            'Non-Null Count': data.count(),
            'Null Count': data.isnull().sum()
        })
        st.dataframe(col_info)
        
        if validate_data(data):
            if st.button("Generate Report"):
                with st.spinner("Generating report..."):
                    try:
                        # Generate report
                        report = generate_report(data)
                        
                        # Create download button
                        report_bytes = report.encode('utf-8')
                        st.download_button(
                            label="Download Report",
                            data=report_bytes,
                            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                            mime="text/html"
                        )
                        
                        # Show preview
                        st.subheader("Report Preview")
                        st.components.v1.html(report, height=600, scrolling=True)
                    except Exception as e:
                        st.error(f"Error generating report: {str(e)}")

if __name__ == "__main__":
    main()
