import sqlite3
from bs4 import BeautifulSoup
import re

def clean_price(text):
    # Removes ₹ and extra spaces
    return float(re.sub(r'[^\d.]', '', text))

def import_menu():
    try:
        # This looks for your menu.html file
        with open('menu.html', 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        items_to_add = []
        sections = soup.find_all('div', class_='section')

        for section in sections:
            rows = section.find_all('div', class_='menu-row')
            for row in rows:
                spans = row.find_all('span')
                item_name = spans[0].text.strip()
                prices = row.find_all('span', class_='price')

                if len(prices) == 2:
                    veg_p = clean_price(prices[0].text)
                    nv_p = clean_price(prices[1].text)
                    items_to_add.append((f"{item_name} (Veg)", veg_p))
                    items_to_add.append((f"{item_name} (Non-Veg)", nv_p))
                elif len(prices) == 1:
                    p = clean_price(prices[0].text)
                    items_to_add.append((item_name, p))

        conn = sqlite3.connect('cafe.db')
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS menu")
        cursor.execute("CREATE TABLE menu (id INTEGER PRIMARY KEY, name TEXT, price REAL)")
        cursor.executemany("INSERT INTO menu (name, price) VALUES (?, ?)", items_to_add)
        conn.commit()
        conn.close()
        print(f"✅ Success! Imported {len(items_to_add)} items.")

    except FileNotFoundError:
        print("❌ Error: 'menu.html' not found in this folder!")

if __name__ == "__main__":
    import_menu()