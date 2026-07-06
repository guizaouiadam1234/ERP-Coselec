# Document de Cadrage : ERP COSELEC
**Projet :** Gestion RH (Documents), Helpdesk centralisé
**Date :** 06 Juillet 2026

---

## 1. Module Helpdesk (Ticket System)
Un système unique et générique pour centraliser toutes les demandes internes.

*   **Modèle unique (`Ticket`) :**
    *   Gestion par catégories : `IT` (Accès, matériel), `PURCHASE` (Achats, réapprovisionnement), `FACILITY` (Maintenance locaux), `LEAVE` (Congés/Absences).
    *   Champ `meta_data` (JSON) : Permet de stocker des attributs spécifiques (dates de congés, références produits, etc.) sans multiplier les tables.
*   **Workflow :**
    *   `OPEN` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `RESOLVED` / `REJECTED`.
*   **Notifications :**
    *   **Mail :** Envoi automatique lors du changement de statut (via SMTP) pour informer l'initiateur.
    *   **In-App :** Badge visuel sur la cloche de notification pour les gestionnaires (files d'attente par service).

---

## 2. Module Documents Employés
Gestion documentaire pour répondre aux exigences réglementaires sénégalaises (Inspection du travail).

*   **Classification :**
    *   **Identité :** CIN, Passeport, Visa/Carte de résident.
    *   **Social/Familial :** Certificat de mariage, actes de naissance (pour allocations).
    *   **Contrat :** Contrat de travail, visite médicale.
*   **Conformité & Alertes :**
    *   Champ `expiry_date` pour le suivi des dates de fin de validité.
    *   **Alerte 6 mois :** Système de pastilles de couleurs (Orange < 6 mois, Rouge < 3 mois) sur le tableau de bord RH.
    *   **Validation :** Système de double vérification (`is_verified` booléen) pour valider la conformité des documents scannés.

---

## 3. Architecture Technique (SMTP & Notifs)
Pour assurer le fonctionnement des notifications mails sur le serveur local de l'entreprise :

*   **Protocole :** Utilisation de `FastAPI-Mail` avec configuration SMTP via variables d'environnement (`.env`).
*   **Stratégie d'envoi :**
    *   *Réactive :* Envoi immédiat lors d'un changement de statut de ticket.
    *   *Batch (Cron) :* Script hebdomadaire pour scanner les documents expirants et alerter la RH sans spammer.

---

## 4. Prochaines étapes de développement
1.  **Backend :** Création du modèle `Ticket` et `EmployeeDocument`, et migration `Alembic`.
2.  **Frontend :** Création de la vue "Helpdesk" avec les onglets "Mes demandes" et "Validations".
3.  **Documents :** Mise en place de l'upload de fichiers et de la checklist de conformité sur la fiche employé.

---
*Ce document sert de référence pour le développement de l'ERP. Toute modification majeure des flux doit être approuvée par l'équipe de développement.*