import re
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\\Users\\user\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'


def popraw_jakosc_obrazu(img):
    img = img.convert('L')  # Konwersja do odcieni szarości
    img = img.filter(ImageFilter.SHARPEN)  # Wyostrzenie obrazu
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)  # Zwiększenie kontrastu
    return img


def wyodrebnij_tekst(img):
    try:
        tekst = pytesseract.image_to_string(img, lang='pol')
    except pytesseract.TesseractError as e:
        print(f"Błąd Tesseract OCR: {e}")
        return ""
    return tekst


def znajdz_polaczenia(tekst):
    wzorce = [
        re.compile(r'-?\s*(F\d+)\s*:\s*(\d+).*?\|\s*([^\s|]+)', re.IGNORECASE),  # wzorzec dla F
        re.compile(r'(\d+)\s*\/?\s*(PS\d+-X\d)\s*:\s*(\d+)', re.IGNORECASE),  # wzorzec dla PS-X
        re.compile(r'(PS\d+)\s*:\s*(\d+)\s*\|\s*(\d+)', re.IGNORECASE),  # wzorzec dla PS
        re.compile(r'(\d+)\s*\/?\s*(K\d+)\s*:\s*(\d+)', re.IGNORECASE),  # wzorzec dla K
        re.compile(r'(\d+)\s*\/?\s*(SCU\d+-X\d)\s*:\s*(\d+)', re.IGNORECASE),  # wzorzec dla SCU
        re.compile(r'(\d+)\s*\/?\s*(U\d+)\s*:\s*(\d+)', re.IGNORECASE)  # wzorzec dla U
    ]

    polaczenia = {
        'F': [],
        'K': [],
        'U': [],
        'PS': [],
        'PS-X': [],
        'SCU': []
    }

    for wzorzec in wzorce:
        print(f"Używany wzorzec: {wzorzec.pattern}")
        for dopasowanie in re.findall(wzorzec, tekst):
            print(f"Znaleziono dopasowanie: {dopasowanie}")
            if len(dopasowanie) == 3:
                if re.match(r'PS\d+-X\d', dopasowanie[1]):  # poprawna walidacja na format PS-X
                    kategoria = 'PS-X'
                    polaczenie = f"{dopasowanie[0].strip()}/{dopasowanie[1].strip()}:{dopasowanie[2].strip()}"
                elif re.match(r'PS\d+', dopasowanie[1]):
                    kategoria = 'PS'
                    polaczenie = f"{dopasowanie[1].strip()}:{dopasowanie[2].strip()}|{dopasowanie[0].strip()}"
                elif re.match(r'SCU\d+-X\d', dopasowanie[1]):
                    kategoria = 'SCU'
                    polaczenie = f"{dopasowanie[0].strip()}/{dopasowanie[1].strip()}:{dopasowanie[2].strip()}"
                elif re.match(r'F\d+', dopasowanie[0]):
                    kategoria = 'F'
                    polaczenie = f"{dopasowanie[0].strip()}:{dopasowanie[1].strip()}|{dopasowanie[2].strip()}"
                else:
                    kategoria = dopasowanie[1][0].upper()
                    polaczenie = f"{dopasowanie[0].strip()}/{dopasowanie[1].strip()}:{dopasowanie[2].strip()}"

                if kategoria in polaczenia:
                    polaczenia[kategoria].append(polaczenie)

    return polaczenia


def wyodrebnij_polaczenia_kabli(sciezka_do_obrazu):
    try:
        img = Image.open(sciezka_do_obrazu)
    except IOError as e:
        print(f"Błąd otwierania pliku: {e}")
        return {}

    img = popraw_jakosc_obrazu(img)
    tekst = wyodrebnij_tekst(img)

    print("Wyodrębniony tekst:")
    print(tekst)

    return znajdz_polaczenia(tekst)


if __name__ == "__main__":
    sciezka_do_obrazu = r"C:\\Users\\user\\Desktop\\testObraz.png"
    polaczenia = wyodrebnij_polaczenia_kabli(sciezka_do_obrazu)

    if polaczenia:
        for rodzaj, lista_polaczen in polaczenia.items():
            if lista_polaczen:
                print(f"\nPołączenia dla rodzaju {rodzaj}:")
                for idx, polaczenie in enumerate(lista_polaczen, start=1):
                    print(f"Połączenie nr {idx}: {polaczenie}")
    else:
        print("Nie znaleziono połączeń.")
