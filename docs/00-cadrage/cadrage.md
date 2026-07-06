# Cadrage du projet ERP - Coselec
> Version : v0.1
> Statut : Brouillon initial
> Projet : ERP Interne
> Auteur : Adam Guizaoui
> Nombre d'utilisateurs estimés : 30

## Contexte

COSELEC souhaite mettre en place un ERP interne afin de centraliser, structurer et automatiser une partie importante de ses processus administratifs, opérationnels et de gestion.

Aujourd'hui, plusieurs activités sont suivies à travers différents supports : fichiers Excel, documents papier, échanges WhatsApp, e-mails, dossiers locaux ou partages réseau. Cette organisation rend parfois difficile le suivi des informations, la traçabilité des décisions, la mise à jour des données et la production de rapports fiables.

L'objectif du projet est donc de concevoir et développer une application web interne permettant de gérer progressivement les principaux processus de l'entreprise autour d'une plateforme unique.
L'ERP devra être adapté à la réalité de COSELEC, à ses processus internes, à ses ressources techniques et au nombre limité d'utilisateurs prévus au démarrage.

---

## Objectifs

Le projet ERP COSELEC a pour objectifs principaux :

- centraliser les données importantes de l'entreprise 
- automatiser les processus répétitifs 
- améliorer le suivi des demandes internes 
- fiabiliser les données RH, stock, immobilisations et projets 
- faciliter la gestion documentaire 
- améliorer la traçabilité des validations 
- réduire la dépendance aux fichiers Excel non mis à jour 
- améliorer le reporting pour la direction et les responsables 
- structurer les workflows internes 
- faciliter l'accès à l'information selon les droits des utilisateurs

L'application devra permettre à COSELEC de passer progressivement d'une gestion dispersée à une gestion centralisée, contrôlée et digitalisée.

---
## Problèmes actuels identifiés

Les problèmes suivants ont été identifiés à ce stade :

- les informations sont dispersées entre plusieurs fichiers, outils et supports 
- certains fichiers Excel existent mais ne sont pas régulièrement mis à jour 
- les demandes internes sont parfois faites de manière informelle 
- les validations ne sont pas toujours tracées 
- les documents sont parfois difficiles à retrouver 
- les affectations de matériel, véhicules ou équipements peuvent manquer de suivi 
- les données de stock et d'immobilisations peuvent manquer de fiabilité 
- les rapports consolidés sont difficiles à produire rapidement 
- les responsabilités dans certains processus ne sont pas toujours clairement documentées 
- certains processus dépendent fortement de personnes spécifiques 
- il n'existe pas encore de plateforme unique pour suivre l'ensemble des opérations.

---
## Vision cible

La vision cible est de disposer d'une application web interne accessible aux utilisateurs autorisés, permettant de gérer les principaux modules suivants :

- capital humain 
- demandes internes 
- gestion commerciale 
- stock 
- immobilisations 
- budget 
- gestion électronique de documents 
- gestion de projet 
- maintenance assistée par ordinateur 
- qualité 
- reporting 
- administration des utilisateurs et des droits.

L'application devra être modulaire afin de permettre un développement progressif.

Le cœur du système devra reposer sur les éléments suivants :

```text
Utilisateurs
Rôles
Permissions
Demandes
Workflows
Documents
Projets
Stock
Immobilisations
Reporting
```

## 5. Périmètre fonctionnel initial

Le périmètre fonctionnel global du projet couvre les modules suivants.

### 5.1 Gestion du capital humain

Le module capital humain devra permettre de gérer les informations liées aux employés.

Fonctionnalités envisagées :

- fiches employés 
- statut de l'employé : CDI, CDD, stagiaire ou autre 
- suivi des contrats 
- suivi des congés 
- suivi des absences 
- suivi des déplacements chantier 
- rattachement à un service ou département 
- rattachement à un responsable hiérarchique.

---

### 5.2 Demandes internes

Le module demandes internes devra permettre de centraliser les demandes faites par les utilisateurs.

Types de demandes envisagés :

- demande de carburant 
- demande de PC 
- demande de matériel 
- demande de déplacement chantier 
- demande de congé 
- demande d'achat 
- demande d'avance 
- demande d'intervention 
- autres demandes configurables.

Le module devra intégrer :

- formulaire de demande 
- brouillon 
- soumission 
- validation 
- refus avec motif 
- traitement 
- clôture 
- historique 
- notifications 
- suivi par statut.

---

### 5.3 Gestion commerciale

Le module commercial devra permettre de suivre les clients, prospects et opportunités commerciales.

Fonctionnalités envisagées :

- gestion des clients 
- gestion des prospects 
- contacts clients 
- opportunités commerciales 
- devis 
- contrats 
- suivi des relances 
- conversion d'une affaire gagnée en projet ou chantier.

---

### 5.4 Gestion de stock, immobilisations et budget

Ce module devra permettre de remplacer progressivement les suivis Excel existants.

Fonctionnalités envisagées :

- articles 
- consommables 
- entrées en stock 
- sorties de stock 
- inventaires 
- immobilisations 
- affectation matériel à un employé, projet ou chantier 
- suivi de l'état du matériel 
- budget prévu/réalisé 
- alertes de stock minimum 
- import initial depuis Excel 
- exports.

---

### 5.5 Gestion électronique de documents

Le module GED devra permettre de centraliser les documents importants.

Fonctionnalités envisagées :

- dépôt de documents 
- classement par module 
- recherche 
- rattachement à une entité : employé, demande, projet, client, équipement, etc. 
- gestion des versions 
- droits d'accès 
- historique 
- documents expirables 
- téléchargement contrôlé.

---

### 5.6 Gestion de projet

Le module projet devra permettre de suivre les projets et chantiers.

Fonctionnalités envisagées :

- fiche projet 
- client lié 
- responsable projet 
- équipe affectée 
- budget 
- avancement 
- tâches 
- jalons 
- rapports chantier 
- documents projet 
- matériel affecté 
- clôture projet.

---

### 5.7 Maintenance assistée par ordinateur

Le module maintenance devra permettre de suivre les équipements et interventions.

Fonctionnalités envisagées :

- équipements 
- véhicules 
- matériel de chantier 
- déclaration de panne 
- ordre de maintenance 
- maintenance corrective 
- maintenance préventive 
- historique des interventions 
- coût de maintenance 
- pièces utilisées 
- rapports d'intervention.

---

### 5.8 Qualité

Le module qualité devra permettre de suivre les procédures, non-conformités et actions correctives.

Fonctionnalités envisagées :

- procédures qualité 
- audits 
- non-conformités 
- actions correctives 
- actions préventives 
- réclamations clients 
- suivi des plans d'action 
- indicateurs qualité.

---

### 5.9 Reporting

Le reporting devra permettre de produire des tableaux de bord fiables à partir des données saisies dans l'ERP.

Indicateurs envisagés :

- demandes par type et statut 
- délais moyens de traitement 
- demandes en attente de validation 
- employés par statut 
- congés et absences 
- stock critique 
- immobilisations affectées 
- projets en cours 
- budget prévu/réalisé 
- interventions maintenance 
- non-conformités ouvertes 
- documents expirés.

---

## 6. Utilisateurs concernés

Le nombre d'utilisateurs estimé au démarrage est d'environ 30.

Les profils utilisateurs envisagés sont :

- administrateur 
- direction 
- ressources humaines 
- commercial 
- responsable projet 
- stock / logistique 
- maintenance 
- qualité 
- finance / budget 

Chaque utilisateur devra avoir accès uniquement aux fonctionnalités et données correspondant à son rôle.

Les utilisateurs pourront être regroupés selon :

- leur service 
- leur rôle 
- leur niveau hiérarchique 
- leur périmètre projet 
- leurs droits de validation 
- leur niveau d'accès aux documents.

Le système devra permettre une gestion fine des droits afin d'éviter qu'un utilisateur accède à des informations qui ne le concernent pas, notamment pour les données RH, les documents sensibles et les informations financières.

---

## 7. Rôles principaux envisagés

### 7.1 Administrateur

Responsabilités :

- gérer les utilisateurs 
- gérer les rôles 
- gérer les permissions 
- gérer les paramètres de l'application 
- superviser la plateforme 
- consulter les logs techniques et fonctionnels 
- désactiver ou réactiver des comptes utilisateurs 
- créer ou modifier certains référentiels 
- assister les utilisateurs en cas de problème.

L'administrateur dispose du niveau d'accès le plus élevé sur la plateforme.

---

### 7.2 Direction

Responsabilités :

- consulter les tableaux de bord globaux 
- suivre les indicateurs clés 
- consulter les données consolidées 
- valider certaines demandes sensibles 
- suivre les projets importants 
- consulter les informations budgétaires 
- accéder aux reportings stratégiques.

La direction n'a pas nécessairement vocation à modifier toutes les données, mais doit pouvoir disposer d'une vision globale et fiable de l'activité.

---

### 7.3 Ressources humaines

Responsabilités :

- gérer les fiches employés 
- suivre les contrats 
- suivre les statuts CDI, CDD, stagiaires ou autres 
- gérer les congés 
- suivre les absences 
- gérer les documents RH 
- suivre les alertes de fin de contrat 
- consulter l'historique RH des employés 
- valider ou traiter certaines demandes liées au personnel.

Les utilisateurs RH doivent avoir accès aux données RH, mais cet accès doit rester limité aux personnes autorisées.

---

### 7.4 Commercial

Responsabilités :

- gérer les prospects 
- gérer les clients 
- suivre les opportunités commerciales 
- créer ou suivre les devis 
- suivre les contrats commerciaux 
- suivre les relances 
- consulter l'historique client 
- transformer une affaire gagnée en projet ou chantier si le processus le prévoit.

Le commercial doit avoir accès principalement aux données clients, prospects, devis, opportunités et contrats commerciaux.

---

### 7.5 Responsable projet

Responsabilités :

- créer ou suivre les projets 
- consulter les informations projet 
- affecter des ressources humaines ou matérielles 
- suivre l'avancement 
- consulter les documents projet 
- valider certaines demandes liées au projet 
- suivre les budgets projet 
- consulter les rapports chantier 
- clôturer ou demander la clôture d'un projet.

Le responsable projet doit avoir accès aux projets dont il est responsable, ainsi qu'aux demandes, documents et ressources liés à ces projets.

---

### 7.7 Stock / Logistique

Responsabilités :

- gérer les articles 
- gérer les entrées en stock 
- gérer les sorties de stock 
- traiter les demandes de matériel 
- traiter les demandes de carburant 
- suivre les immobilisations 
- affecter du matériel à un employé, projet ou chantier 
- suivre l'état du matériel 
- participer aux inventaires 
- consulter les alertes de stock minimum.

Le rôle stock / logistique est central pour assurer la traçabilité du matériel, des consommables et des immobilisations.

---

### 7.8 Maintenance

Responsabilités :

- gérer les équipements 
- suivre les pannes 
- créer ou traiter les ordres de maintenance 
- planifier les interventions 
- suivre la maintenance corrective 
- suivre la maintenance préventive 
- renseigner les rapports d'intervention 
- suivre l'historique de maintenance par équipement 
- suivre les coûts de maintenance si nécessaire.

Le rôle maintenance intervient principalement sur les équipements, véhicules, matériels techniques et interventions.

---

### 7.9 Qualité

Responsabilités :

- gérer les procédures qualité 
- enregistrer les non-conformités 
- suivre les actions correctives 
- suivre les actions préventives 
- gérer les audits internes 
- suivre les réclamations clients 
- consulter les indicateurs qualité 
- assurer le suivi des plans d'action.

Le rôle qualité doit permettre d'assurer la traçabilité des problèmes qualité, des actions décidées et de leur clôture.

---

### 7.10 Finance / Budget

Responsabilités :

- consulter les budgets 
- suivre le prévu/réalisé 
- contrôler certaines dépenses 
- consulter les demandes ayant un impact financier 
- participer à la validation de certaines demandes 
- suivre les écarts budgétaires 
- consulter les exports ou reportings financiers.

Ce rôle intervient principalement sur les aspects budget, dépenses, validations financières et reporting.

---

### 7.11 Employé

Responsabilités :

- se connecter à l'application 
- consulter son espace personnel 
- créer des demandes 
- suivre ses demandes 
- consulter le statut de ses demandes 
- recevoir des notifications 
- consulter certains documents selon ses droits 
- modifier ses informations personnelles si autorisé.

L'employé simple dispose d'un accès limité à ses propres informations et aux processus auxquels il participe.

---

### 7.12 Principes généraux d'accès

Les droits d'accès devront respecter les principes suivants :

- un utilisateur ne voit que les données nécessaires à son rôle 
- un employé voit principalement ses propres demandes 
- un manager peut voir et valider les demandes de son équipe 
- la RH peut accéder aux données RH autorisées 
- la direction peut consulter les données consolidées 
- le stock/logistique peut traiter les demandes liées au matériel, au stock et au carburant 
- les documents sensibles doivent être protégés par des droits spécifiques 
- toutes les validations importantes doivent être tracées 
- les droits doivent pouvoir évoluer sans modifier le code autant que possible.