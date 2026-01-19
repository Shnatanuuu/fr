import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime
import io
import pytz
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
from io import BytesIO

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai_client = OpenAI(api_key=openai_api_key)
else:
    openai_client = None
    st.warning("OpenAI API key not found. Translation features will be limited.")

# Page config
st.set_page_config(
    page_title="Factory Sample Review Report",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chinese cities dictionary
CHINESE_CITIES = {
    "Guangzhou": "广东",
    "Shenzhen": "深圳",
    "Dongguan": "东莞",
    "Foshan": "佛山",
    "Zhongshan": "中山",
    "Huizhou": "惠州",
    "Zhuhai": "珠海",
    "Jiangmen": "江门",
    "Zhaoqing": "肇庆",
    "Shanghai": "上海",
    "Beijing": "北京",
    "Suzhou": "苏州",
    "Hangzhou": "杭州",
    "Ningbo": "宁波",
    "Wenzhou": "温州",
    "Wuhan": "武汉",
    "Chengdu": "成都",
    "Chongqing": "重庆",
    "Tianjin": "天津",
    "Nanjing": "南京",
    "Xi'an": "西安",
    "Qingdao": "青岛",
    "Dalian": "大连",
    "Shenyang": "沈阳",
    "Changsha": "长沙",
    "Zhengzhou": "郑州",
    "Jinan": "济南",
    "Harbin": "哈尔滨",
    "Changchun": "长春",
    "Taiyuan": "太原",
    "Shijiazhuang": "石家庄",
    "Lanzhou": "兰州",
    "Xiamen": "厦门",
    "Fuzhou": "福州",
    "Nanning": "南宁",
    "Kunming": "昆明",
    "Guiyang": "贵阳",
    "Haikou": "海口",
    "Ürümqi": "乌鲁木齐",
    "Lhasa": "拉萨"
}

# Sample types
SAMPLE_TYPES = {
    "Dev.sample": "开发样",
    "Cfm sample": "确认样",
    "Fit sample": "试穿样",
    "Size set": "尺码套样",
    "TOP sample": "大货样",
    "Shipment sample": "船样"
}

# Custom icons
ICONS = {
    "title": "📋",
    "basic_info": "📋",
    "measurements": "📏",
    "sample_review": "👟",
    "conclusion": "✅",
    "signatures": "✍️",
    "generate": "📊",
    "download": "📥",
    "settings": "⚙️",
    "language": "🌐",
    "location": "📍",
    "time": "🕐",
    "info": "ℹ️",
    "factory": "🏭",
    "brand": "🏷️",
    "style": "👕",
    "sales": "👔",
    "tech": "🔧",
    "qc": "👁️",
    "success": "✅",
    "error": "⚠️",
    "warning": "⚠️",
    "upload": "📤",
    "photo": "📷",
    "measure": "📐",
    "check": "✓",
    "dimension": "📏"
}

# Custom CSS with enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        padding: 0.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .section-header {
        font-size: 1.9rem;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        padding: 0.8rem 1.2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-header-icon {
        font-size: 1.8rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.3rem;
        font-weight: 600;
        padding: 1rem 2.5rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        position: relative;
        overflow: hidden;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    .stButton>button:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: 0.5s;
    }
    .stButton>button:hover:before {
        left: 100%;
    }
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.8rem;
        border-radius: 15px;
        color: white;
        margin: 1.5rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-right: 1px solid #dee2e6;
    }
    .stSelectbox, .stTextInput, .stTextArea, .stRadio {
        background-color: white;
        border-radius: 10px;
        padding: 0.8rem;
        box-shadow: 0 3px 6px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
        transition: all 0.3s;
    }
    .stSelectbox:hover, .stTextInput:hover, .stTextArea:hover, .stRadio:hover {
        border-color: #667eea;
        box-shadow: 0 5px 10px rgba(102, 126, 234, 0.1);
    }
    .stExpander {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 1.2rem;
        border: 1px solid #e0e0e0;
        overflow: hidden;
    }
    .stExpander > div:first-child {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px 12px 0 0;
    }
    .measurement-box {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .location-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    }
    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        margin-top: 2rem;
        border-top: 3px solid #667eea;
    }
    .dimension-row {
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 8px;
        padding: 0.5rem;
        margin: 0.2rem 0;
    }
    .check-item {
        font-weight: 600;
        color: #2c3e50;
    }
    .sample-type-badge {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'ui_language' not in st.session_state:
    st.session_state.ui_language = "en"
if 'pdf_language' not in st.session_state:
    st.session_state.pdf_language = "en"
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = "Shanghai"
if 'translations_cache' not in st.session_state:
    st.session_state.translations_cache = {}

# Translation function using GPT-4o mini
def translate_text(text, target_language="zh"):
    """Translate text using GPT-4o mini with caching"""
    if not text or not text.strip():
        return text
    
    # Check cache first
    cache_key = f"{text}_{target_language}"
    if cache_key in st.session_state.translations_cache:
        return st.session_state.translations_cache[cache_key]
    
    # Don't translate numbers or alphanumeric codes
    if text.strip().replace('.', '').replace(',', '').replace('-', '').isdigit():
        st.session_state.translations_cache[cache_key] = text
        return text
    
    if not openai_client:
        # Fallback to simple translations if no API key
        st.session_state.translations_cache[cache_key] = text
        return text
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a professional translator. Translate the following text to {target_language}. Only return the translation, no explanations. Preserve any numbers, dates, and special formatting."},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        translated_text = response.choices[0].message.content.strip()
        st.session_state.translations_cache[cache_key] = translated_text
        return translated_text
    except Exception as e:
        st.warning(f"Translation failed: {str(e)}. Using original text.")
        st.session_state.translations_cache[cache_key] = text
        return text

# Helper function to get translated text with caching
def get_text(key, fallback=None):
    """Get translated text based on current UI language"""
    lang = st.session_state.ui_language
    
    # Base English texts
    texts = {
        "title": "Factory Sample Review Report",
        "basic_info": "Basic Information",
        "measurements": "Sample Measurements",
        "sample_review": "Sample Review",
        "conclusion": "Conclusion",
        "signatures": "Signatures",
        "generate_pdf": "Generate PDF Report",
        "download_pdf": "Download PDF Report",
        "style_no": "Style No. / 型体",
        "size": "Size / 码数",
        "factory": "Factory / 工厂",
        "purpose": "Purpose / 类型",
        "brand": "Brand / 品牌",
        "last_no": "Last No. / 楦号",
        "sales": "Sales / 业务",
        "new_old": "New/Old / 新旧",
        "outsole_no": "Outsole NO. / 大底",
        "review_date": "Review Date / 日期",
        "check_items": "Check Items / 核查项目",
        "first": "First / 第一次",
        "second": "Second / 第二次",
        "third": "Third / 第三次",
        "fourth": "Fourth / 第四次",
        "measurement_details": "Measurement Details",
        "picture": "Picture / 图片",
        "footer_text": "Factory Sample Review System",
        "generate_success": "PDF Generated Successfully!",
        "fill_required": "Please fill in at least Style No. and Factory!",
        "creating_pdf": "Creating your sample review PDF report...",
        "pdf_details": "PDF Details",
        "report_language": "Report Language",
        "generated": "Generated",
        "location": "Location",
        "error_generating": "Error generating PDF",
        "select_location": "Select Location",
        "user_interface_language": "User Interface Language",
        "pdf_report_language": "PDF Report Language",
        "test_location": "Assessment Location",
        "local_time": "Local Time",
        "quick_guide": "Quick Guide",
        "powered_by": "Powered by Streamlit",
        "copyright": "© 2025 - Factory Sample Review Platform",
        "upload_photo": "Upload Sample Photo",
        "conclusion_note": "Conclusion & Notes",
        "disclaimer": "Disclaimer",
        "disclaimer_text": "Note: This review information does not release the factory from any responsibilities in the event of claims being received from our customer.",
        "disclaimer_text_chinese": "以上不免除我客人收到货后索赔而引起的货物供应商(工厂)的任何责任.",
        "measurement_check": "Measurement Check Items",
        "add_measurement": "Add Measurement Point",
        "grandstep_tech": "GrandStep Tech",
        "factory_representative": "Factory Representative"
    }
    
    text = texts.get(key, fallback or key)
    
    # Translate if needed
    if lang == "zh" and openai_client:
        return translate_text(text, "zh")
    return text

def translate_pdf_content(text, pdf_lang):
    """Translate text for PDF based on selected language"""
    if pdf_lang == "en" or not openai_client:
        return text
    return translate_text(text, "zh")

# PDF Generation with Headers and Footers
class SampleReviewPDF(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        self.header_text = kwargs.pop('header_text', '')
        self.location = kwargs.pop('location', '')
        self.pdf_language = kwargs.pop('pdf_language', 'en')
        self.selected_city = kwargs.pop('selected_city', '')
        self.chinese_city = kwargs.pop('chinese_city', '')
        self.chinese_font = kwargs.pop('chinese_font', 'Helvetica')
        super().__init__(*args, **kwargs)
        
    def afterFlowable(self, flowable):
        """Add header and footer"""
        # Add header on all pages except first
        if self.page > 1:
            self.canv.saveState()
            # Header
            self.canv.setFillColor(colors.HexColor('#667eea'))
            self.canv.rect(0, self.pagesize[1] - 0.6*inch, self.pagesize[0], 0.6*inch, fill=1, stroke=0)
            
            # Use Chinese font if needed
            font_size = 12
            if self.pdf_language == "zh":
                self.canv.setFont(self.chinese_font, font_size)
            else:
                self.canv.setFont('Helvetica-Bold', font_size)
                
            self.canv.setFillColor(colors.white)
            header_title = "FACTORY SAMPLE REVIEW REPORT"
            self.canv.drawCentredString(
                self.pagesize[0]/2.0, 
                self.pagesize[1] - 0.4*inch, 
                header_title
            )
            self.canv.restoreState()
            
        # Footer on all pages
        self.canv.saveState()
        
        # Footer background
        self.canv.setFillColor(colors.HexColor('#f8f9fa'))
        self.canv.rect(0, 0, self.pagesize[0], 0.7*inch, fill=1, stroke=0)
        
        # Top border
        self.canv.setStrokeColor(colors.HexColor('#667eea'))
        self.canv.setLineWidth(1)
        self.canv.line(0, 0.7*inch, self.pagesize[0], 0.7*inch)
        
        # Footer text
        font_size = 8
        if self.pdf_language == "zh":
            self.canv.setFont(self.chinese_font, font_size)
        else:
            self.canv.setFont('Helvetica', font_size)
            
        self.canv.setFillColor(colors.HexColor('#666666'))
        
        # Left: Location
        china_tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.now(china_tz)
        
        if self.pdf_language == "zh" and self.chinese_city:
            location_info = f"地点: {self.selected_city} ({self.chinese_city})"
        else:
            location_info = f"Location: {self.selected_city}"
        
        self.canv.drawString(0.5*inch, 0.25*inch, location_info)
        
        # Center: Timestamp
        timestamp = f"Generated: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        self.canv.drawCentredString(self.pagesize[0]/2.0, 0.25*inch, timestamp)
        
        # Right: Page number
        page_num = f"Page {self.page}"
        self.canv.drawRightString(self.pagesize[0] - 0.5*inch, 0.25*inch, page_num)
        
        self.canv.restoreState()

def generate_pdf():
    """Generate Sample Review PDF report"""
    buffer = io.BytesIO()
    
    # Get location info
    selected_city = st.session_state.selected_city
    chinese_city = CHINESE_CITIES[selected_city]
    pdf_lang = st.session_state.pdf_language
    
    # Register Chinese font if needed
    chinese_font = 'Helvetica'
    
    if pdf_lang == "zh":
        try:
            try:
                pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                chinese_font = 'STSong-Light'
            except:
                chinese_font = 'Helvetica'
        except:
            chinese_font = 'Helvetica'
    
    # Create PDF with custom header/footer
    doc = SampleReviewPDF(
        buffer, 
        pagesize=letter,
        topMargin=0.8*inch,
        bottomMargin=0.8*inch,
        header_text="FACTORY SAMPLE REVIEW REPORT",
        location=f"{selected_city}",
        pdf_language=pdf_lang,
        selected_city=selected_city,
        chinese_city=chinese_city,
        chinese_font=chinese_font
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Create styles
    title_font = 'Helvetica-Bold' if pdf_lang != "zh" else chinese_font
    normal_font = 'Helvetica' if pdf_lang != "zh" else chinese_font
    bold_font = 'Helvetica-Bold' if pdf_lang != "zh" else chinese_font
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=5,
        alignment=TA_CENTER,
        fontName=bold_font
    )
    
    # Subtitle style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#764ba2'),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName=bold_font
    )
    
    # Table header style
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.white,
        alignment=TA_CENTER,
        fontName=bold_font
    )
    
    # Table cell style
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        fontName=normal_font
    )
    
    # Normal style
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        fontName=normal_font
    )
    
    # Build the PDF content similar to the provided template
    
    # Title
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Factory Sample Review 样品技术核查表", title_style))
    elements.append(Paragraph("Page# 1", subtitle_style))
    elements.append(Spacer(1, 10))
    
    # Helper function for creating paragraphs
    def create_paragraph(text, style=normal_style, bold=False):
        """Create paragraph with appropriate font"""
        if bold:
            font_name = bold_font
        else:
            font_name = normal_font
        
        custom_style = ParagraphStyle(
            f"CustomStyle_{bold}",
            parent=style,
            fontName=font_name
        )
        
        return Paragraph(text, custom_style)
    
    # Basic Information Table (6 rows, 4 columns)
    # Get values from session state
    style_no_val = st.session_state.get('style_no', '')
    size_val = st.session_state.get('size', '')
    factory_val = st.session_state.get('factory', '')
    purpose_val = st.session_state.get('purpose', '')
    brand_val = st.session_state.get('brand', '')
    last_no_val = st.session_state.get('last_no', '')
    sales_val = st.session_state.get('sales', '')
    new_old_val = st.session_state.get('new_old', '')
    outsole_no_val = st.session_state.get('outsole_no', '')
    review_date_val = st.session_state.get('review_date', datetime.now())
    
    # Sample type badge
    purpose_display = purpose_val
    if purpose_val in SAMPLE_TYPES:
        purpose_display = f"{purpose_val} {SAMPLE_TYPES[purpose_val]}"
    
    basic_data = [
        [
            create_paragraph("Style No.", bold=True), 
            create_paragraph("型体", bold=True), 
            create_paragraph(style_no_val),
            create_paragraph("Size#", bold=True),
            create_paragraph("码数", bold=True),
            create_paragraph(size_val)
        ],
        [
            create_paragraph("Factory", bold=True), 
            create_paragraph("工厂", bold=True), 
            create_paragraph(factory_val),
            create_paragraph("Purpose", bold=True),
            create_paragraph("类型", bold=True),
            create_paragraph(purpose_display)
        ],
        [
            create_paragraph("Brand", bold=True), 
            create_paragraph("品牌", bold=True), 
            create_paragraph(brand_val),
            create_paragraph("Last No.", bold=True),
            create_paragraph("楦号", bold=True),
            create_paragraph(last_no_val)
        ],
        [
            create_paragraph("Sales", bold=True), 
            create_paragraph("业务", bold=True), 
            create_paragraph(sales_val),
            create_paragraph("New/Old", bold=True),
            create_paragraph("新旧", bold=True),
            create_paragraph(new_old_val)
        ],
        [
            create_paragraph("Outsole NO.", bold=True), 
            create_paragraph("大底", bold=True), 
            create_paragraph(outsole_no_val),
            create_paragraph("Review", bold=True),
            create_paragraph("日期", bold=True),
            create_paragraph(review_date_val.strftime('%Y-%m-%d') if hasattr(review_date_val, 'strftime') else str(review_date_val))
        ]
    ]
    
    basic_table = Table(basic_data, colWidths=[0.8*inch, 0.6*inch, 1.2*inch, 0.8*inch, 0.6*inch, 1.2*inch])
    basic_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (1, -1), colors.HexColor('#e0e0e0')),
        ('BACKGROUND', (3, 0), (4, -1), colors.HexColor('#e0e0e0')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    elements.append(basic_table)
    elements.append(Spacer(1, 10))
    
    # Measurement Check Table
    # Define the check items (left side)
    check_items_left = [
        ("Last Length", "楦长"),
        ("Toe Girth", "趾围"),
        ("Ball Girth", "掌围"),
        ("Waist Girth", "腰围"),
        ("Instep Girth", "背围"),
        ("Vamp length:", "鞋口长度"),
        ("Back Height:", "后跟高度"),
        ("Boot Height:", "靴筒高度"),
        ("Boot top Width:", "靴筒宽度"),
        ("Boot Calf Width:", "小腿宽度Point 位置点 298"),
        ("Ankle Width:", "脚踝宽度 Point 位置点 90mm")
    ]
    
    # Define the check items (right side)
    check_items_right = [
        ("Toe Width", "趾  宽"),
        ("Bottom Width", "掌  宽"),
        ("Heel Seat Width", "后跟宽度"),
        ("Heel to Instep Girth", "后跟到脚背长度"),
        ("Toe Spring", "鞋头翘度"),
        ("Sock Foam:", "鞋垫"),
        ("Thickness:", "厚度"),
        ("Shank:", "钢芯"),
        ("Mid-sole:", "中底"),
        ("Outsole Degree", "大底硬度")
    ]
    
    # Create measurement data from session state
    measurement_data = []
    
    # Header row
    header_row = [
        create_paragraph("Check Items", bold=True),
        create_paragraph("核查项目", bold=True),
        create_paragraph("First", bold=True),
        create_paragraph("第一次", bold=True),
        create_paragraph("Second", bold=True),
        create_paragraph("第二次", bold=True),
        create_paragraph("Third", bold=True),
        create_paragraph("第三次", bold=True),
        create_paragraph("Fourth", bold=True),
        create_paragraph("第四次", bold=True),
        create_paragraph("Check Items", bold=True),
        create_paragraph("核查项目", bold=True),
        create_paragraph("First", bold=True),
        create_paragraph("第一次", bold=True),
        create_paragraph("Second", bold=True),
        create_paragraph("第二次", bold=True),
        create_paragraph("Third", bold=True),
        create_paragraph("第三次", bold=True),
        create_paragraph("Fourth", bold=True),
        create_paragraph("第四次", bold=True)
    ]
    measurement_data.append(header_row)
    
    # Get maximum length for iteration
    max_items = max(len(check_items_left), len(check_items_right))
    
    for i in range(max_items):
        row = []
        
        # Left side items
        if i < len(check_items_left):
            item_en, item_zh = check_items_left[i]
            # Get measurement values from session state
            first_val = st.session_state.get(f'{item_en.lower().replace(":", "").replace(" ", "_")}_first', '')
            second_val = st.session_state.get(f'{item_en.lower().replace(":", "").replace(" ", "_")}_second', '')
            third_val = st.session_state.get(f'{item_en.lower().replace(":", "").replace(" ", "_")}_third', '')
            fourth_val = st.session_state.get(f'{item_en.lower().replace(":", "").replace(" ", "_")}_fourth', '')
            
            row.extend([
                create_paragraph(item_en),
                create_paragraph(item_zh),
                create_paragraph(first_val),
                create_paragraph(""),
                create_paragraph(second_val),
                create_paragraph(""),
                create_paragraph(third_val),
                create_paragraph(""),
                create_paragraph(fourth_val),
                create_paragraph("")
            ])
        else:
            # Empty cells for left side
            row.extend([create_paragraph("")] * 10)
        
        # Right side items
        if i < len(check_items_right):
            item_en, item_zh = check_items_right[i]
            # Get measurement values from session state
            first_val = st.session_state.get(f'{item_en.lower().replace(":", "").replace(" ", "_")}_first', '')
            second_val = st.session_state.get(f'{item_en.lower().replace(":", "").replace(" ", "_")}_second', '')
            third_val = st.session_state.get(f'{item_en.lower().replace(":", "").replace(" ", "_")}_third', '')
            fourth_val = st.session_state.get(f'{item_en.lower().replace(":", "").replace(" ", "_")}_fourth', '')
            
            row.extend([
                create_paragraph(item_en),
                create_paragraph(item_zh),
                create_paragraph(first_val),
                create_paragraph(""),
                create_paragraph(second_val),
                create_paragraph(""),
                create_paragraph(third_val),
                create_paragraph(""),
                create_paragraph(fourth_val),
                create_paragraph("")
            ])
        else:
            # Empty cells for right side
            row.extend([create_paragraph("")] * 10)
        
        measurement_data.append(row)
    
    # Add Sock Foam special row (After/Before)
    sock_foam_after = st.session_state.get('sock_foam_after', '')
    sock_foam_before = st.session_state.get('sock_foam_before', '')
    
    sock_row = [create_paragraph("")] * 20
    sock_row[8] = create_paragraph("After 后置")
    sock_row[9] = create_paragraph(sock_foam_after)
    sock_row[10] = create_paragraph("Before 前置")
    sock_row[11] = create_paragraph(sock_foam_before)
    measurement_data.append(sock_row)
    
    # Create the measurement table
    measurement_table = Table(measurement_data, colWidths=[0.6*inch] * 20)
    measurement_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (10, 0), (-1, 0), colors.HexColor('#4a5568')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
    ]))
    elements.append(measurement_table)
    elements.append(Spacer(1, 15))
    
    # Conclusion Section
    conclusion_val = st.session_state.get('conclusion', '')
    conclusion_row = [
        create_paragraph("Conclusion 结论：", bold=True),
        create_paragraph(conclusion_val, ParagraphStyle('Conclusion', parent=normal_style, fontSize=9, alignment=TA_LEFT))
    ]
    
    conclusion_table = Table([conclusion_row], colWidths=[1.5*inch, 6*inch])
    conclusion_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#e0e0e0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(conclusion_table)
    elements.append(Spacer(1, 20))
    
    # Disclaimer Section
    disclaimer_en = "Note: This review information does not release the factory from any responsibilities in the event of claims being received from our customer."
    disclaimer_zh = "以上不免除我客人收到货后索赔而引起的货物供应商(工厂)的任何责任."
    
    elements.append(create_paragraph(disclaimer_en, ParagraphStyle('Disclaimer', parent=normal_style, fontSize=8, alignment=TA_LEFT)))
    elements.append(Spacer(1, 5))
    elements.append(create_paragraph(disclaimer_zh, ParagraphStyle('Disclaimer', parent=normal_style, fontSize=8, alignment=TA_LEFT)))
    elements.append(Spacer(1, 15))
    
    # Signatures
    grandstep_tech_val = st.session_state.get('grandstep_tech', '')
    factory_rep_val = st.session_state.get('factory_representative', '')
    
    signature_data = [
        [
            create_paragraph("GrandStep Tech:", bold=True),
            create_paragraph(grandstep_tech_val),
            create_paragraph(""),
            create_paragraph("Factory Representative:", bold=True),
            create_paragraph(factory_rep_val)
        ]
    ]
    
    signature_table = Table(signature_data, colWidths=[1.2*inch, 2*inch, 0.5*inch, 1.5*inch, 2*inch])
    signature_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(signature_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Sidebar with enhanced filters
with st.sidebar:
    st.markdown(f'### {ICONS["settings"]} Settings & Filters')
    
    # Language filters with icons
    st.markdown(f'#### {ICONS["language"]} Language Settings')
    ui_language = st.selectbox(
        "User Interface Language",
        ["English", "Mandarin"],
        index=0 if st.session_state.ui_language == "en" else 1,
        key="ui_lang_select"
    )
    st.session_state.ui_language = "en" if ui_language == "English" else "zh"
    
    pdf_language = st.selectbox(
        "PDF Report Language",
        ["English", "Mandarin"],
        index=0 if st.session_state.pdf_language == "en" else 1,
        key="pdf_lang_select"
    )
    st.session_state.pdf_language = "en" if pdf_language == "English" else "zh"
    
    # Location filter with enhanced UI
    st.markdown(f'#### {ICONS["location"]} Location Settings')
    selected_city = st.selectbox(
        "Select Assessment Location",
        list(CHINESE_CITIES.keys()),
        index=list(CHINESE_CITIES.keys()).index(st.session_state.selected_city) 
        if st.session_state.selected_city in CHINESE_CITIES else 0,
        key="city_select"
    )
    st.session_state.selected_city = selected_city
    
    # Display selected location in a badge
    st.markdown(f"""
    <div class="location-badge">
        {ICONS["location"]} {selected_city} ({CHINESE_CITIES[selected_city]})
    </div>
    """, unsafe_allow_html=True)
    
    # Timezone information
    st.markdown(f'#### {ICONS["time"]} Timezone Info')
    china_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(china_tz)
    st.metric(
        "Local Time", 
        current_time.strftime('%H:%M:%S'),
        current_time.strftime('%Y-%m-%d')
    )
    
    # Translation status
    if openai_client:
        st.success(f"{ICONS['success']} Translation API: Active")
    else:
        st.warning(f"{ICONS['warning']} Translation API: Not Configured")
    
    st.markdown("---")
    
    # Sample Types Information
    st.markdown(f'#### {ICONS["info"]} Sample Types')
    for eng, chi in SAMPLE_TYPES.items():
        st.markdown(f'<div class="sample-type-badge">{eng}: {chi}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f'### {ICONS["info"]} Instructions')
    st.info(f"""
    {ICONS["info"]} **Quick Guide:**
    1. {ICONS["basic_info"]} Fill basic information
    2. {ICONS["measure"]} Enter measurement data
    3. {ICONS["conclusion"]} Add conclusion
    4. {ICONS["language"]} Select languages
    5. {ICONS["generate"]} Generate PDF report
    """)

# Title with enhanced styling
st.markdown(f"""
<div class="main-header">
    {ICONS["title"]} Factory Sample Review Report
</div>
""", unsafe_allow_html=True)

# Create tabs for better organization
tab1, tab2, tab3 = st.tabs([
    f"{ICONS['basic_info']} Basic Info",
    f"{ICONS['measurements']} Measurements",
    f"{ICONS['conclusion']} Conclusion"
])

with tab1:
    # Basic Information Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["basic_info"]}</span>
        {get_text("basic_info")}
    </div>
    """, unsafe_allow_html=True)
    
    # Main basic info in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        style_no = st.text_input(
            f"{ICONS['style']} {get_text('style_no')}", 
            placeholder="STYLE-2024-001",
            key="style_no"
        )
        
        factory = st.text_input(
            f"{ICONS['factory']} {get_text('factory')}", 
            placeholder="ABC Manufacturing Co., Ltd.",
            key="factory"
        )
        
        sales = st.text_input(
            f"{ICONS['sales']} {get_text('sales')}", 
            placeholder="Sales Representative",
            key="sales"
        )
    
    with col2:
        size = st.text_input(
            f"{ICONS['measure']} {get_text('size')}", 
            placeholder="US 8, EU 41",
            key="size"
        )
        
        purpose = st.selectbox(
            f"{ICONS['info']} {get_text('purpose')}",
            list(SAMPLE_TYPES.keys()),
            key="purpose"
        )
        
        new_old = st.selectbox(
            f"{ICONS['info']} {get_text('new_old')}",
            ["New", "Old", "Revised"],
            key="new_old"
        )
    
    with col3:
        brand = st.text_input(
            f"{ICONS['brand']} {get_text('brand')}", 
            placeholder="Brand Name",
            key="brand"
        )
        
        last_no = st.text_input(
            f"{ICONS['measure']} {get_text('last_no')}", 
            placeholder="Last #12345",
            key="last_no"
        )
        
        outsole_no = st.text_input(
            f"{ICONS['measure']} {get_text('outsole_no')}", 
            placeholder="OS-2024-001",
            key="outsole_no"
        )
    
    # Review date
    review_date = st.date_input(
        f"{ICONS['time']} {get_text('review_date')}", 
        datetime.now(),
        key="review_date"
    )

with tab2:
    # Measurements Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["measurements"]}</span>
        {get_text("measurements")}
    </div>
    """, unsafe_allow_html=True)
    
    st.info(f"{ICONS['info']} Enter measurement data for each check item. Leave blank if not applicable.")
    
    # Create two columns for left and right measurement items
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown(f"#### {ICONS['measure']} Check Items")
        
        # Check Items
        measurements_left = [
            ("Last Length", "楦长"),
            ("Toe Girth", "趾围"),
            ("Ball Girth", "掌围"),
            ("Waist Girth", "腰围"),
            ("Instep Girth", "背围"),
            ("Vamp length", "鞋口长度"),
            ("Back Height", "后跟高度"),
            ("Boot Height", "靴筒高度"),
            ("Boot top Width", "靴筒宽度"),
            ("Boot Calf Width", "小腿宽度Point 位置点 298"),
            ("Ankle Width", "脚踝宽度 Point 位置点 90mm")
        ]
        
        for item_en, item_zh in measurements_left:
            st.markdown(f"**{item_en} / {item_zh}**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.text_input("First", key=f"{item_en.lower().replace(' ', '_')}_first", label_visibility="collapsed")
            with col2:
                st.text_input("Second", key=f"{item_en.lower().replace(' ', '_')}_second", label_visibility="collapsed")
            with col3:
                st.text_input("Third", key=f"{item_en.lower().replace(' ', '_')}_third", label_visibility="collapsed")
            with col4:
                st.text_input("Fourth", key=f"{item_en.lower().replace(' ', '_')}_fourth", label_visibility="collapsed")
    
    with col_right:
        st.markdown(f"#### {ICONS['measure']} Check Items")
        
        # Check Items
        measurements_right = [
            ("Toe Width", "趾宽"),
            ("Bottom Width", "掌宽"),
            ("Heel Seat Width", "后跟宽度"),
            ("Heel to Instep Girth", "后跟到脚背长度"),
            ("Toe Spring", "鞋头翘度"),
            ("Thickness", "厚度"),
            ("Shank", "钢芯"),
            ("Mid-sole", "中底"),
            ("Outsole Degree", "大底硬度")
        ]
        
        for item_en, item_zh in measurements_right:
            st.markdown(f"**{item_en} / {item_zh}**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.text_input("First", key=f"{item_en.lower().replace(' ', '_')}_first", label_visibility="collapsed")
            with col2:
                st.text_input("Second", key=f"{item_en.lower().replace(' ', '_')}_second", label_visibility="collapsed")
            with col3:
                st.text_input("Third", key=f"{item_en.lower().replace(' ', '_')}_third", label_visibility="collapsed")
            with col4:
                st.text_input("Fourth", key=f"{item_en.lower().replace(' ', '_')}_fourth", label_visibility="collapsed")
        
        # Sock Foam special section
        st.markdown("**Sock Foam / 鞋垫**")
        sock_col1, sock_col2 = st.columns(2)
        with sock_col1:
            st.text_input("After / 后置", key="sock_foam_after")
        with sock_col2:
            st.text_input("Before / 前置", key="sock_foam_before")

with tab3:
    # Conclusion and Signatures Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["conclusion"]}</span>
        {get_text("conclusion")}
    </div>
    """, unsafe_allow_html=True)
    
    conclusion = st.text_area(
        "Conclusion / 结论",
        placeholder="Enter overall conclusion and notes here...",
        height=150,
        key="conclusion"
    )
    
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["signatures"]}</span>
        {get_text("signatures")}
    </div>
    """, unsafe_allow_html=True)
    
    # Signatures
    col1, col2 = st.columns(2)
    
    with col1:
        grandstep_tech = st.text_input(
            f"{ICONS['tech']} {get_text('grandstep_tech')}",
            placeholder="GrandStep Technical Representative",
            key="grandstep_tech"
        )
    
    with col2:
        factory_representative = st.text_input(
            f"{ICONS['factory']} {get_text('factory_representative')}",
            placeholder="Factory Representative Name",
            key="factory_representative"
        )
    
    # Disclaimer
    st.markdown("---")
    st.markdown(f"#### {ICONS['warning']} {get_text('disclaimer')}")
    st.warning(get_text("disclaimer_text"))
    st.info(get_text("disclaimer_text_chinese"))

# Generate PDF Button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button(f"{ICONS['generate']} {get_text('generate_pdf')}", use_container_width=True):
        if not st.session_state.get('style_no') or not st.session_state.get('factory'):
            st.error(f"{ICONS['error']} {get_text('fill_required')}")
        else:
            with st.spinner(f"{ICONS['time']} {get_text('creating_pdf')}"):
                try:
                    pdf_buffer = generate_pdf()
                    st.success(f"{ICONS['success']} {get_text('generate_success')}")
                    
                    # Display PDF preview info
                    with st.expander(f"{ICONS['info']} {get_text('pdf_details')}"):
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.metric(get_text("location"), f"{selected_city} ({CHINESE_CITIES[selected_city]})")
                            st.metric(get_text("report_language"), "Mandarin" if st.session_state.pdf_language == "zh" else "English")
                        with col_info2:
                            china_tz = pytz.timezone('Asia/Shanghai')
                            current_time = datetime.now(china_tz)
                            st.metric(get_text("generated"), current_time.strftime('%H:%M:%S'))
                    
                    # Download button
                    filename = f"Sample_Review_{st.session_state.get('style_no', '')}_{selected_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    st.download_button(
                        label=f"{ICONS['download']} {get_text('download_pdf')}",
                        data=pdf_buffer,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"{ICONS['error']} {get_text('error_generating')}: {str(e)}")

# Footer
st.markdown("---")
st.markdown(f"""
<div class="footer">
    <p style='font-size: 1.2rem; font-weight: 600; color: #667eea; margin-bottom: 0.5rem;'>
        {ICONS['title']} {get_text('footer_text')}
    </p>
    <p style='font-size: 0.9rem; color: #666666;'>
        {ICONS['location']} {get_text('location')}: {selected_city} ({CHINESE_CITIES[selected_city]}) | 
        {ICONS['language']} {get_text('report_language')}: {'Mandarin' if st.session_state.pdf_language == 'zh' else 'English'}
    </p>
    <p style='font-size: 0.8rem; color: #999999; margin-top: 1rem;'>
        {get_text('powered_by')} | {get_text('copyright')}
    </p>
</div>
""", unsafe_allow_html=True)

# Create .env file instructions in sidebar
with st.sidebar:
    with st.expander(f"{ICONS['info']} API Setup"):
        st.code("""
# Create .env file in your project folder
OPENAI_API_KEY=your-api-key-here
""")
        st.info("Restart the app after adding your API key to enable translations.")
