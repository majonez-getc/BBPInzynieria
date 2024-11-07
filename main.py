import re
import fitz
import io
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\user\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
#zmienic zeby bral jedynie czesc obrazu a nie dokument
def wyodrebnij_polaczenia_kabli(sciezka_do_pdf, strona_poczatkowa=None, strona_koncowa=None):
    polaczenia = []
    dokument = fitz.open(sciezka_do_pdf)

    strona_poczatkowa = strona_poczatkowa or 0
    strona_koncowa = strona_koncowa or len(dokument)

    wzorzec_polaczenia = re.compile(r'([A-Z]+\d+)\s*:\s*(\d+)\s+(\d+)\s+([A-Z]+\d+-X\d+)\s*:\s*(\d+)')

    licznik = 0
    while not polaczenia and licznik < 10:
        for numer_strony in range(strona_poczatkowa, strona_koncowa):
            strona = dokument[numer_strony]

            pixmap = strona.get_pixmap()

            img = Image.open(io.BytesIO(pixmap.tobytes()))

            tekst = pytesseract.image_to_string(img, lang='pol')


            for dopasowanie in re.findall(wzorzec_polaczenia, tekst):
                polaczenia.append(f"{dopasowanie[0]}:{dopasowanie[1]}/{dopasowanie[2]}/{dopasowanie[3]}:{dopasowanie[4]}")
        licznik += 1
    print(tekst)
    return polaczenia


if __name__ == "__main__":
    plik_pdf = r"C:\Users\user\Desktop\Szkolenie SSiN\Wysoka Głogowska\dtrWysoka.pdf"
    polaczenia = wyodrebnij_polaczenia_kabli(plik_pdf, strona_poczatkowa=54, strona_koncowa=55)

    if polaczenia:
        for polaczenie in polaczenia:
            print(f"Połączenie: {polaczenie}")
    else:
        print("Nie znaleziono połączeń.")