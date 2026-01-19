import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics PDF Preview Features
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
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

# Sample types - separate for English and Chinese
SAMPLE_TYPES_EN = {
    "Dev.sample": "Development Sample",
    "Cfm sample": "Confirmation Sample",
    "Fit sample": "Fitting Sample",
    "Size set": "Size Set Sample",
    "TOP sample": "Production Sample",
    "Shipment sample": "Shipment Sample"
}

SAMPLE_TYPES_ZH = {
    "Dev.sample": "开发样",
    "Cfm sample": "确认样",
    "Fit sample": "试穿样",
    "Size set": "尺码套样",
    "TOP sample": "大货样",
    "Shipment sample": "船样"
}

# Color scheme for the PDF
COLORS = {
    "primary": "#667eea",  # Purple
    "secondary": "#764ba2",  # Dark purple
    "accent": "#f093fb",  # Light purple
    "success": "#4CAF50",  # Green
    "warning": "#FF9800",  # Orange
    "danger": "#f44336",  # Red
    "light": "#f8f9fa",  # Light gray
    "dark": "#343a40",  # Dark gray
    "info": "#17a2b8",  # Teal
    "table_header": "#4a5568",  # Gray blue
    "table_row_even": "#ffffff",  # White
    "table_row_odd": "#f7fafc",  # Very light blue
    "border": "#e2e8f0",  # Light border
    "highlight": "#fffacd"  # Light yellow for highlights
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
    .pdf-preview {
        border: 2px solid #667eea;
        border-radius: 10px;
        padding: 1rem;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        margin: 1rem 0;
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
        # Titles and Headers
        "title": "Factory Sample Review Report",
        "basic_info": "Basic Information",
        "measurements": "Sample Measurements",
        "sample_review": "Sample Review",
        "conclusion": "Conclusion",
        "signatures": "Signatures",
        
        # Buttons
        "generate_pdf": "Generate PDF Report",
        "download_pdf": "Download PDF Report",
        
        # Form Fields
        "style_no": "Style No.",
        "size": "Size",
        "factory": "Factory",
        "purpose": "Purpose",
        "brand": "Brand",
        "last_no": "Last No.",
        "sales": "Sales",
        "new_old": "New/Old",
        "outsole_no": "Outsole NO.",
        "review_date": "Review Date",
        "check_items": "Check Items",
        "first": "First",
        "second": "Second",
        "third": "Third",
        "fourth": "Fourth",
        "measurement_details": "Measurement Details",
        "picture": "Picture",
        
        # Footer and Messages
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
        "measurement_check": "Measurement Check Items",
        "add_measurement": "Add Measurement Point",
        "grandstep_tech": "GrandStep Tech",
        "factory_representative": "Factory Representative",
        "sample_id": "Sample ID",
        "technical_review": "Technical Review",
        "quality_assessment": "Quality Assessment"
    }
    
    text = texts.get(key, fallback or key)
    
    # Translate if needed
    if lang == "zh" and openai_client:
        return translate_text(text, "zh")
    return text

# PDF text based on selected language
def get_pdf_text(key, pdf_lang):
    """Get text for PDF based on selected language"""
    # English texts for PDF
    pdf_texts_en = {
        "title": "Factory Sample Review Report",
        "page_num": "Page# 1",
        "style_no": "Style No.",
        "size": "Size",
        "factory": "Factory",
        "purpose": "Purpose",
        "brand": "Brand",
        "last_no": "Last No.",
        "sales": "Sales",
        "new_old": "New/Old",
        "outsole_no": "Outsole NO.",
        "review": "Review Date",
        "check_items": "Check Items",
        "first": "First",
        "second": "Second",
        "third": "Third",
        "fourth": "Fourth",
        "conclusion": "Conclusion",
        "disclaimer": "Note: This review information does not release the factory from any responsibilities in the event of claims being received from our customer.",
        "grandstep_tech": "GrandStep Tech",
        "factory_rep": "Factory Representative",
        "after": "After",
        "before": "Before",
        "location": "Location",
        "header": "FACTORY SAMPLE REVIEW REPORT",
        "sample_id": "Sample ID",
        "technical_review": "Technical Review",
        "quality_assessment": "Quality Assessment",
        "measurement_data": "Measurement Data",
        "signature_section": "Authorization & Signatures",
        "status": "Status",
        "remarks": "Remarks",
        "reviewed_by": "Reviewed By",
        "approved_by": "Approved By",
        "date": "Date"
    }
    
    # Chinese texts for PDF
    pdf_texts_zh = {
        "title": "样品技术核查表",
        "page_num": "页码# 1",
        "style_no": "型体",
        "size": "码数",
        "factory": "工厂",
        "purpose": "类型",
        "brand": "品牌",
        "last_no": "楦号",
        "sales": "业务",
        "new_old": "新旧",
        "outsole_no": "大底",
        "review": "审核日期",
        "check_items": "核查项目",
        "first": "第一次",
        "second": "第二次",
        "third": "第三次",
        "fourth": "第四次",
        "conclusion": "结论",
        "disclaimer": "以上不免除我客人收到货后索赔而引起的货物供应商(工厂)的任何责任.",
        "grandstep_tech": "GrandStep技术代表",
        "factory_rep": "工厂代表",
        "after": "后置",
        "before": "前置",
        "location": "地点",
        "header": "样品技术核查报告",
        "sample_id": "样品编号",
        "technical_review": "技术审核",
        "quality_assessment": "质量评估",
        "measurement_data": "测量数据",
        "signature_section": "授权与签名",
        "status": "状态",
        "remarks": "备注",
        "reviewed_by": "审核人",
        "approved_by": "批准人",
        "date": "日期"
    }
    
    if pdf_lang == "en":
        return pdf_texts_en.get(key, key)
    else:
        return pdf_texts_zh.get(key, key)

# Measurement items in both languages
MEASUREMENT_ITEMS_EN = {
    "left": [
        ("Last Length", "Last Length"),
        ("Toe Girth", "Toe Girth"),
        ("Ball Girth", "Ball Girth"),
        ("Waist Girth", "Waist Girth"),
        ("Instep Girth", "Instep Girth"),
        ("Vamp length", "Vamp length"),
        ("Back Height", "Back Height"),
        ("Boot Height", "Boot Height"),
        ("Boot top Width", "Boot top Width"),
        ("Boot Calf Width", "Boot Calf Width"),
        ("Ankle Width", "Ankle Width")
    ],
    "right": [
        ("Toe Width", "Toe Width"),
        ("Bottom Width", "Bottom Width"),
        ("Heel Seat Width", "Heel Seat Width"),
        ("Heel to Instep Girth", "Heel to Instep Girth"),
        ("Toe Spring", "Toe Spring"),
        ("Thickness", "Thickness"),
        ("Shank", "Shank"),
        ("Mid-sole", "Mid-sole"),
        ("Outsole Degree", "Outsole Degree"),
        ("Sock Foam", "Sock Foam")
    ]
}

MEASUREMENT_ITEMS_ZH = {
    "left": [
        ("楦长", "楦长"),
        ("趾围", "趾围"),
        ("掌围", "掌围"),
        ("腰围", "腰围"),
        ("背围", "背围"),
        ("鞋口长度", "鞋口长度"),
        ("后跟高度", "后跟高度"),
        ("靴筒高度", "靴筒高度"),
        ("靴筒宽度", "靴筒宽度"),
        ("小腿宽度", "小腿宽度"),
        ("脚踝宽度", "脚踝宽度")
    ],
    "right": [
        ("趾宽", "趾宽"),
        ("掌宽", "掌宽"),
        ("后跟宽度", "后跟宽度"),
        ("后跟到脚背长度", "后跟到脚背长度"),
        ("鞋头翘度", "鞋头翘度"),
        ("厚度", "厚度"),
        ("钢芯", "钢芯"),
        ("中底", "中底"),
        ("大底硬度", "大底硬度"),
        ("鞋垫", "鞋垫")
    ]
}

# PDF Generation with Enhanced Headers and Footers
class EnhancedSampleReviewPDF(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        self.header_text = kwargs.pop('header_text', '')
        self.location = kwargs.pop('location', '')
        self.pdf_language = kwargs.pop('pdf_language', 'en')
        self.selected_city = kwargs.pop('selected_city', '')
        self.chinese_city = kwargs.pop('chinese_city', '')
        self.chinese_font = kwargs.pop('chinese_font', 'Helvetica')
        self.style_no = kwargs.pop('style_no', '')
        super().__init__(*args, **kwargs)
        
    def afterFlowable(self, flowable):
        """Add header and footer with enhanced design"""
        # Add header on all pages
        self.canv.saveState()
        
        # Draw header background with gradient effect
        header_height = 0.7*inch
        self.canv.setFillColor(colors.HexColor(COLORS['primary']))
        self.canv.rect(0, self.pagesize[1] - header_height, self.pagesize[0], header_height, fill=1, stroke=0)
        
        # Add subtle pattern to header
        self.canv.setFillColor(colors.HexColor('#ffffff'))
        self.canv.setFillAlpha(0.1)
        for i in range(0, int(self.pagesize[0]), 10):
            self.canv.circle(i, self.pagesize[1] - header_height/2, 2, fill=1, stroke=0)
        self.canv.setFillAlpha(1)
        
        # Use appropriate font
        font_size = 14
        if self.pdf_language == "zh":
            self.canv.setFont(self.chinese_font, font_size)
        else:
            self.canv.setFont('Helvetica-Bold', font_size)
            
        self.canv.setFillColor(colors.white)
        header_title = get_pdf_text("header", self.pdf_language)
        self.canv.drawCentredString(
            self.pagesize[0]/2.0, 
            self.pagesize[1] - 0.45*inch, 
            header_title
        )
        
        # Add sub-header with style number
        if self.style_no:
            self.canv.setFont('Helvetica', 9)
            self.canv.setFillColor(colors.HexColor('#e2e8f0'))
            style_text = f"{get_pdf_text('sample_id', self.pdf_language)}: {self.style_no}"
            self.canv.drawCentredString(
                self.pagesize[0]/2.0, 
                self.pagesize[1] - 0.65*inch, 
                style_text
            )
        
        self.canv.restoreState()
            
        # Footer on all pages
        self.canv.saveState()
        
        # Footer background with gradient
        footer_height = 0.6*inch
        self.canv.setFillColor(colors.HexColor(COLORS['light']))
        self.canv.rect(0, 0, self.pagesize[0], footer_height, fill=1, stroke=0)
        
        # Top border with accent color
        self.canv.setStrokeColor(colors.HexColor(COLORS['accent']))
        self.canv.setLineWidth(2)
        self.canv.line(0.5*inch, footer_height, self.pagesize[0] - 0.5*inch, footer_height)
        
        # Footer text
        font_size = 8
        if self.pdf_language == "zh":
            self.canv.setFont(self.chinese_font, font_size)
        else:
            self.canv.setFont('Helvetica', font_size)
            
        self.canv.setFillColor(colors.HexColor(COLORS['dark']))
        
        # Left: Location with icon
        china_tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.now(china_tz)
        
        location_info = f"📍 {get_pdf_text('location', self.pdf_language)}: {self.selected_city}"
        if self.pdf_language == "zh" and self.chinese_city:
            location_info = f"📍 {get_pdf_text('location', self.pdf_language)}: {self.selected_city} ({self.chinese_city})"
        
        self.canv.drawString(0.5*inch, 0.3*inch, location_info)
        
        # Center: Timestamp with formatted box
        self.canv.setFillColor(colors.HexColor(COLORS['primary']))
        self.canv.setFont('Helvetica-Bold', 8)
        if self.pdf_language == "zh":
            timestamp = f"📅 生成: {current_time.strftime('%Y-%m-%d %H:%M')}"
        else:
            timestamp = f"📅 Generated: {current_time.strftime('%Y-%m-%d %H:%M')}"
        self.canv.drawCentredString(self.pagesize[0]/2.0, 0.3*inch, timestamp)
        
        # Right: Page number with decorative background
        self.canv.setFillColor(colors.HexColor(COLORS['secondary']))
        page_num_width = 0.6*inch
        page_num_x = self.pagesize[0] - 0.5*inch - page_num_width
        self.canv.rect(page_num_x, 0.15*inch, page_num_width, 0.3*inch, fill=1, stroke=0)
        
        self.canv.setFillColor(colors.white)
        self.canv.setFont('Helvetica-Bold', 9)
        if self.pdf_language == "zh":
            page_num = f"第 {self.page} 页"
        else:
            page_num = f"Page {self.page}"
        self.canv.drawCentredString(self.pagesize[0] - 0.8*inch, 0.3*inch, page_num)
        
        self.canv.restoreState()

def generate_pdf():
    """Generate enhanced Sample Review PDF report with colors"""
    buffer = io.BytesIO()
    
    # Get location info
    selected_city = st.session_state.selected_city
    chinese_city = CHINESE_CITIES[selected_city]
    pdf_lang = st.session_state.pdf_language
    
    # Register Chinese font if needed
    chinese_font = 'Helvetica'
    
    if pdf_lang == "zh":
        try:
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            chinese_font = 'STSong-Light'
        except:
            chinese_font = 'Helvetica'
    
    # Create enhanced PDF
    doc = EnhancedSampleReviewPDF(
        buffer, 
        pagesize=A4,  # Use A4 for more professional look
        topMargin=1.0*inch,
        bottomMargin=0.8*inch,
        header_text=get_pdf_text("header", pdf_lang),
        location=selected_city,
        pdf_language=pdf_lang,
        selected_city=selected_city,
        chinese_city=chinese_city,
        chinese_font=chinese_font,
        style_no=st.session_state.get('style_no', '')
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Create enhanced styles based on language
    title_font = 'Helvetica-Bold' if pdf_lang != "zh" else chinese_font
    normal_font = 'Helvetica' if pdf_lang != "zh" else chinese_font
    bold_font = 'Helvetica-Bold' if pdf_lang != "zh" else chinese_font
    
    # Title style with gradient effect
    title_style = ParagraphStyle(
        'EnhancedTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor(COLORS['primary']),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName=bold_font
    )
    
    # Subtitle style
    subtitle_style = ParagraphStyle(
        'EnhancedSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor(COLORS['secondary']),
        alignment=TA_CENTER,
        spaceAfter=25,
        fontName=bold_font
    )
    
    # Section header style
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor(COLORS['dark']),
        spaceBefore=20,
        spaceAfter=10,
        fontName=bold_font,
        backColor=colors.HexColor(COLORS['light']),
        borderPadding=(6, 6, 6, 6),
        borderColor=colors.HexColor(COLORS['border']),
        borderWidth=1
    )
    
    # Table header style
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        alignment=TA_CENTER,
        fontName=bold_font
    )
    
    # Table cell style
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        fontName=normal_font
    )
    
    # Highlight cell style
    highlight_cell_style = ParagraphStyle(
        'HighlightCell',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        fontName=bold_font,
        textColor=colors.HexColor(COLORS['primary'])
    )
    
    # Normal style with better spacing
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        fontName=normal_font
    )
    
    # Helper function for creating paragraphs
    def create_paragraph(text, style=normal_style, bold=False, color=None):
        """Create paragraph with appropriate font and color"""
        if bold:
            font_name = bold_font
        else:
            font_name = normal_font
        
        custom_style = ParagraphStyle(
            f"CustomStyle_{bold}_{color}",
            parent=style,
            fontName=font_name
        )
        
        if color:
            custom_style.textColor = colors.HexColor(color)
        
        return Paragraph(text, custom_style)
    
    # Build the PDF content with enhanced design
    elements.append(Spacer(1, 20))
    
    # Title with colored background
    title_bg = Drawing(500, 60)
    title_bg.add(Rect(0, 0, 500, 60, fillColor=colors.HexColor(COLORS['light']), strokeColor=colors.HexColor(COLORS['primary']), strokeWidth=2))
    # elements.append(title_bg)
    
    elements.append(Paragraph(get_pdf_text("title", pdf_lang), title_style))
    elements.append(Paragraph(get_pdf_text("technical_review", pdf_lang), subtitle_style))
    
    # Add decorative line
    elements.append(Spacer(1, 5))
    # elements.append(Drawing(500, 1))
    elements.append(Spacer(1, 15))
    
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
    
    # Get appropriate sample type based on language
    if pdf_lang == "zh":
        purpose_display = SAMPLE_TYPES_ZH.get(purpose_val, purpose_val)
    else:
        purpose_display = SAMPLE_TYPES_EN.get(purpose_val, purpose_val)
    
    # Basic Information Table with enhanced styling
    elements.append(Paragraph(get_pdf_text("sample_id", pdf_lang), section_header_style))
    
    basic_data = [
        [
            create_paragraph(get_pdf_text("style_no", pdf_lang), bold=True, color=COLORS['primary']), 
            create_paragraph(style_no_val, style=highlight_cell_style),
            create_paragraph(get_pdf_text("factory", pdf_lang), bold=True, color=COLORS['primary']),
            create_paragraph(factory_val)
        ],
        [
            create_paragraph(get_pdf_text("brand", pdf_lang), bold=True, color=COLORS['primary']), 
            create_paragraph(brand_val),
            create_paragraph(get_pdf_text("size", pdf_lang), bold=True, color=COLORS['primary']),
            create_paragraph(size_val)
        ],
        [
            create_paragraph(get_pdf_text("purpose", pdf_lang), bold=True, color=COLORS['primary']), 
            create_paragraph(purpose_display),
            create_paragraph(get_pdf_text("last_no", pdf_lang), bold=True, color=COLORS['primary']),
            create_paragraph(last_no_val)
        ],
        [
            create_paragraph(get_pdf_text("sales", pdf_lang), bold=True, color=COLORS['primary']), 
            create_paragraph(sales_val),
            create_paragraph(get_pdf_text("outsole_no", pdf_lang), bold=True, color=COLORS['primary']),
            create_paragraph(outsole_no_val)
        ],
        [
            create_paragraph(get_pdf_text("new_old", pdf_lang), bold=True, color=COLORS['primary']), 
            create_paragraph(new_old_val),
            create_paragraph(get_pdf_text("review", pdf_lang), bold=True, color=COLORS['primary']),
            create_paragraph(review_date_val.strftime('%Y-%m-%d') if hasattr(review_date_val, 'strftime') else str(review_date_val))
        ]
    ]
    
    basic_table = Table(basic_data, colWidths=[1.5*inch, 2.0*inch, 1.5*inch, 2.0*inch])
    basic_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(COLORS['border'])),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor(COLORS['light'])),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor(COLORS['light'])),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor(COLORS['table_row_odd'])]),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor(COLORS['primary'])),
    ]))
    elements.append(basic_table)
    elements.append(Spacer(1, 25))
    
    # Measurement Check Table with enhanced design
    elements.append(Paragraph(get_pdf_text("measurement_data", pdf_lang), section_header_style))
    
    if pdf_lang == "zh":
        check_items = MEASUREMENT_ITEMS_ZH
    else:
        check_items = MEASUREMENT_ITEMS_EN
    
    # Create two columns for measurements
    left_items = check_items["left"]
    right_items = check_items["right"]
    
    # Header for measurement table
    measurement_header = [
        create_paragraph(get_pdf_text("check_items", pdf_lang), style=table_header_style),
        create_paragraph(get_pdf_text("first", pdf_lang), style=table_header_style),
        create_paragraph(get_pdf_text("second", pdf_lang), style=table_header_style),
        create_paragraph(get_pdf_text("third", pdf_lang), style=table_header_style),
        create_paragraph(get_pdf_text("fourth", pdf_lang), style=table_header_style),
        "",  # Spacer column
        create_paragraph(get_pdf_text("check_items", pdf_lang), style=table_header_style),
        create_paragraph(get_pdf_text("first", pdf_lang), style=table_header_style),
        create_paragraph(get_pdf_text("second", pdf_lang), style=table_header_style),
        create_paragraph(get_pdf_text("third", pdf_lang), style=table_header_style),
        create_paragraph(get_pdf_text("fourth", pdf_lang), style=table_header_style)
    ]
    
    measurement_data = [measurement_header]
    
    # Get maximum length for iteration
    max_items = max(len(left_items), len(right_items))
    
    for i in range(max_items):
        row = []
        
        # Left side items
        if i < len(left_items):
            item_name, item_key = left_items[i]
            # Get measurement values from session state
            if pdf_lang == "zh":
                eng_item = MEASUREMENT_ITEMS_EN["left"][i][1] if i < len(MEASUREMENT_ITEMS_EN["left"]) else ""
            else:
                eng_item = item_key
            
            if eng_item:
                first_val = st.session_state.get(f'{eng_item.lower().replace(" ", "_")}_first', '')
                second_val = st.session_state.get(f'{eng_item.lower().replace(" ", "_")}_second', '')
                third_val = st.session_state.get(f'{eng_item.lower().replace(" ", "_")}_third', '')
                fourth_val = st.session_state.get(f'{eng_item.lower().replace(" ", "_")}_fourth', '')
            else:
                first_val = second_val = third_val = fourth_val = ''
            
            row.extend([
                create_paragraph(item_name, bold=True, color=COLORS['dark']),
                create_paragraph(first_val),
                create_paragraph(second_val),
                create_paragraph(third_val),
                create_paragraph(fourth_val)
            ])
        else:
            # Empty cells for left side
            row.extend([create_paragraph("")] * 5)
        
        # Add spacer column
        row.append(create_paragraph(""))
        
        # Right side items
        if i < len(right_items):
            item_name, item_key = right_items[i]
            # Get measurement values from session state
            if pdf_lang == "zh":
                eng_item = MEASUREMENT_ITEMS_EN["right"][i][1] if i < len(MEASUREMENT_ITEMS_EN["right"]) else ""
            else:
                eng_item = item_key
            
            if eng_item:
                first_val = st.session_state.get(f'{eng_item.lower().replace(" ", "_")}_first', '')
                second_val = st.session_state.get(f'{eng_item.lower().replace(" ", "_")}_second', '')
                third_val = st.session_state.get(f'{eng_item.lower().replace(" ", "_")}_third', '')
                fourth_val = st.session_state.get(f'{eng_item.lower().replace(" ", "_")}_fourth', '')
            else:
                first_val = second_val = third_val = fourth_val = ''
            
            row.extend([
                create_paragraph(item_name, bold=True, color=COLORS['dark']),
                create_paragraph(first_val),
                create_paragraph(second_val),
                create_paragraph(third_val),
                create_paragraph(fourth_val)
            ])
        else:
            # Empty cells for right side
            row.extend([create_paragraph("")] * 5)
        
        measurement_data.append(row)
    
    # Create the measurement table with enhanced styling
    measurement_table = Table(measurement_data, colWidths=[1.3*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.2*inch, 1.3*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch])
    measurement_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(COLORS['border'])),
        ('BACKGROUND', (0, 0), (4, 0), colors.HexColor(COLORS['table_header'])),
        ('BACKGROUND', (6, 0), (10, 0), colors.HexColor(COLORS['table_header'])),
        ('TEXTCOLOR', (0, 0), (4, 0), colors.white),
        ('TEXTCOLOR', (6, 0), (10, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor(COLORS['table_row_even']), colors.HexColor(COLORS['table_row_odd'])]),
        ('BOX', (0, 0), (4, -1), 1, colors.HexColor(COLORS['primary'])),
        ('BOX', (6, 0), (10, -1), 1, colors.HexColor(COLORS['primary'])),
    ]))
    elements.append(measurement_table)
    elements.append(Spacer(1, 20))
    
    # Sock Foam special section with colored box
    if pdf_lang == "zh":
        sock_foam_label = "鞋垫"
    else:
        sock_foam_label = "Sock Foam"
    
    sock_foam_after = st.session_state.get('sock_foam_after', '')
    sock_foam_before = st.session_state.get('sock_foam_before', '')
    
    sock_data = [
        [
            create_paragraph(sock_foam_label, bold=True, color=COLORS['primary']),
            create_paragraph(get_pdf_text("after", pdf_lang), bold=True),
            create_paragraph(sock_foam_after, style=highlight_cell_style),
            create_paragraph(get_pdf_text("before", pdf_lang), bold=True),
            create_paragraph(sock_foam_before, style=highlight_cell_style)
        ]
    ]
    
    sock_table = Table(sock_data, colWidths=[1.5*inch, 1.0*inch, 1.2*inch, 1.0*inch, 1.2*inch])
    sock_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(COLORS['border'])),
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(COLORS['light'])),
        ('BACKGROUND', (2, 0), (2, 0), colors.HexColor(COLORS['highlight'])),
        ('BACKGROUND', (4, 0), (4, 0), colors.HexColor(COLORS['highlight'])),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor(COLORS['accent'])),
    ]))
    elements.append(sock_table)
    elements.append(Spacer(1, 25))
    
    # Conclusion Section with colored background
    elements.append(Paragraph(get_pdf_text("quality_assessment", pdf_lang), section_header_style))
    
    conclusion_val = st.session_state.get('conclusion', '')
    conclusion_label = f"{get_pdf_text('conclusion', pdf_lang)}:"
    conclusion_row = [
        create_paragraph(conclusion_label, bold=True, color=COLORS['primary']),
        create_paragraph(conclusion_val, ParagraphStyle('Conclusion', parent=normal_style, fontSize=10, alignment=TA_LEFT, textColor=colors.HexColor(COLORS['dark']), backColor=colors.HexColor(COLORS['light']), borderPadding=8))
    ]
    
    conclusion_table = Table([conclusion_row], colWidths=[1.5*inch, 5.5*inch])
    conclusion_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(COLORS['border'])),
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(COLORS['light'])),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#ffffff')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor(COLORS['primary'])),
    ]))
    elements.append(conclusion_table)
    elements.append(Spacer(1, 25))
    
    # Disclaimer Section with warning style
    disclaimer_style = ParagraphStyle(
        'DisclaimerStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor(COLORS['warning']),
        alignment=TA_LEFT,
        fontName=bold_font,
        backColor=colors.HexColor('#fff3cd'),
        borderColor=colors.HexColor('#ffeaa7'),
        borderWidth=1,
        borderPadding=8,
        leading=13
    )
    
    elements.append(create_paragraph("⚠️ " + get_pdf_text("disclaimer", pdf_lang), style=disclaimer_style))
    elements.append(Spacer(1, 25))
    
    # Signatures Section with enhanced design
    elements.append(Paragraph(get_pdf_text("signature_section", pdf_lang), section_header_style))
    
    grandstep_tech_val = st.session_state.get('grandstep_tech', '')
    factory_rep_val = st.session_state.get('factory_representative', '')
    review_date_str = review_date_val.strftime('%Y-%m-%d') if hasattr(review_date_val, 'strftime') else str(review_date_val)
    
    # Create signature table with colored sections
    signature_header = [
        create_paragraph(get_pdf_text("reviewed_by", pdf_lang), bold=True, color=COLORS['primary']),
        create_paragraph(get_pdf_text("approved_by", pdf_lang), bold=True, color=COLORS['primary']),
        create_paragraph(get_pdf_text("date", pdf_lang), bold=True, color=COLORS['primary'])
    ]
    
    signature_data = [
        signature_header,
        [
            create_paragraph(grandstep_tech_val),
            create_paragraph(factory_rep_val),
            create_paragraph(review_date_str, style=highlight_cell_style)
        ]
    ]
    
    # Add signature lines
    signature_lines = [
        ["___________________", "___________________", "___________________"]
    ]
    
    signature_table_data = signature_data + signature_lines
    
    signature_table = Table(signature_table_data, colWidths=[2.5*inch, 2.5*inch, 1.5*inch])
    signature_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0, colors.white),  # No grid lines
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['light'])),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 1), (-1, 1), 1, colors.HexColor(COLORS['dark'])),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor(COLORS['primary'])),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(signature_table)
    elements.append(Spacer(1, 20))
    
    # Add status section
    status_style = ParagraphStyle(
        'StatusStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor(COLORS['dark']),
        alignment=TA_CENTER,
        fontName=normal_font,
        borderPadding=6
    )
    
    status_text = "✓ " + ("审核完成 | Review Completed" if pdf_lang == "zh" else "Review Completed | 审核完成")
    elements.append(create_paragraph(status_text, style=status_style, bold=True, color=COLORS['success']))
    
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
    if ui_language == "English":
        for eng, desc in SAMPLE_TYPES_EN.items():
            st.markdown(f'<div class="sample-type-badge">{eng}: {desc}</div>', unsafe_allow_html=True)
    else:
        for eng, chi in SAMPLE_TYPES_ZH.items():
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

# PDF Preview Section


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
            list(SAMPLE_TYPES_EN.keys()),
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
        st.markdown(f"#### {ICONS['measure']} Check Items (Left Side)")
        
        # Show English measurements in UI regardless of language
        measurements_left = MEASUREMENT_ITEMS_EN["left"]
        
        for item_en, item_key in measurements_left:
            st.markdown(f"**{item_en}**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.text_input("First", key=f"{item_key.lower().replace(' ', '_')}_first", label_visibility="collapsed")
            with col2:
                st.text_input("Second", key=f"{item_key.lower().replace(' ', '_')}_second", label_visibility="collapsed")
            with col3:
                st.text_input("Third", key=f"{item_key.lower().replace(' ', '_')}_third", label_visibility="collapsed")
            with col4:
                st.text_input("Fourth", key=f"{item_key.lower().replace(' ', '_')}_fourth", label_visibility="collapsed")
    
    with col_right:
        st.markdown(f"#### {ICONS['measure']} Check Items (Right Side)")
        
        # Show English measurements in UI regardless of language
        measurements_right = MEASUREMENT_ITEMS_EN["right"]
        
        for i, (item_en, item_key) in enumerate(measurements_right):
            if item_en == "Sock Foam":
                # Special handling for Sock Foam
                st.markdown("**Sock Foam**")
                sock_col1, sock_col2 = st.columns(2)
                with sock_col1:
                    st.text_input("After", key="sock_foam_after", label_visibility="collapsed")
                with sock_col2:
                    st.text_input("Before", key="sock_foam_before", label_visibility="collapsed")
            else:
                st.markdown(f"**{item_en}**")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.text_input("First", key=f"{item_key.lower().replace(' ', '_')}_first", label_visibility="collapsed")
                with col2:
                    st.text_input("Second", key=f"{item_key.lower().replace(' ', '_')}_second", label_visibility="collapsed")
                with col3:
                    st.text_input("Third", key=f"{item_key.lower().replace(' ', '_')}_third", label_visibility="collapsed")
                with col4:
                    st.text_input("Fourth", key=f"{item_key.lower().replace(' ', '_')}_fourth", label_visibility="collapsed")

with tab3:
    # Conclusion and Signatures Section
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["conclusion"]}</span>
        {get_text("conclusion")}
    </div>
    """, unsafe_allow_html=True)
    
    conclusion = st.text_area(
        "Conclusion",
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
                    
                    # Display PDF preview info with enhanced design
                    with st.expander(f"{ICONS['info']} 📊 {get_text('pdf_details')}", expanded=True):
                        col_info1, col_info2, col_info3 = st.columns(3)
                        with col_info1:
                            st.metric(
                                "📍 " + get_text("location"), 
                                f"{selected_city}",
                                CHINESE_CITIES[selected_city]
                            )
                        with col_info2:
                            st.metric(
                                "🌐 " + get_text("report_language"), 
                                "Mandarin" if st.session_state.pdf_language == "zh" else "English"
                            )
                        with col_info3:
                            china_tz = pytz.timezone('Asia/Shanghai')
                            current_time = datetime.now(china_tz)
                            st.metric(
                                "🕐 " + get_text("generated"), 
                                current_time.strftime('%H:%M'),
                                current_time.strftime('%Y-%m-%d')
                            )
                        
                        # PDF features preview
                        st.markdown("""
                        <div style='background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                                    padding: 1rem; border-radius: 10px; margin-top: 1rem;'>
                            <h4 style='color: #667eea; text-align: center;'>🎨 PDF Features Included:</h4>
                            <div style='display: flex; justify-content: space-between; margin-top: 0.5rem;'>
                                <span style='color: #4CAF50;'>✓ Color-coded sections</span>
                                <span style='color: #2196F3;'>✓ Professional headers</span>
                                <span style='color: #9C27B0;'>✓ Enhanced tables</span>
                                <span style='color: #FF9800;'>✓ Signature boxes</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Download button with enhanced styling
                    filename = f"Sample_Review_{st.session_state.get('style_no', '')}_{selected_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    
                    # Convert PDF to base64 for preview
                    pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode()
                    
                    col_download1, col_download2 = st.columns([3, 1])
                    with col_download1:
                        st.download_button(
                            label=f"{ICONS['download']} 📥 {get_text('download_pdf')}",
                            data=pdf_buffer,
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                    
                    with col_download2:
                        # PDF preview button
                        if st.button(f"{ICONS['info']} Preview", use_container_width=True):
                            pdf_display = f"""
                            <iframe src="data:application/pdf;base64,{pdf_base64}" 
                                    width="100%" height="600px" 
                                    style="border: 2px solid #667eea; border-radius: 10px;">
                            </iframe>
                            """
                            st.markdown(pdf_display, unsafe_allow_html=True)
                    
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
