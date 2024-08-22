
# Logsys API Documentatie

## Belangrijke Afhankelijkheden
Dit project maakt gebruik van de volgende belangrijke afhankelijkheden:
- SQLite
- Flask-CORS
- Werkzeug
- PyJWT

Zorg ervoor dat deze afhankelijkheden correct zijn geïnstalleerd en draaien. Voeg meldingen toe om te waarschuwen als een van deze afhankelijkheden niet werkt.

## Inhoudsopgave
1. [Inleiding](#inleiding)
2. [Installatie](#installatie)
3. [API Endpoints](#api-endpoints)
    - [Login](#login)
    - [Gebruikers ophalen](#gebruikers-ophalen)
    - [Gebruiker toevoegen](#gebruiker-toevoegen)
    - [Gebruiker bewerken](#gebruiker-bewerken)
    - [Gebruiker verwijderen](#gebruiker-verwijderen)

## Inleiding
Dit project bevat een eenvoudige API voor gebruikersbeheer met behulp van Flask en JWT-authenticatie.

## Installatie
1. Installeer de vereiste Python-pakketten:
    ```bash
    pip install -r requirements.txt
    ```

2. Start de server:
    ```bash
    python app.py
    ```

## API Endpoints

### Login
- **URL**: `/login`
- **Methode**: `POST`
- **Beschrijving**: Authenticeer een gebruiker en verkrijg een JWT-token.
- **Request Body**:
    ```json
    {
        "username": "string",
        "password": "string"
    }
    ```
- **Response**:
    ```json
    {
        "token": "string"
    }
    ```

### Gebruikers ophalen
- **URL**: `/users`
- **Methode**: `GET`
- **Beschrijving**: Haal de lijst van gebruikers op. Vereist een geldige JWT-token.
- **Headers**:
    ```json
    {
        "x-access-tokens": "string"
    }
    ```
- **Response**:
    ```json
    [
        [id, email, username, status]
    ]
    ```

### Gebruiker toevoegen
- **URL**: `/add_user`
- **Methode**: `POST`
- **Beschrijving**: Voeg een nieuwe gebruiker toe. Vereist een geldige JWT-token.
- **Request Body**:
    ```json
    {
        "username": "string",
        "password": "string"
    }
    ```
- **Response**:
    ```json
    {
        "message": "User added successfully"
    }
    ```

### Gebruiker bewerken
- **URL**: `/edit_user`
- **Methode**: `PUT`
- **Beschrijving**: Bewerk een bestaande gebruiker. Vereist een geldige JWT-token.
- **Request Body**:
    ```json
    {
        "id": "integer",
        "username": "string",
        "password": "string"
    }
    ```
- **Response**:
    ```json
    {
        "message": "User updated successfully"
    }
    ```

### Gebruiker verwijderen
- **URL**: `/delete_user`
- **Methode**: `DELETE`
- **Beschrijving**: Verwijder een gebruiker. Vereist een geldige JWT-token.
- **Request Body**:
    ```json
    {
        "id": "integer"
    }
    ```
- **Response**:
    ```json
    {
        "message": "User deleted successfully"
    }
    ```

