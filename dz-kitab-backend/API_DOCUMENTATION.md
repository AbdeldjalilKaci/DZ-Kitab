# DZ-Kitab API Documentation

## Table des matières
- [Annonces](#annonces)
- [Recherche](#recherche)
- [Favoris](#favoris)
- [Messages](#messages)
- [Checkout](#checkout)
- [Badges / Recommandations](#badges--recommandations)

---

## Annonces

### Liste des annonces
- **Méthode :** GET
- **Endpoint :** `/annonces/`
- **Permissions :** Public
- **Description :** Liste toutes les annonces
- **Query params (optionnel) :**
  - `title` → filtrer par titre
  - `author` → filtrer par auteur

### Créer une annonce
- **Méthode :** POST
- **Endpoint :** `/annonces/`
- **Permissions :** Authenticated
- **Body :**
```json
{
  "title": "Nom du livre",
  "author": "Auteur",
  "price": 50.0,
  "image": "URL ou fichier",
  "category": "Informatique",
  "market_price": 60.0,
  "final_calculated_price": 55.0,
  "page_count": 300,
  "publication_date": "2024-01-01"
}
Détail d'une annonce
Méthode : GET

Endpoint : /annonces/{id}/

Mettre à jour une annonce
Méthode : PUT / PATCH

Endpoint : /annonces/{id}/

Supprimer une annonce
Méthode : DELETE

Endpoint : /annonces/{id}/

Recherche
Recherche avancée
Méthode : GET

Endpoint : /announcements/search/

Query params : price, created_at, book__published_date, etc.

Recherche basique
Méthode : GET

Endpoint : /announcements/search/basic/

Query params : title, author

Favoris
Ajouter un favori
Méthode : POST

Endpoint : /favorites/

Body :

json
Copier le code
{
  "user_id": 1,
  "announcement_id": 5
}
Supprimer un favori
Méthode : DELETE

Endpoint : /favorites/{id}/

Messages
Envoyer un message
Méthode : POST

Endpoint : /messages/

Liste des conversations
Méthode : GET

Endpoint : /messages/conversations/

Messages d'une annonce
Méthode : GET

Endpoint : /messages/{announcement_id}/

Checkout
Créer une commande
Méthode : POST

Endpoint : /checkout/

Body :

json
Copier le code
{
  "user_id": 1,
  "items": [
    {"announcement_id": 5, "quantity": 1},
    {"announcement_id": 7, "quantity": 2}
  ]
}
Réponse :

json
Copier le code
{
  "id": 1,
  "user_id": 1,
  "total_price": 125.0,
  "status": "Pending",
  "created_at": "2026-01-14T08:00:00Z",
  "items": [
    {"announcement_id": 5, "quantity": 1, "price": 50.0},
    {"announcement_id": 7, "quantity": 2, "price": 75.0}
  ]
}
Badges / Recommandations
Méthodes : À définir selon votre système de recommandation

Endpoints : À compléter

Description : Système de badges pour utilisateurs et recommandations personnalisées.
