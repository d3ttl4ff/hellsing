import sqlite3

def setup_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('hellsing.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS hosts (
        host_id INTEGER PRIMARY KEY,
        hostname TEXT,
        ip_address TEXT,
        operating_system TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS services (
        service_id INTEGER PRIMARY KEY,
        host_id INTEGER,
        service_name TEXT,
        port INTEGER,
        protocol TEXT,
        FOREIGN KEY(host_id) REFERENCES hosts(host_id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        host_id INTEGER,
        service_id INTEGER,
        product_name TEXT,
        version TEXT,
        FOREIGN KEY(host_id) REFERENCES hosts(host_id),
        FOREIGN KEY(service_id) REFERENCES services(service_id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS credentials (
        credential_id INTEGER PRIMARY KEY,
        host_id INTEGER,
        service_id INTEGER,
        username TEXT,
        password TEXT,
        FOREIGN KEY(host_id) REFERENCES hosts(host_id),
        FOREIGN KEY(service_id) REFERENCES services(service_id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS vulnerabilities (
        vulnerability_id INTEGER PRIMARY KEY,
        host_id INTEGER,
        service_id INTEGER,
        vulnerability_name TEXT,
        description TEXT,
        severity TEXT,
        FOREIGN KEY(host_id) REFERENCES hosts(host_id),
        FOREIGN KEY(service_id) REFERENCES services(service_id)
    )''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Call the function to set up the database and tables
setup_database()
