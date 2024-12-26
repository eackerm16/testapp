import streamlit as st
import pandas as pd
from anthropic import Anthropic
import plotly.express as px
from datetime import datetime
import io

# Initialize Anthropic client
client = Anthropic(api_key="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")

def generate_insights(data: pd.DataFrame) -> str:
    """Generate AI insights from the data"""
    prompt = f"""
    You are a business analyst. Please analyze this data and provide key insights:
    
    Data Summary:
    {data.describe()}
    
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

def generate_report(data: pd.DataFrame) -> str:
    """Generate HTML report"""
    insights = generate_insights(data)
    
    # Create visualizations
    fig1 = px.line(data, x=data.index, y=data.select_dtypes(include=['float64', 'int64']).columns[0], 
                   title='Time Series Analysis')
    fig2 = px.histogram(data, x=data.select_dtypes(include=['float64', 'int64']).columns[0], 
                       title='Distribution Analysis')
    
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
                {fig1.to_html()}
                {fig2.to_html()}
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
    
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file:
        try:
            # Read the file
            if uploaded_file.name.endswith('.csv'):
                data = pd.read_csv(uploaded_file)
            else:
                data = pd.read_excel(uploaded_file)
            
            st.success("File uploaded successfully!")
            
            # Show data preview
            st.subheader("Data Preview")
            st.dataframe(data.head())
            
            if st.button("Generate Report"):
                with st.spinner("Generating report..."):
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
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 
