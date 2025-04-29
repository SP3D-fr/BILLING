from flask import Blueprint, send_file, abort
from models import db, Facture, Client, LigneFacture, Produit, Settings
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os

invoice_pdf_api = Blueprint('invoice_pdf_api', __name__)

def get_setting(key, default=""):
    s = Settings.query.get(key)
    return s.value if s else default

# Fonction centrale unique pour générer le PDF d'une facture dans un buffer
def build_invoice_pdf(facture_id, buffer):
    facture = Facture.query.get_or_404(facture_id)
    client = Client.query.get(facture.client_id)
    lignes = LigneFacture.query.filter_by(facture_id=facture.id).all()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    styles = getSampleStyleSheet()
    email = get_setting('email', 'contact@sp3d.fr')
    telephone = get_setting('telephone', '06 00 00 00 00')
    adresse = get_setting('adresse', "123 Rue de l'Impression, 75000 Paris")
    iban = get_setting('iban', 'FR76 XXXX XXXX XXXX XXXX XXXX XXX')
    logo_path = os.path.join(os.path.dirname(__file__), 'static', 'logo_sp3d.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 20, height - 70, width=40, height=40, mask='auto')
    p.setFont('Helvetica-Bold', 20)
    p.drawString(70, height - 50, "SP3D Printing")
    p.setFont('Helvetica', 10)
    p.drawString(70, height - 65, f"{email} | {telephone}")
    p.drawString(70, height - 80, adresse)
    p.setFont('Helvetica-Bold', 12)
    p.drawString(width - 220, height - 50, "Facturé à :")
    p.setFont('Helvetica', 10)
    if client:
        p.drawString(width - 220, height - 65, client.nom)
        if client.adresse:
            p.drawString(width - 220, height - 80, client.adresse)
        if client.email:
            p.drawString(width - 220, height - 95, client.email)
        if client.telephone:
            p.drawString(width - 220, height - 110, client.telephone)
    else:
        p.drawString(width - 220, height - 65, f"ID client : {facture.client_id}")
    p.setFont('Helvetica-Bold', 14)
    p.drawString(50, height - 120, f"Facture n° {facture.id}")
    p.setFont('Helvetica', 10)
    p.drawString(50, height - 140, f"Date : {facture.date}")
    data = [["Produit", "Quantité", "Prix unitaire", "Total"]]
    for ligne in lignes:
        produit = Produit.query.get(ligne.produit_id)
        nom = produit.nom if produit else f"ID {ligne.produit_id}"
        data.append([
            nom,
            str(ligne.quantite),
            f"{ligne.prix_unitaire:.2f} €",
            f"{ligne.prix_unitaire * ligne.quantite:.2f} €"
        ])
    table = Table(data, colWidths=[120, 60, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, height - 220 - 30 * len(data))
    p.setFont('Helvetica-Bold', 12)
    p.drawString(400, height - 230 - 30 * len(data), f"Total : {facture.montant:.2f} €")
    p.setFont('Helvetica', 10)
    p.drawString(50, 80, f"IBAN : {iban}")
    p.save()
    buffer.seek(0)

# Génération PDF pour téléchargement
@invoice_pdf_api.route('/api/factures/<int:facture_id>/pdf', methods=['GET'])
def facture_pdf(facture_id):
    buffer = BytesIO()
    build_invoice_pdf(facture_id, buffer)
    buffer.seek(0)
    return send_file(buffer, download_name=f'Facture_{facture_id}.pdf', as_attachment=True, mimetype='application/pdf')

# Génération PDF pour envoi mail (retourne bytes)
def generate_invoice_pdf_bytes(facture_id):
    # Utilise exactement la même logique que pour le téléchargement
    buffer = BytesIO()
    facture = Facture.query.get_or_404(facture_id)
    client = Client.query.get(facture.client_id)
    lignes = LigneFacture.query.filter_by(facture_id=facture.id).all()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    styles = getSampleStyleSheet()
    email = get_setting('email', 'contact@sp3d.fr')
    telephone = get_setting('telephone', '06 00 00 00 00')
    adresse = get_setting('adresse', "123 Rue de l'Impression, 75000 Paris")
    iban = get_setting('iban', 'FR76 XXXX XXXX XXXX XXXX XXXX XXX')
    logo_path = os.path.join(os.path.dirname(__file__), 'static', 'logo_sp3d.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 20, height - 70, width=40, height=40, mask='auto')
    p.setFont('Helvetica-Bold', 20)
    p.drawString(70, height - 50, "SP3D Printing")
    p.setFont('Helvetica', 10)
    p.drawString(70, height - 65, f"{email} | {telephone}")
    p.drawString(70, height - 80, adresse)
    p.setFont('Helvetica-Bold', 12)
    p.drawString(width - 220, height - 50, "Facturé à :")
    p.setFont('Helvetica', 10)
    if client:
        p.drawString(width - 220, height - 65, client.nom)
        if client.adresse:
            p.drawString(width - 220, height - 80, client.adresse)
        if client.email:
            p.drawString(width - 220, height - 95, client.email)
        if client.telephone:
            p.drawString(width - 220, height - 110, client.telephone)
    else:
        p.drawString(width - 220, height - 65, f"ID client : {facture.client_id}")
    p.setFont('Helvetica-Bold', 14)
    p.drawString(50, height - 120, f"Facture n° {facture.id}")
    p.setFont('Helvetica', 10)
    p.drawString(50, height - 140, f"Date : {facture.date}")
    data = [["Produit", "Quantité", "Prix unitaire", "Total"]]
    for ligne in lignes:
        produit = Produit.query.get(ligne.produit_id)
        nom = produit.nom if produit else f"ID {ligne.produit_id}"
        data.append([
            nom,
            str(ligne.quantite),
            f"{ligne.prix_unitaire:.2f} €",
            f"{ligne.prix_unitaire * ligne.quantite:.2f} €"
        ])
    table = Table(data, colWidths=[120, 60, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    table.wrapOn(p, width, height)
    table.drawOn(p, 50, height - 220 - 30 * len(data))
    p.setFont('Helvetica-Bold', 12)
    p.drawString(400, height - 230 - 30 * len(data), f"Total : {facture.montant:.2f} €")
    p.setFont('Helvetica', 10)
    p.drawString(50, 80, f"IBAN : {iban}")
    p.save()
    buffer.seek(0)
    return buffer.getvalue()
