import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.modules.requests.models.fuel_request import FuelRequest
from app.services.storage import upload_buffer_to_minio

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

    logo_path = os.path.join(os.path.dirname(__file__), "../../../frontend/public/logo_coselec.jfif")
    if os.path.exists(logo_path):
        logo_p = Image(logo_path, width=60, height=60)
    else:
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
    
    try:
        # Save directly to Cloudflare R2 / MinIO
        return upload_buffer_to_minio(pdf_buffer, file_name)
    except Exception as e:
        print(f"Error saving PDF to cloud: {e}")
        return ""


# -----------------------------------------
# CAISSE PDF GENERATOR
# -----------------------------------------

def generate_caisse_pdf(data: dict) -> str:
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    elements = []
    
    logo_path = os.path.join(os.path.dirname(__file__), "../../../frontend/public/logo_coselec.jfif")
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=80, height=80))
    else:
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
    
    try:
        return upload_buffer_to_minio(pdf_buffer, file_name)
    except Exception as e:
        print(f"Error saving PDF to cloud: {e}")
        return ""

# -----------------------------------------
# LEAVE CERTIFICATE PDF GENERATOR
# -----------------------------------------

def generate_leave_certificate(leave_request, employee) -> str:
    """Generates an attestation de congé."""
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Logo
    logo_path = os.path.join(os.path.dirname(__file__), "../../../frontend/public/logo_coselec.jfif")
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=80, height=80))
    else:
        logo_style = ParagraphStyle('LogoStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.red, alignment=1)
        elements.append(Paragraph("GROUPE<br/><b>Y</b><br/>COSELEC", logo_style))
    elements.append(Spacer(1, 30))
    
    # Title
    title_style = ParagraphStyle('Title', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, alignment=1, spaceAfter=20)
    elements.append(Paragraph("ATTESTATION DE CONGE", title_style))
    elements.append(Spacer(1, 20))
    
    # Body
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=12, leading=18)
    
    today_str = datetime.now().strftime('%d/%m/%Y')
    emp_name = f"{employee.first_name} {employee.last_name}" if hasattr(employee, 'first_name') else employee.name
    
    content = f"""
    Nous soussignés, la Direction des Ressources Humaines de COSELEC, attestons par la présente que :<br/><br/>
    <b>M./Mme {emp_name}</b>, employé(e) au sein de notre structure, bénéficie d'un congé de type <b>{leave_request.leave_type}</b>.<br/><br/>
    Ce congé est accordé pour la période allant du <b>{leave_request.start_date.strftime('%d/%m/%Y')}</b> au <b>{leave_request.end_date.strftime('%d/%m/%Y')}</b> inclus.<br/><br/>
    """
    if leave_request.reason:
        content += f"<b>Motif :</b> {leave_request.reason}<br/><br/>"
        
    content += "La présente attestation est délivrée pour servir et valoir ce que de droit."
    
    elements.append(Paragraph(content, body_style))
    elements.append(Spacer(1, 40))
    
    # Date & Signature
    elements.append(Paragraph(f"Fait à Dakar, le {today_str}", ParagraphStyle('Right', parent=styles['Normal'], alignment=2)))
    elements.append(Spacer(1, 40))
    
    sig_style = ParagraphStyle('Signature', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, alignment=2)
    elements.append(Paragraph("La Direction des Ressources Humaines", sig_style))
    
    doc.build(elements)
    
    pdf_buffer.seek(0)
    emp_name_clean = emp_name.replace(" ", "_").lower()
    file_name = f"conge_{emp_name_clean}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    try:
        return upload_buffer_to_minio(pdf_buffer, file_name)
    except Exception as e:
        print(f"Error saving PDF to cloud: {e}")
        return ""

# -----------------------------------------
# PURCHASE ORDER PDF GENERATOR
# -----------------------------------------

def generate_purchase_order_pdf(order) -> str:
    """Generates a Bon de Commande."""
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer, 
        pagesize=A4, 
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40,
        title=f"Bon de Commande BC-{order.id}",
        author="COSELEC"
    )
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Logo
    logo_path = os.path.join(os.path.dirname(__file__), "../../../frontend/public/logo_coselec.jfif")
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=80, height=80))
    else:
        logo_style = ParagraphStyle('LogoStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.red, alignment=1)
        elements.append(Paragraph("GROUPE<br/><b>Y</b><br/>COSELEC", logo_style))
    elements.append(Spacer(1, 20))
    
    # Title
    title_style = ParagraphStyle('Title', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, alignment=1, spaceAfter=20)
    elements.append(Paragraph(f"BON DE COMMANDE N° BC-{order.id}", title_style))
    elements.append(Spacer(1, 10))
    
    # Order Info
    info_data = [
        [Paragraph("<b>Date:</b>", styles['Normal']), Paragraph(order.created_at.strftime('%d/%m/%Y'), styles['Normal'])],
        [Paragraph("<b>Statut:</b>", styles['Normal']), Paragraph(order.status, styles['Normal'])],
    ]
    if order.supplier:
        info_data.append([Paragraph("<b>Fournisseur:</b>", styles['Normal']), Paragraph(order.supplier.name, styles['Normal'])])
        info_data.append([Paragraph("<b>Code Fournisseur:</b>", styles['Normal']), Paragraph(order.supplier.code or "-", styles['Normal'])])

    if order.purchase_request and order.purchase_request.project:
        info_data.append([Paragraph("<b>Projet:</b>", styles['Normal']), Paragraph(order.purchase_request.project.nom, styles['Normal'])])

    t_info = Table(info_data, colWidths=[100, 410], hAlign='LEFT')
    t_info.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_info)
    elements.append(Spacer(1, 20))
    
    # Order Lines
    line_data = [["Désignation", "Quantité", "Prix Unitaire", "Total"]]
    if getattr(order, 'lines', []) and len(order.lines) > 0:
        for line in order.lines:
            product_name = line.product.designation if line.product else f"Produit #{line.product_id}"
            line_data.append([
                product_name,
                str(line.quantity),
                f"{line.unit_price:,.0f} XOF",
                f"{(line.quantity * line.unit_price):,.0f} XOF"
            ])
    else:
        line_data.append(["-", "-", "-", "-"])
        
    subtotal = float(order.total_amount or 0)
    vat_amount = subtotal * 0.18
    total_ttc = subtotal + vat_amount

    line_data.append(["", "", "Sous-total HT:", f"{subtotal:,.0f} XOF"])
    line_data.append(["", "", "TVA (18%):", f"{vat_amount:,.0f} XOF"])
    line_data.append(["", "", "Total TTC:", f"{total_ttc:,.0f} XOF"])
    
    t_lines = Table(line_data, colWidths=[240, 70, 100, 100])
    t_lines.setStyle(TableStyle([
        ('BOX', (0,0), (-1,0), 1, colors.black),  # Box around header
        ('INNERGRID', (0,0), (-1,-4), 0.25, colors.black), # Grid for items
        ('BOX', (0,0), (-1,-4), 1, colors.black), # Box around items
        
        # Header styles
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        
        # Items alignment
        ('ALIGN', (1,1), (-1,-4), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        
        # Totals styles
        ('FONTNAME', (2,-3), (2,-1), 'Helvetica-Bold'),
        ('FONTNAME', (3,-3), (3,-1), 'Helvetica-Bold'),
        ('ALIGN', (2,-3), (3,-1), 'RIGHT'),
        ('BACKGROUND', (2,-1), (3,-1), colors.lightgrey), # Highlight Total TTC
        ('BOX', (2,-3), (3,-1), 1, colors.black),
        ('INNERGRID', (2,-3), (3,-1), 0.25, colors.black),
        
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_lines)
    elements.append(Spacer(1, 20))
    
    # Terms and conditions
    terms_style = ParagraphStyle('Terms', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.dimgrey)
    elements.append(Paragraph("<b>Conditions de Paiement :</b> À 30 jours fin de mois.", terms_style))
    elements.append(Paragraph("<b>Modalités de Livraison :</b> Selon les conditions spécifiées dans notre contrat cadre.", terms_style))
    elements.append(Spacer(1, 40))
    
    # Signatures
    sig_data = [
        ["Acheteur", "Direction", "Fournisseur"]
    ]
    t_sig = Table(sig_data, colWidths=[170, 170, 170], rowHeights=[40])
    t_sig.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(t_sig)
    
    doc.build(elements)
    
    pdf_buffer.seek(0)
    file_name = f"BC_{order.id:04d}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    
    try:
        return upload_buffer_to_minio(pdf_buffer, file_name)
    except Exception as e:
        print(f"Error saving PDF to cloud: {e}")
        return ""

# -----------------------------------------
# PROJECT REPORT PDF GENERATOR
# -----------------------------------------

def generate_project_report_pdf(project) -> str:
    """Generates a Project Report."""
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Logo
    logo_path = os.path.join(os.path.dirname(__file__), "../../../frontend/public/logo_coselec.jfif")
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=80, height=80))
    else:
        logo_style = ParagraphStyle('LogoStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.red, alignment=1)
        elements.append(Paragraph("GROUPE<br/><b>Y</b><br/>COSELEC", logo_style))
    elements.append(Spacer(1, 20))
    
    # Title
    title_style = ParagraphStyle('Title', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, alignment=1, spaceAfter=20)
    elements.append(Paragraph(f"RAPPORT DE PROJET : {project.nom.upper()}", title_style))
    elements.append(Spacer(1, 10))
    
    # Project Summary Info
    info_data = [
        [Paragraph("<b>Code Projet:</b>", styles['Normal']), Paragraph(project.code, styles['Normal'])],
        [Paragraph("<b>Statut:</b>", styles['Normal']), Paragraph(project.status.value if hasattr(project.status, 'value') else str(project.status), styles['Normal'])],
        [Paragraph("<b>Type:</b>", styles['Normal']), Paragraph(project.project_type or "-", styles['Normal'])],
    ]
    if project.chef_projet:
        info_data.append([Paragraph("<b>Chef de Projet:</b>", styles['Normal']), Paragraph(f"{project.chef_projet.first_name} {project.chef_projet.last_name}", styles['Normal'])])
    if project.client:
        info_data.append([Paragraph("<b>Client:</b>", styles['Normal']), Paragraph(project.client.name, styles['Normal'])])

    info_data.append([Paragraph("<b>Date Début Prévue:</b>", styles['Normal']), Paragraph(project.date_debut_estimee.strftime('%d/%m/%Y') if project.date_debut_estimee else "-", styles['Normal'])])
    info_data.append([Paragraph("<b>Date Fin Prévue:</b>", styles['Normal']), Paragraph(project.date_fin_prevue.strftime('%d/%m/%Y') if project.date_fin_prevue else "-", styles['Normal'])])

    t_info = Table(info_data, colWidths=[150, 360], hAlign='LEFT')
    t_info.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_info)
    elements.append(Spacer(1, 20))
    
    # Financial Overview
    header_style = ParagraphStyle('Header2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, spaceAfter=10)
    elements.append(Paragraph("Aperçu Financier", header_style))
    
    budget_data = [
        ["Budget Estimé", "Budget Engagé", "Reste à Engager"],
        [f"{project.budget_estime or 0} XOF", f"{project.budget_engage or 0} XOF", f"{(project.budget_estime or 0) - (project.budget_engage or 0)} XOF"]
    ]
    t_budget = Table(budget_data, colWidths=[170, 170, 170])
    t_budget.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_budget)
    elements.append(Spacer(1, 20))
    
    # Milestones (Jalons)
    elements.append(Paragraph("Jalons & Tâches", header_style))
    milestone_data = [["Nom du Jalon", "Date", "Statut"]]
    if getattr(project, 'milestones', []):
        for m in project.milestones:
            m_status = m.status.value if hasattr(m.status, 'value') else str(m.status)
            milestone_data.append([
                m.title,
                m.due_date.strftime('%d/%m/%Y') if m.due_date else "-",
                m_status
            ])
    else:
        milestone_data.append(["Aucun jalon défini", "-", "-"])
        
    t_milestones = Table(milestone_data, colWidths=[250, 130, 130])
    t_milestones.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_milestones)
    
    elements.append(Spacer(1, 40))
    elements.append(Paragraph(f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", ParagraphStyle('Right', parent=styles['Normal'], fontSize=8, alignment=2)))
    
    doc.build(elements)
    
    pdf_buffer.seek(0)
    file_name = f"Rapport_Projet_{project.code}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    
    try:
        return upload_buffer_to_minio(pdf_buffer, file_name)
    except Exception as e:
        print(f"Error saving PDF to cloud: {e}")
        return ""
