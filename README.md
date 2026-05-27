# Swiss Weather & Air Quality Analyzer

Dieses Projekt analysiert automatisiert Wetter- und Luftqualitätsdaten für 7 Schweizer Städte, basierend auf:

- Täglichen Temperaturdaten (Mittel, Max, Min)
- PM2.5 Feinstaubwerten und europäischem Luftqualitätsindex (AQI)
- Niederschlag und Windgeschwindigkeit
- Statistischer Korrelationsanalyse (Pearson + T-Test)
- KI-generierten wissenschaftlichen Erkenntnissen via Claude API
- Interaktiver Kartenvisualisierung mit Folium
- Lokaler SQLite-Datenbank zur Datenspeicherung
- Flask Web-App zur Ergebnispräsentation

---

## Features

- Automatischer Datenabruf über die kostenlose Open-Meteo API (kein API-Key nötig)
- Objektorientierte Architektur mit `WeatherAnalyzer` Klasse
- Datenbereinigung mit regulären Ausdrücken
- Saisonale und städtebasierte Analyse mit pandas
- Statistische Analyse mit scipy (Pearson-Korrelation + T-Test mit p-Wert)
- 4-Panel-Grafik, Heatmap und Regressions-Plot
- Interaktive Folium-Karte mit Luftqualitätsampel
- SQLite-Datenbank mit SQL-Abfragen
- KI-Analyse via Anthropic Claude API
- Flask Web-Dashboard zur Ergebnispräsentation

---

##  Schritt-für-Schritt-Anleitung

### 1. Repository klonen
```bash
git clone https://github.com/cin614/swiss-weather-air-quality.git
cd swiss-weather-air-quality
```

### 2. Anforderungen installieren
```bash
pip install -r requirements.txt
```

### 3. Jupyter Notebook ausführen
```bash
jupyter notebook swiss_weather_analysis.ipynb
```
Dann im Menü: **Cell → Run All**

Das Notebook führt automatisch alle Schritte aus:
- Wetter- und Luftqualitätsdaten für 7 Städte abrufen
- Daten bereinigen und in SQLite speichern
- Visualisierungen erstellen und speichern
- Statistische Analyse durchführen
- KI-Erkenntnisse via Claude API generieren

### 4. (Optional) Claude API-Key für KI-Analyse setzen

Den API-Key erhältst du unter: https://console.anthropic.com

In Zelle 12 des Notebooks eintragen:
```python
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."
```

### 5. Flask Web-App starten
```bash
python app.py
```
Anschliessend im Browser öffnen: **http://localhost:5000**

---

## Projektstruktur

```
├── swiss_weather_analysis.ipynb   ← Haupt-Jupyter-Notebook
├── app.py                         ← Flask Web-App
├── requirements.txt               ← Python-Abhängigkeiten
├── README.md                      ← Diese Datei
├── .gitignore                     ← Grosse Dateien ausgeschlossen
├── swiss_weather.db               ← SQLite-Datenbank (wird automatisch erstellt)
├── visualizations.png             ← 4-Panel-Grafik (wird automatisch erstellt)
├── heatmap.png                    ← Korrelations-Heatmap (wird automatisch erstellt)
├── regression_plot.png            ← Regressions-Plot (wird automatisch erstellt)
└── swiss_air_quality_map.html     ← Interaktive Karte (wird automatisch erstellt)
```

---

## Ergebnisse

| Kennzahl | Wert |
|----------|------|
| Analysezeitraum | Januar – Dezember 2024 |
| Anzahl Datenpunkte | 2'562 tägliche Einträge |
| Städte | Zürich, Bern, Genf, Basel, Lausanne, St. Gallen, Luzern |
| Pearson r (Temp. vs. PM2.5) | −0.281 |
| p-Wert | 8.9 × 10⁻⁴⁸ (hochsignifikant) |
| Durchschnittliches PM2.5 | 8.22 µg/m³ |
| WHO-Jahresgrenzwert | 15.00 µg/m³ |
| Schmutzigste Stadt | Basel (9.78 µg/m³) |
| Sauberste Stadt | Lausanne (7.29 µg/m³) |

---

## Verwendete Technologien

| Technologie | Zweck |
|-------------|-------|
| `pandas` | Datenverarbeitung und DataFrames |
| `numpy` | Numerische Berechnungen |
| `matplotlib` / `seaborn` | Datenvisualisierung |
| `scipy` | Statistische Analyse |
| `folium` | Interaktive Karte |
| `sqlite3` | Lokale Datenbank |
| `requests` | API-Aufrufe |
| `re` | Reguläre Ausdrücke |
| `anthropic` | Claude LLM API |
| `flask` | Web-App |

---

## Abgedeckte Modulanforderungen

### Pflichtpunkte (8/8)
| # | Anforderung | Umsetzung |
|---|-------------|-----------|
| 1 | Reale Datenerhebung | Open-Meteo API, 2 Endpunkte |
| 2 | Datenaufbereitung mit Regex | `prepare_data()` — Datumsextraktion |
| 3 | Listen, Dicts, Sets, Tuples, DataFrames | Stadtdefinitionen + pandas |
| 4 | Conditionals & Loops | Saisonzuweisung, Stadtiteration |
| 5 | OOP | `WeatherAnalyzer` Klasse |
| 6 | Tabellen & Visualisierungen | 4 Grafiken, Heatmap, Karte |
| 7 | Statistik + p-Wert | Pearson + T-Test (scipy) |
| 8 | Moodle-Abgabe | ZIP-Datei |

### Bonuspunkte (5/6)
| # | Bonus | Umsetzung |
|---|-------|-----------|
| ✅ | Web API | Open-Meteo (Wetter + Luftqualität) |
| ✅ | SQLite Datenbank | `save_to_sqlite()` + SQL-Abfragen |
| ✅ | LLM Integration | Claude API in Zelle 12 |
| ✅ | Web-App | Flask Dashboard (`app.py`) |
| ✅ | GitHub Repository | Öffentliches Repo mit `.gitignore` |

---

## 👥 Autoren

**Cindy Sommer** · **Andrea Brunetto**  
Scientific Programming – FS2026 · ZHAW School of Management and Law
