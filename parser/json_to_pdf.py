import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY

# Register fonts that support Cyrillic (you'll need to have these font files)
# Download DejaVuSans fonts if you don't have them
try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
    font_name = 'DejaVuSans'
    font_bold = 'DejaVuSans-Bold'
except:
    print("Warning: DejaVuSans fonts not found. Using default fonts (may not display Cyrillic correctly)")
    font_name = 'Helvetica'
    font_bold = 'Helvetica-Bold'

def sanitize_text(text):
    """Sanitize text for ReportLab PDF generation"""
    if not text:
        return text
    # Replace HTML br tags with proper self-closing tags
    text = text.replace('<br>', '<br/>')
    text = text.replace('<BR>', '<br/>')
    text = text.replace('<br >', '<br/>')
    # Escape ampersands
    text = text.replace('&', '&amp;')
    return text

def create_pdf_from_json(json_file, output_pdf):
    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Group questions by theme
    themes = {}
    for q in questions:
        theme_id = q['theme_id']
        if theme_id not in themes:
            themes[theme_id] = {
                'name': q['theme_name'],
                'questions': []
            }
        themes[theme_id]['questions'].append(q)
    
    # Create PDF
    doc = SimpleDocTemplate(output_pdf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles for Cyrillic text
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
        alignment=TA_LEFT
    )
    
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=11,
        spaceAfter=8,
        alignment=TA_LEFT
    )
    
    answer_style = ParagraphStyle(
        'Answer',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        spaceAfter=4,
        leftIndent=20,
        alignment=TA_LEFT
    )
    
    correct_answer_style = ParagraphStyle(
        'CorrectAnswer',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=10,
        spaceAfter=4,
        leftIndent=20,
        textColor='green',
        alignment=TA_LEFT
    )
    
    article_style = ParagraphStyle(
        'Article',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        spaceAfter=15,
        leftIndent=20,
        textColor='grey',
        alignment=TA_LEFT
    )
    
    # Build PDF content
    story = []
    
    # Add title
    story.append(Paragraph("Вопросы для подготовки к экзамену", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Add questions grouped by theme
    for theme_id in sorted(themes.keys(), key=lambda x: int(x)):
        theme_data = themes[theme_id]
        
        # Add theme title
        story.append(Paragraph(f"<b>Тема {theme_id}: {theme_data['name']}</b>", theme_style))
        story.append(Spacer(1, 0.3*cm))
        
        # Add questions
        for q in theme_data['questions']:
            # Question number and text
            question_text = f"<b>Вопрос {q['question_number']}:</b> {sanitize_text(q['question'])}"
            story.append(Paragraph(question_text, question_style))
            
            # Answers
            for answer_id in sorted(q['answers'].keys(), key=lambda x: int(x)):
                answer_text = sanitize_text(q['answers'][answer_id])
                # Sanitize HTML tags - replace <br> with line breaks
                answer_text = answer_text.replace('<br>', '<br/>')
                answer_text = answer_text.replace('<BR>', '<br/>')
                # Escape other special characters if needed
                answer_text = answer_text.replace('&', '&amp;')
                
                # Highlight correct answer
                if answer_id == q['correct_answer']:
                    story.append(Paragraph(f"{sanitize_text(answer_text)} <b>(Правильный ответ)</b>", 
                                         correct_answer_style))
                else:
                    story.append(Paragraph(f"{answer_text}", answer_style))
            
            # Add article reference if available
            if 'article' in q and q['article']:
                story.append(Paragraph(f"<i>Статья: {q['article']}</i>", article_style))
            else:
                story.append(Spacer(1, 0.3*cm))
        
        # Add page break after each theme (except the last one)
        if theme_id != list(themes.keys())[-1]:
            story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    print(f"PDF successfully created: {output_pdf}")
    print(f"Total themes: {len(themes)}")
    print(f"Total questions: {len(questions)}")

# Usage
if __name__ == "__main__":
    json_file = "all_questions.json"  # Your JSON file
    output_pdf = "quiz_questions.pdf"  # Output PDF file
    
    create_pdf_from_json(json_file, output_pdf)