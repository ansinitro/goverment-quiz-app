import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import HexColor

# Register fonts that support Cyrillic
try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
    font_name = 'DejaVuSans'
    font_bold = 'DejaVuSans-Bold'
except:
    print("Warning: DejaVuSans fonts not found. Using default fonts")
    font_name = 'Helvetica'
    font_bold = 'Helvetica-Bold'

def sanitize_text(text):
    """Sanitize text for ReportLab PDF generation"""
    if not text:
        return text
    text = text.replace('<br>', '<br/>')
    text = text.replace('<BR>', '<br/>')
    text = text.replace('<br >', '<br/>')
    text = text.replace('&', '&amp;')
    return text

def create_answers_pdf(json_file, output_pdf):
    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Group and deduplicate questions by theme
    themes = {}
    seen_questions = {}  # Track unique questions by text
    
    for q in questions:
        theme_id = q['theme_id']
        question_text = q['question'].strip()
        
        # Initialize theme if not exists
        if theme_id not in themes:
            themes[theme_id] = {
                'name': q['theme_name'],
                'questions': {}
            }
        
        # Check if this exact question already exists in this theme
        if question_text not in themes[theme_id]['questions']:
            # New unique question
            themes[theme_id]['questions'][question_text] = {
                'question': q['question'],
                'correct_answers': [q['correct_answer_text']],
                'article': q.get('article', ''),
                'question_number': q.get('question_number', 0)
            }
        else:
            # Question exists, add the correct answer if it's different
            existing = themes[theme_id]['questions'][question_text]
            if q['correct_answer_text'] not in existing['correct_answers']:
                existing['correct_answers'].append(q['correct_answer_text'])
    
    # Create PDF
    doc = SimpleDocTemplate(output_pdf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    
    # Define styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_bold,
        fontSize=16,
        spaceAfter=12,
        alignment=TA_LEFT
    )
    
    theme_style = ParagraphStyle(
        'ThemeTitle',
        parent=styles['Heading2'],
        fontName=font_bold,
        fontSize=14,
        spaceAfter=10,
        spaceBefore=10,
        alignment=TA_LEFT,
        textColor=HexColor('#1e40af')
    )
    
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=11,
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    answer_style = ParagraphStyle(
        'Answer',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=10,
        spaceAfter=4,
        leftIndent=20,
        textColor=HexColor('#16a34a'),
        alignment=TA_LEFT
    )
    
    article_style = ParagraphStyle(
        'Article',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        spaceAfter=15,
        leftIndent=20,
        textColor=HexColor('#6b7280'),
        alignment=TA_LEFT
    )
    
    # Build PDF content
    story = []
    
    # Add title
    story.append(Paragraph("Ответы на вопросы экзамена", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    question_counter = 1
    
    # Add questions grouped by theme
    for theme_id in sorted(themes.keys(), key=lambda x: int(x)):
        question_counter = 1
        theme_data = themes[theme_id]
        
        # Add theme title
        story.append(Paragraph(f"<b>Тема {theme_id}: {theme_data['name']}</b>", theme_style))
        story.append(Spacer(1, 0.3*cm))
        
        # Sort questions by original question number if available
        sorted_questions = sorted(
            theme_data['questions'].items(),
            key=lambda x: x[1]['question_number']
        )
        
        # Add questions with correct answers only
        for question_text, q_data in sorted_questions:
            # Question number and text
            question_display = f"<b>{question_counter}.</b> {sanitize_text(q_data['question'])}"
            story.append(Paragraph(question_display, question_style))
            
            # Correct answers (may be multiple if same question had different correct answers)
            for i, answer in enumerate(q_data['correct_answers']):
                if len(q_data['correct_answers']) > 1:
                    # Multiple correct answers for same question
                    answer_text = f"✓ {sanitize_text(answer)}"
                else:
                    answer_text = f"✓ {sanitize_text(answer)}"
                
                story.append(Paragraph(answer_text, answer_style))
            
            # Add article reference if available
            if q_data['article']:
                story.append(Paragraph(f"<i>Статья: {q_data['article']}</i>", article_style))
            else:
                story.append(Spacer(1, 0.3*cm))
            
            question_counter += 1
        
        # Add page break after each theme (except the last one)
        theme_ids = list(themes.keys())
        if theme_id != theme_ids[-1]:
            story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    
    # Print statistics
    total_unique = sum(len(theme['questions']) for theme in themes.values())
    print(f"PDF successfully created: {output_pdf}")
    print(f"Total themes: {len(themes)}")
    print(f"Total unique questions: {total_unique}")
    print(f"Original questions in JSON: {len(questions)}")
    print(f"Duplicates removed: {len(questions) - total_unique}")

# Usage
if __name__ == "__main__":
    json_file = "all_questions.json"  # Your JSON file
    output_pdf = "quiz_answers_only.pdf"  # Output PDF file
    
    create_answers_pdf(json_file, output_pdf)