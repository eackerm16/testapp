import streamlit as st
from pypdf import PdfReader
import io
import httpx
from anthropic import Anthropic

def init_anthropic_client():
    """Initialize Anthropic client with API key from secrets"""
    try:
        return Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    except Exception as e:
        return None

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF"""
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def create_presentation(insights):
    """Create presentation from insights"""
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        
        prs = Presentation()
        # Set slide size to 16:9
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        
        # Add title slide
        title_slide = prs.slides.add_slide(prs.slide_layouts[0])
        title_slide.shapes.title.text = "Strategic Analysis"
        
        # Add content slides
        for section in insights.split('\n\n'):
            if section.strip():
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                slide.shapes.title.text = section.split('\n')[0]
                content = slide.shapes.placeholders[1]
                content.text = '\n'.join(section.split('\n')[1:])
        
        # Save to BytesIO
        output = io.BytesIO()
        prs.save(output)
        return output.getvalue()
    except Exception as e:
        st.error(f"Error creating presentation: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="McKinsey-Style Presentation Generator")
    
    st.title("McKinsey-Style Presentation Generator")
    st.write("Upload PDFs and generate professional presentations with AI insights")

    # Check for API key
    if "ANTHROPIC_API_KEY" not in st.secrets:
        st.error("Please set up your Anthropic API key in Streamlit secrets.")
        st.stop()

    # Initialize Anthropic client
    client = init_anthropic_client()
    if client is None:
        st.error("Failed to initialize Anthropic client. Please check your API key.")
        st.stop()

    uploaded_files = st.file_uploader(
        "Upload PDF documents", 
        type=['pdf'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        combined_text = ""
        for pdf_file in uploaded_files:
            text = extract_text_from_pdf(pdf_file)
            combined_text += text + "\n\n"
        
        st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")
        
        if st.button("Generate Presentation"):
            with st.spinner("Analyzing documents and generating presentation..."):
                try:
                    # Generate insights using Claude
                    response = client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=1500,
                        messages=[{
                            "role": "user",
                            "content": f"""
                            Analyze this text and create a structured presentation outline:
                            
                            {combined_text}
                            
                            Format as:
                            1. Executive Summary (2-3 points)
                            2. Key Findings (3-4 points)
                            3. Recommendations (2-3 points)
                            4. Next Steps (2-3 points)
                            """
                        }]
                    )
                    
                    insights = response.content[0].text
                    
                    # Show insights preview
                    st.subheader("Generated Insights")
                    st.write(insights)
                    
                    # Create and offer presentation download
                    pptx_data = create_presentation(insights)
                    if pptx_data:
                        st.download_button(
                            label="Download Presentation",
                            data=pptx_data,
                            file_name="strategic_analysis.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )
                    
                except Exception as e:
                    st.error(f"Error generating analysis: {str(e)}")

if __name__ == "__main__":
    main()
