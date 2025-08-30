# Letzte bearbeitung 30.08
import requests

BASE_URL = "http://127.0.0.1:8000/ask"  # FastAPI Endpoint

# --- Testfälle für Customer ---
customer_queries = [
    "Zeig mir alle Kunden",
    "Wer ist der neueste Kunde?",
    "Welche Kunden wurden in den letzten 30 Tagen hinzugefügt?",
    "Welche Kunden sind in Berlin?",
    "Welcher Kunde hat am meisten gekauft?"
]

# --- Testfälle für Sales ---
sales_queries = [
    "Zeig mir alle Verkäufe",
    "Welcher Verkauf ist der größte?",
    "Zeig mir die letzten 5 Verkäufe",
    "Welcher Kunde hat den letzten Kauf gemacht?",
    "Welche Produkte wurden heute verkauft?",
    "Top 3 Produkte nach Menge verkauft",
    "Zeig mir alle Verkäufe von Kunden aus 'Munich'"
]

# --- Testfälle für Product ---
product_queries = [
    "Zeig mir alle Produkte",
    "Welches ist das neueste Produkt?",
    "Welche Produkte sind teurer als 100 €?",
    "Top 3 beliebtesten Produkte",
    "Welche Produkte gehören zur Kategorie 'Laptops'?",
    "Zeig mir Produkte, die weniger als 10 Stück auf Lager haben"
]

# --- Testfälle für Employee ---
employee_queries = [
    "Zeig mir alle Mitarbeiter",
    "Wer ist der neueste Mitarbeiter?",
    "Welche Mitarbeiter arbeiten in Region 'Berlin'?",
    "Wer wurde zuerst eingestellt?",
    "Wer hat am meisten Verkäufe betreut?"
]

# Zusammenfassung aller Tests
all_tests = [
    ("Customer", customer_queries),
    ("Sales", sales_queries),
    ("Product", product_queries),
    ("Employee", employee_queries)
]

def run_tests():
    for category, queries in all_tests:
        print(f"\n=== TESTS: {category} ===")
        for query in queries:
            print(f"\n📌 Query: {query}")
            try:
                response = requests.post(BASE_URL, json={"query": query})
                try:
                    data = response.json()
                except ValueError:
                    print("❌ Fehler: Antwort war kein gültiges JSON")
                    print("Antwort:", response.text)
                    continue

                if response.status_code == 200 and "query" in data:
                    print("✅ SQL:", data.get("query"))
                    print("📊 Result HTML:")
                    print(data.get("results_html"))
                else:
                    print("❌ Fehler:", data.get("detail", "Unbekannter Fehler"))
            except requests.exceptions.RequestException as e:
                print("❌ Fehler bei der Anfrage:", e)

if __name__ == "__main__":
    run_tests()
