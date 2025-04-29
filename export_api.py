from flask import Blueprint, Response
from models import db, Client, Produit, Facture
import csv
from io import StringIO

export_api = Blueprint('export_api', __name__)

def make_csv(rows, header):
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(header)
    writer.writerows(rows)
    return si.getvalue()

@export_api.route('/api/export/clients', methods=['GET'])
def export_clients():
    clients = Client.query.all()
    rows = [[c.id, c.nom, c.email, c.telephone, c.adresse] for c in clients]
    csv_data = make_csv(rows, ["ID", "Nom", "Email", "Téléphone", "Adresse"])
    return Response(csv_data, mimetype='text/csv', headers={"Content-Disposition":"attachment;filename=clients.csv"})

@export_api.route('/api/export/produits', methods=['GET'])
def export_produits():
    produits = Produit.query.all()
    rows = [[p.id, p.nom, p.prix, p.description] for p in produits]
    csv_data = make_csv(rows, ["ID", "Nom", "Prix", "Description"])
    return Response(csv_data, mimetype='text/csv', headers={"Content-Disposition":"attachment;filename=produits.csv"})

@export_api.route('/api/export/factures', methods=['GET'])
def export_factures():
    factures = Facture.query.all()
    rows = [[f.id, f.client_id, f.date, f.montant, f.statut] for f in factures]
    csv_data = make_csv(rows, ["ID", "Client ID", "Date", "Montant", "Statut"])
    return Response(csv_data, mimetype='text/csv', headers={"Content-Disposition":"attachment;filename=factures.csv"})
