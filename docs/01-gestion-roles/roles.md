# Modèle de données ERP COSELEC (V1)

> Version : 1.0
> Statut : Fondations du système
> Auteur : Adam Guizaoui

---

# Objectif

Cette structure constitue la base fonctionnelle de l'ERP COSELEC.

Elle permet de gérer :

- l'authentification
- les utilisateurs
- les rôles
- les permissions
- les départements
- les employés
- les demandes internes
- les projets
- la gestion documentaire
- le reporting

L'objectif est de conserver une architecture simple, évolutive et adaptée à une entreprise d'environ 30 utilisateurs.

---

# Organisation

## departments

Représente les services de l'entreprise.

### Champs

```text
id
name
code
created_at
updated_at
```

### Exemples

```text
Direction
RH
Commercial
Informatique
Maintenance
Logistique
Finance
```

---

# Sécurité

## users

Compte de connexion.

### Champs

```text
id
email
hashed_password
is_active
employee_id
last_login
created_at
updated_at
```

### Rôle

Le compte utilisateur sert uniquement à :

- se connecter
- être authentifié
- tracer les actions
- recevoir des notifications

---

## roles

Fonctions métier.

### Champs

```text
id
name
description
created_at
updated_at
```

### Rôles prévus

```text
Admin
RH
Commercial
Employé
Direction
Responsable Projet
```

---

## permissions

Droits granulaires du système.

### Champs

```text
id
code
name
description
module
created_at
```

### Convention de nommage

```text
module.action
```

### Exemples

```text
employees.read
employees.create
employees.update
employees.delete

requests.read
requests.create
requests.update
requests.delete
requests.approve
requests.reject

projects.read
projects.create
projects.update
projects.delete

documents.read
documents.create
documents.update
documents.delete

reports.read
```

---

## user_roles

Permet d'associer un ou plusieurs rôles à un utilisateur.

### Champs

```text
id
user_id
role_id
```

### Exemple

```text
Adam
→ Admin

ou

Adam
→ Admin
→ Responsable Projet
```

---

## role_permissions

Permet d'associer des permissions à un rôle.

### Champs

```text
id
role_id
permission_id
```

### Exemple

```text
Role RH

→ employees.read
→ employees.create
→ employees.update
→ requests.approve
```

---

# Ressources Humaines

## employees

Fiche employé.

### Champs

```text
id
matricule
first_name
last_name
email
phone
department_id
manager_id
hire_date
status
user_id
created_at
updated_at
```

### Status possibles

```text
CDI
CDD
Stagiaire
Prestataire
```

### Relations

```text
Employee
    ↓
Department

Employee
    ↓
Manager (Employee)

Employee
    ↓
User
```

---

# Gestion des demandes

## request_types

Types de demandes disponibles.

### Champs

```text
id
code
name
description
is_active
```

### Exemples

```text
FUEL
LEAVE
PURCHASE
IT_EQUIPMENT
TRAVEL
ADVANCE
INTERVENTION
```

---

## requests

Table principale des demandes internes.

### Champs

```text
id
title
description
request_type_id
status
created_by
assigned_to
payload_json
submitted_at
created_at
updated_at
```

### Status possibles

```text
DRAFT
SUBMITTED
APPROVED
REJECTED
IN_PROGRESS
COMPLETED
```

---

### Champ payload_json

Permet de stocker les informations spécifiques à chaque type de demande.

Exemple carburant :

```json
{
  "vehicle": "123-A-456",
  "liters": 50,
  "project": "Chantier Rabat"
}
```

Exemple congé :

```json
{
  "start_date": "2026-08-01",
  "end_date": "2026-08-15",
  "leave_type": "Annuel"
}
```

Cette approche évite de créer une table par type de demande.

---

## request_approvals

Historique des validations.

### Champs

```text
id
request_id
approver_id
decision
comment
created_at
```

### Décisions possibles

```text
APPROVED
REJECTED
```

### Exemple

```text
Demande #14

Manager
→ APPROVED

RH
→ APPROVED
```

---

## request_attachments

Pièces jointes liées aux demandes.

### Champs

```text
id
request_id
document_id
```

---

# Gestion de projet

## projects

Projet ou chantier.

### Champs

```text
id
code
name
description
client_name
start_date
end_date
budget
status
manager_id
created_at
updated_at
```

### Status possibles

```text
PLANNED
ACTIVE
ON_HOLD
COMPLETED
CLOSED
```

---

## project_members

Affectation des collaborateurs aux projets.

### Champs

```text
id
project_id
employee_id
role
```

### Exemple

```text
Projet A

Adam
→ Chef de projet

Yassine
→ Technicien
```

---

# Gestion documentaire (GED)

## documents

Stockage centralisé des documents.

### Champs

```text
id
file_name
storage_path
mime_type
uploaded_by
entity_type
entity_id
version
created_at
```

---

### Principe

Un document peut être associé à n'importe quelle entité du système.

Exemple :

```text
entity_type = REQUEST
entity_id = 15
```

ou

```text
entity_type = PROJECT
entity_id = 8
```

ou

```text
entity_type = EMPLOYEE
entity_id = 3
```

---

# Reporting

Aucune table spécifique n'est nécessaire.

Le reporting est calculé à partir des données existantes :

```text
employees
requests
projects
documents
```

---

# Relations principales

```text
Department
    ↓
Employee

Employee
    ↓
User

User
    ↓
UserRole
    ↓
Role
    ↓
RolePermission
    ↓
Permission

Request
    ↓
RequestType

Request
    ↓
RequestApproval

Request
    ↓
Document

Project
    ↓
ProjectMember
    ↓
Employee

Project
    ↓
Document
```

---

# Périmètre V1

Cette version permet déjà de gérer :

- Authentification JWT
- Utilisateurs
- Départements
- Employés
- Rôles
- Permissions
- Demandes de congé
- Demandes de carburant
- Demandes de matériel
- Validations hiérarchiques
- Projets
- Documents
- Tableaux de bord
- Reporting

Soit une base solide pour le développement progressif de l'ERP COSELEC.