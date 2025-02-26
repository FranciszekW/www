# Zadanie

# W tym zadaniu masz napisać program, który przygotuje statyczną witrynę internetową i wystawi ją “w internecie”.

# Precyzyjniej:

#     Należy napisać program, który ściągnie stronę internetową poświęconą jakiemuś wybranemu przez siebie tematowi, na przykład:
#         TikTokerom (https://www.favikon.com/blog/the-20-most-famous-tiktok-influencers-in-the-world)
#         językom programowania (https://www.tiobe.com/tiobe-index/)
#         otwarciom szachowym (https://www.thechesswebsite.com/chess-openings/) ważna informacja: strona ta powinna zawierać listę elementów, które można łatwo zescrapować (np. lista języków programowania, lista otwarć szachowych, lista tiktokowych influencerów), lista ta może być w formie tabeli, listy, itp.
#     Program ten powinien przetworzyć stronę internetową i wygenerować z niej plik w formacie markdown, który będzie zawierał listę elementów zescrapowanych z internetu wraz z jakimiś dodatkowymi informacjami (np. opis, link, obrazek, itp.)
#     Następnie należy (przy użyciu biblioteki w rodzaju https://github.com/MarioVilas/googlesearch, https://github.com/deedy5/duckduckgo_search) wyszukać w internecie dodatkowe informacje na temat każdego z elementów zescrapowanych z internetu.
#     Następnie należy przygotować witrynę internetową w formacie markdown, która będzie zawierała stronę statyczną, obrazki, dane zescrapowane z internetu (patrz punkt 2) i inne informacje, które uważasz za istotne.

# Witryna internetowa

# Witryna powinna zawierać

#     co najmniej jedną stronę statyczną opisującą wybrany przez Ciebie temat
#     listę zescrapowaną z internetu
#     podstronę dla każdej z pozycji


# Stworzymy stronę z listą 10 najbardziej doświadczonych kierowców F1. https://pl.wikipedia.org/wiki/Lista_kierowc%C3%B3w_Formu%C5%82y_1

# Na początek pobieramy dane z użyciem biblioteki BeautifulSoup
from bs4 import BeautifulSoup
import requests

url = 'https://pl.wikipedia.org/wiki/Lista_kierowc%C3%B3w_Formu%C5%82y_1'
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')
# Print top 1000 lines of the soup
# print(soup.prettify()[:50000])

# Znajdujemy tabelę z listą kierowców
table = soup.find('table', class_='wikitable sortable')
# print(table)

# Znajdujemy wiersze tabeli
rows = table.find_all('tr')
# print(rows[1])

# Teraz z każdego wiersza wyciągamy imię i nazwisko kierowcy, link do strony wikipedii oraz liczbę startów,
# która jest szóstą kolumną w tabeli
drivers = []
for row in rows[1:11]:
    driver = {}
    driver['name'] = row.find('a').get_text()
    # Po kliknieciu w link ma być przeniesienie do pliku markdown z dodatkowymi informacjami
    driver['link'] = 'https://pl.wikipedia.org' + row.find('a')['href']
    driver['starts'] = row.find_all('td')[5].get_text()
    driver['subpage'] = f"drivers/{driver['name']}.md"
    drivers.append(driver)

# print(drivers[:10])
# print(len(drivers))

# Sortujemy kierowców po liczbie startów
drivers = sorted(drivers, key=lambda x: int(x['starts']), reverse=True)

# Teraz zapisujemy dane do pliku markdown
with open('index.md', 'w', encoding='utf-8') as file:
    file.write('# Najbardziej doświadczeni kierowcy F1\n\n')
    for driver in drivers:
        file.write(f"## {driver['name']}\n")
        file.write(f"Starty: {driver['starts']}\n")
        file.write(f"[Podstrona]({driver['subpage']})\n\n")

# Teraz wyszukujemy dodatkowych informacji o kierowcach, pełne imię i nazwisko, narodowość, datę urodzenia.
from googlesearch import search
import re

# Teraz robimy to samo co na górze, ale dla każdego kierowcy
for driver in drivers:
    print(f"Processing driver {driver['name']}")
    query = f"{driver['name']} polska wikipedia"
    for j in search(query, num=1, stop=1, pause=2):
        # Używamy ten url do pobrania opisu
        desc_page = requests.get(j)
        desc_soup = BeautifulSoup(desc_page.content, 'html.parser')
        # Bierzemy wszystko co znajduje się pod tagiem <table class="infobox">
        infobox = desc_soup.find('table', class_='infobox')
        # Funkcja, która wyciąga wartość z infoboxu
        def get_infobox_value(infobox, field_pattern):
            row = infobox.find('th', string=re.compile(field_pattern, re.IGNORECASE))
            if row:
                td = row.find_next_sibling('td')
                return td.get_text(strip=True, separator=" ") if td else None
            return None
        # Wyciągamy dane
        full_name = get_infobox_value(infobox, r"imię.*nazwisko")
        birth = get_infobox_value(infobox, r"data.*urodzenia")
        current_starting_nr = get_infobox_value(infobox, r"nr.*startowy")
        # for a_tag in infobox.find_all('a'):
        #     print(a_tag)
        country_tr = infobox.find('a', title='Państwo').find_parent('tr')
        country = country_tr.find('td').get_text(strip=True)
        # Zapisujemy dane
        driver['full_name'] = full_name if full_name else driver['name']
        driver['birth'] = birth
        driver['country'] = country
        driver['current_starting_nr'] = current_starting_nr if current_starting_nr else "Kierowca już nie startuje"

# Save the drivers dataframe to a csv file
import csv
with open('drivers.csv', 'w', encoding='utf-8', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=drivers[0].keys())
    writer.writeheader()
    writer.writerows(drivers)

# Now for each driver we create a separate markdown file with additional information
for driver in drivers:
    with open(f"drivers/{driver['name']}.md", 'w', encoding='utf-8') as file:
        file.write(f"# {driver['full_name']}\n\n")
        file.write(f"+ Narodowość: {driver['country']}\n\n")
        file.write(f"+ Data i miejsce urodzenia: {driver['birth']}\n\n")
        file.write(f"+ Obecny numer startowy: {driver['current_starting_nr']}\n\n")
        file.write(f"[Więcej informacji]({driver['link']})\n\n")