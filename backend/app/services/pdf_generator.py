import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.modules.requests.models.fuel_request import FuelRequest

def get_dmcar_table(request: FuelRequest):
    """Generates a single DMCAR table block."""
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', 
        parent=styles['Normal'], 
        fontName='Helvetica-Bold', 
        fontSize=14, 
        alignment=1, # Center
    )
    logo_style = ParagraphStyle(
        'LogoStyle', 
        parent=styles['Normal'], 
        fontName='Helvetica-Bold', 
        fontSize=12, 
        textColor=colors.red,
        alignment=1, # Center
    )

    logo_p = Paragraph("GROUPE<br/><b>Y</b><br/>COSELEC", logo_style)
    title_p = Paragraph("DEMANDE DE CARBURANT", title_style)

    # We use 5 columns
    data = [
        [logo_p, title_p, "", "", ""],
        ["DATE:", str(request.request_date), "", "", ""],
        ["AFFAIRE:", request.affaire_no or "", "", "", ""],
        ["DOSSIER:", request.dossier_no or "", "", "", ""],
        [f"OBJET DEPLACEMENT .......................... {request.objet_deplacement}", "", "", "", ""],
        [f"VEHICULE .............................................. {request.vehicule_matricule}", "", "", "", ""],
        [f"DESTINATION ........................................ {request.destination}", "", "", "", ""],
        [f"RELEVE KILOMETRIQUE .................... {request.releve_kilometrique}", "", "", "", ""],
        [f"NOMBRE DE JOURS ............................ {request.nombre_jours}", "", "", "", ""],
        [f"QUANTITE DE CARBURANT ............... {request.quantite_carburant} L", "", "", "", ""],
    ]

    # Calculate employee name
    employee_name = ""
    if request.employee:
        employee_name = f"{request.employee.first_name} {request.employee.last_name}"

    sig_data = [
        ["DEMANDEUR", "RESP. SERVICE", "VISA DIRECTION"],
        [
            employee_name,
            f"Validé par:\n{request.manager.name if hasattr(request, 'manager') and request.manager else ''}",
            f"Validé par:\n{request.finance_validator.name if hasattr(request, 'finance_validator') and request.finance_validator else 'En attente'}"
        ]
    ]

    t_main = Table(data, colWidths=[130, 95, 95, 95, 95], rowHeights=[40, 20, 20, 20, 25, 25, 25, 25, 25, 25])
    
    t_main.setStyle(TableStyle([
        # Logo & Title
        ('SPAN', (1, 0), (4, 0)),
        ('ALIGN', (0, 0), (4, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        
        # Grid lines only for Date, Affaire, Dossier
        ('SPAN', (1, 1), (2, 1)),
        ('SPAN', (3, 1), (4, 1)),
        
        ('SPAN', (1, 2), (2, 2)),
        ('SPAN', (3, 2), (4, 2)),
        
        ('SPAN', (1, 3), (2, 3)),
        ('SPAN', (3, 3), (4, 3)),

        # Span all for the dotted lines
        ('SPAN', (0, 4), (4, 4)),
        ('SPAN', (0, 5), (4, 5)),
        ('SPAN', (0, 6), (4, 6)),
        ('SPAN', (0, 7), (4, 7)),
        ('SPAN', (0, 8), (4, 8)),
        ('SPAN', (0, 9), (4, 9)),
        
        ('FONTNAME', (0, 1), (0, 9), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))

    t_sig = Table(sig_data, colWidths=[170, 170, 170], rowHeights=[20, 50])
    t_sig.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    return [t_main, t_sig]

def generate_dmcar_pdf(request: FuelRequest) -> str:
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=30, bottomMargin=30)
    
    elements = []
    
    # Add top table
    elements.extend(get_dmcar_table(request))
    
    # Add dotted separator
    styles = getSampleStyleSheet()
    separator = Paragraph("<br/>" + "-"*90 + "<br/><br/>", styles['Normal'])
    elements.append(separator)
    
    # Add bottom table (duplicate)
    elements.extend(get_dmcar_table(request))
    
    doc.build(elements)
    
    pdf_buffer.seek(0)
    file_name = f"DMCAR_{request.id:04d}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    local_path = f"uploads/{file_name}"
    
    os.makedirs("uploads", exist_ok=True)
    
    try:
        with open(local_path, "wb") as f:
            f.write(pdf_buffer.read())
        return local_path
    except Exception as e:
        print(f"Error saving PDF locally: {e}")
        return ""


# -----------------------------------------
# CAISSE PDF GENERATOR
# -----------------------------------------

def generate_caisse_pdf(data: dict) -> str:
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    elements = []
    
    logo_style = ParagraphStyle('LogoStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.red, alignment=1)
    elements.append(Paragraph("GROUPE<br/><b>Y</b><br/>COSELEC", logo_style))
    elements.append(Spacer(1, 20))
    
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, alignment=1, spaceAfter=10)
    elements.append(Paragraph("COSELEC &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; \"A\"", header_style))
    
    depense_style = ParagraphStyle('Depense', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, alignment=1, backColor=colors.lightgrey)
    elements.append(Table([[Paragraph("PIECE DE CAISSE / DEPENSE", depense_style)]], colWidths=[510], style=[('BOX', (0,0), (-1,-1), 0.25, colors.black)]))
    elements.append(Spacer(1, 10))
    
    num = data.get("num", "")
    affaire = data.get("affaire", "")
    cia = data.get("cia", "")
    
    elements.append(Paragraph(f"<b>NUM :</b> {num}", styles['Normal']))
    elements.append(Paragraph(f"<b>N°AFFAIRE :</b> {affaire}", styles['Normal']))
    elements.append(Paragraph(f"<b>N°CIA :</b> {cia}", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    # Depense Table
    depense_rows = data.get("depenses", [])
    t_depense_data = [["DATE", "DESIGNATION", "MONTANT"]]
    
    num_rows = max(4, len(depense_rows))
    for i in range(num_rows):
        if i < len(depense_rows):
            t_depense_data.append([depense_rows[i].get("date", ""), depense_rows[i].get("designation", ""), depense_rows[i].get("montant", "")])
        else:
            t_depense_data.append(["", "", ""])
            
    t_depense = Table(t_depense_data, colWidths=[80, 330, 100], rowHeights=[20] + [30]*num_rows)
    t_depense.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
    ]))
    elements.append(t_depense)
    elements.append(Spacer(1, 20))
    
    elements.append(Table([[Paragraph("PIECE DE CAISSE / RECETTE", depense_style)]], colWidths=[510], style=[('BOX', (0,0), (-1,-1), 0.25, colors.black)]))
    elements.append(Spacer(1, 10))
    
    # Recette Table
    recette_rows = data.get("recettes", [])
    t_recette_data = [["DATE", "DESIGNATION", "MONTANT"]]
    
    num_rec_rows = max(4, len(recette_rows))
    for i in range(num_rec_rows):
        if i < len(recette_rows):
            t_recette_data.append([recette_rows[i].get("date", ""), recette_rows[i].get("designation", ""), recette_rows[i].get("montant", "")])
        else:
            t_recette_data.append(["", "", ""])
            
    t_recette = Table(t_recette_data, colWidths=[80, 330, 100], rowHeights=[20] + [30]*num_rec_rows)
    t_recette.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
    ]))
    elements.append(t_recette)
    elements.append(Spacer(1, 30))
    
    # Signatures
    sig_data = [
        ["Service\nDemandeur", "Visa contrôleur de\ngestion", "Visa D.G.A", "Visa D.G"]
    ]
    t_sig = Table(sig_data, colWidths=[127, 127, 127, 127], rowHeights=[40])
    t_sig.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(t_sig)
    
    doc.build(elements)
    
    pdf_buffer.seek(0)
    file_name = f"CAISSE_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    local_path = f"uploads/{file_name}"
    
    os.makedirs("uploads", exist_ok=True)
    
    try:
        with open(local_path, "wb") as f:
            f.write(pdf_buffer.read())
        return local_path
    except Exception as e:
        print(f"Error saving PDF locally: {e}")
        return ""
