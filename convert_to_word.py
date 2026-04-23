"""
Convert Markdown files to MS Word format
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re

def add_markdown_to_doc(md_file, doc):
    """Convert markdown content to Word document"""
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Skip empty lines
        if not line.strip():
            i += 1
            continue
        
        # Handle headers
        if line.startswith('# '):
            heading = doc.add_heading(line[2:], level=1)
            heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif line.startswith('## '):
            heading = doc.add_heading(line[3:], level=2)
            heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif line.startswith('### '):
            heading = doc.add_heading(line[4:], level=3)
            heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif line.startswith('#### '):
            heading = doc.add_heading(line[5:], level=4)
            heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Handle code blocks
        elif line.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            
            # Add code block
            code_para = doc.add_paragraph()
            code_run = code_para.add_run('\n'.join(code_lines))
            code_run.font.name = 'Courier New'
            code_run.font.size = Pt(9)
            code_para.paragraph_format.left_indent = Inches(0.5)
            code_para.paragraph_format.space_before = Pt(6)
            code_para.paragraph_format.space_after = Pt(6)
        
        # Handle bullet points
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:].strip()
            # Remove markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
            text = re.sub(r'\*(.*?)\*', r'\1', text)  # Italic
            text = re.sub(r'`(.*?)`', r'\1', text)  # Code
            doc.add_paragraph(text, style='List Bullet')
        
        # Handle numbered lists
        elif re.match(r'^\d+\. ', line):
            text = re.sub(r'^\d+\. ', '', line).strip()
            # Remove markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            text = re.sub(r'\*(.*?)\*', r'\1', text)
            text = re.sub(r'`(.*?)`', r'\1', text)
            doc.add_paragraph(text, style='List Number')
        
        # Handle tables
        elif '|' in line and i + 1 < len(lines) and '|' in lines[i + 1]:
            # Parse table
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            i -= 1
            
            # Skip separator line
            if len(table_lines) > 1 and '-' in table_lines[1]:
                table_lines.pop(1)
            
            # Create table
            if table_lines:
                rows = []
                for tline in table_lines:
                    cells = [cell.strip() for cell in tline.split('|')[1:-1]]
                    rows.append(cells)
                
                if rows:
                    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
                    table.style = 'Light Grid Accent 1'
                    
                    for row_idx, row_data in enumerate(rows):
                        for col_idx, cell_data in enumerate(row_data):
                            cell = table.rows[row_idx].cells[col_idx]
                            cell.text = cell_data
                            if row_idx == 0:  # Header row
                                for paragraph in cell.paragraphs:
                                    for run in paragraph.runs:
                                        run.font.bold = True
        
        # Handle horizontal rules
        elif line.strip() == '---':
            doc.add_paragraph('_' * 50)
        
        # Handle regular paragraphs
        else:
            if line.strip():
                # Remove markdown formatting
                text = line
                
                # Handle bold and italic
                para = doc.add_paragraph()
                
                # Split by bold markers
                parts = re.split(r'(\*\*.*?\*\*)', text)
                for part in parts:
                    if part.startswith('**') and part.endswith('**'):
                        run = para.add_run(part[2:-2])
                        run.bold = True
                    else:
                        # Split by italic markers
                        italic_parts = re.split(r'(\*.*?\*)', part)
                        for ipart in italic_parts:
                            if ipart.startswith('*') and ipart.endswith('*') and not ipart.startswith('**'):
                                run = para.add_run(ipart[1:-1])
                                run.italic = True
                            else:
                                # Handle inline code
                                code_parts = re.split(r'(`.*?`)', ipart)
                                for cpart in code_parts:
                                    if cpart.startswith('`') and cpart.endswith('`'):
                                        run = para.add_run(cpart[1:-1])
                                        run.font.name = 'Courier New'
                                        run.font.size = Pt(10)
                                    else:
                                        if cpart:
                                            para.add_run(cpart)
        
        i += 1

def create_word_document():
    """Create Word documents from markdown files"""
    
    # Create document for notes
    print("Creating AWS ECS Complete Notes document...")
    doc1 = Document()
    
    # Add title
    title = doc1.add_heading('AWS ECS Complete Study Notes', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add subtitle
    subtitle = doc1.add_paragraph('Comprehensive Guide to AWS Lambda, Fargate, and EC2 in ECS')
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle_run = subtitle.runs[0]
    subtitle_run.font.size = Pt(14)
    subtitle_run.font.color.rgb = RGBColor(128, 128, 128)
    
    doc1.add_paragraph()
    
    # Add content
    add_markdown_to_doc('AWS_ECS_Complete_Notes.md', doc1)
    
    # Save document
    doc1.save('AWS_ECS_Complete_Notes.docx')
    print("✓ Created: AWS_ECS_Complete_Notes.docx")
    
    # Create document for practical exercises
    print("\nCreating AWS ECS Practical Exercises document...")
    doc2 = Document()
    
    # Add title
    title2 = doc2.add_heading('AWS ECS Practical Exercises', 0)
    title2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add subtitle
    subtitle2 = doc2.add_paragraph('Hands-on Labs and Real-World Scenarios')
    subtitle2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle2_run = subtitle2.runs[0]
    subtitle2_run.font.size = Pt(14)
    subtitle2_run.font.color.rgb = RGBColor(128, 128, 128)
    
    doc2.add_paragraph()
    
    # Add content
    add_markdown_to_doc('AWS_ECS_Practical_Exercises.md', doc2)
    
    # Save document
    doc2.save('AWS_ECS_Practical_Exercises.docx')
    print("✓ Created: AWS_ECS_Practical_Exercises.docx")
    
    print("\n" + "="*50)
    print("SUCCESS! Both Word documents have been created:")
    print("1. AWS_ECS_Complete_Notes.docx")
    print("2. AWS_ECS_Practical_Exercises.docx")
    print("="*50)

if __name__ == '__main__':
    create_word_document()
