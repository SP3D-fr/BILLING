-- Migration pour la refonte du modèle Facture/LigneFacture
ALTER TABLE facture ADD COLUMN reduction_type VARCHAR(10);
ALTER TABLE facture ADD COLUMN reduction_value FLOAT DEFAULT 0;

CREATE TABLE ligne_facture (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    facture_id INTEGER NOT NULL,
    produit_id INTEGER NOT NULL,
    quantite INTEGER NOT NULL DEFAULT 1,
    prix_unitaire FLOAT NOT NULL,
    FOREIGN KEY(facture_id) REFERENCES facture(id) ON DELETE CASCADE,
    FOREIGN KEY(produit_id) REFERENCES produit(id)
);
