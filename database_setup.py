import sqlite3

def setup():
    conn = sqlite3.connect('cafe.db')
    cursor = conn.cursor()
    
    # Create Menu Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS menu 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       name TEXT NOT NULL, 
                       price REAL NOT NULL)''')
    
    # Pre-fill with some items if the table is empty
    cursor.execute("SELECT COUNT(*) FROM menu")
    if cursor.fetchone()[0] == 0:
        menu_items = [
            ('Coffee', 50.0),
            ('Tea', 30.0),
            ('Sandwich', 120.0),
            ('Cake', 150.0),
            ('Burger', 100.0)
        ]
        cursor.executemany("INSERT INTO menu (name, price) VALUES (?, ?)", menu_items)
        print("Menu initialized with default items.")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup()