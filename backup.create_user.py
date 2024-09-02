
import sqlite3
from werkzeug.security import generate_password_hash

# Verbinden met de database
conn = sqlite3.connect('Logsys/users.db')
cursor = conn.cursor()

# Gebruikersgegevens
username = 'admin'
password = 'admin123'

# Wachtwoord hashen
hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

# Gebruiker toevoegen aan de database
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
conn.commit()

# Sluiten van de verbinding
conn.close()

print(f"Gebruiker '{username}' is aangemaakt.")
