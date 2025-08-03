# Główny plik main.py
from machine import Pin, I2C
import time
from i2c_lcd import I2cLcd

# ----- KONFIGURACJA -----

przyciski_slownik = {
    "Przycisk POPRZEDNI": Pin(12, Pin.IN, Pin.PULL_UP),
    "Przycisk COFNIJ": Pin(13, Pin.IN, Pin.PULL_UP),
    "Przycisk ZATWIERDZ": Pin(14, Pin.IN, Pin.PULL_UP),
    "Przycisk NASTEPNY": Pin(15, Pin.IN, Pin.PULL_UP),
}

I2C_ADDR = 0x27
I2C_NUM_ROWS = 2 # Liczba wierszy
I2C_NUM_COLS = 16 # Liczba kolumn

# Jeżeli przyciski są podłączone do masy, zostawić, jeżeli są podpięte do zasilania, zmienić na 1
aktywowany = 0

# Inicjalizacja magistrali I2C - piny muszą pasować do podłączenia
i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)

# Inicjalizacja wyświetlacza
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)


# ----- FUNKCJE POMOCNICZE -----

print("Program startuje...")

lcd.clear()
lcd.backlight_on()

def czeka_na_input():
    '''
    Funkcja która sprawdza czy użytkownik zastosował jakikolwiek input
    (wykorzystywane np. przy wyświetleniu wyniku i czekaniu aż użytkownik cokolwiek naciśnie)

    '''
    while True:
        for nazwa_przycisku, obiekt_pin in przyciski_slownik.items():
            if obiekt_pin.value() == aktywowany:
                while obiekt_pin.value() == aktywowany:
                    time.sleep(0.05)
                return 

def wybor_opcji(nazwa_przycisk, liczba_aktualna, pin_obiektu):
    '''
    Funkcja która przyjmuje nazwe przycisku, aktualną liczbę oraz pin obiektu, żeby w prosty sposób zdefiniować zachowanie danego przycisku
    (wykorzystywane np. kiedy chce sie zdefiniować jaką zmienną {liczba_aktualna} ma dany przycisk powiększać, zmniejszać lub zatwierdzać)

    Przyjmuje:
    :nazwa_przycisk: nazwa zdefiniowanego przycisku fizycznego
    :liczba_aktualna: obecne miejsce w którym znajduje się użytkownik na liście opcji menu 
    :pin_obiektu: nazwa zmiennej odpowiedzialnej za przypisanie fizycznego pinu 

    Oddaje:
    :liczba_aktualna: int który określa obecny numer opcji w którym znajduje się użytkownik
    '''
    # Do przodu
    if nazwa_przycisk == "Przycisk NASTEPNY":
        time.sleep(0.2)
        return liczba_aktualna + 1
    
    # Do tyłu
    elif nazwa_przycisk == "Przycisk POPRZEDNI":
        time.sleep(0.2)
        return liczba_aktualna - 1

    # Gdy oddaje None, wtedy jest znak że użytkownik daną opcję zatwierdził                
    elif nazwa_przycisk == "Przycisk ZATWIERDZ":
        while pin_obiektu.value() == 0:
            time.sleep(0.05)
        return None
    
    # Gdy oddaje COFNIJ, to oznacza że użytkownik chce się cofnąć lub coś anulować
    elif nazwa_przycisk == "Przycisk COFNIJ":
        while pin_obiektu.value() == 0:
            time.sleep(0.05)
        return "COFNIJ"

    return liczba_aktualna


def nastepna_opcja(aktualny_indeks, ilosc_opcji):
    '''
    Funkcja wybiera następną opcję z listy krotek zawierające dane działania

    Przyjmuje:
    :aktualny_indeks: int który mówi na której obecnie pozycji jest użytkownik w menu (indeks z listy krotek)
    :ilosc_opcji: int mówiący o tym jak długa jest lista krotek (ile jest opcji dostępnych)
    '''
    return (aktualny_indeks + 1) % ilosc_opcji


def poprzednia_opcja(aktualny_indeks, ilosc_opcji):
    '''
    Funkcja wybiera poprzednią opcję z listy krotek zawierające dane działania 

    Przyjmuje:
    :aktualny_indeks: int który mówi na której obecnie pozycji jest użytkownik w menu (indeks z listy krotek)
    :ilosc_opcji: int mówiący o tym jak długa jest lista krotek (ile jest opcji dostępnych)
    '''
    return (aktualny_indeks - 1) % ilosc_opcji


def wyswietl_menu(opcje_menu, liczba_menu):
    '''
    Funkcja wyświetla dostępne opcje z listy na ekranie LCD

    przyjmuje:
    :opcje_menu: lista stringów dostępnych opcji które są wyświetlane na ekranie
    :liczba_menu: liczba przypisana do zmiennej która odpowiada za obecną pozycję użytkownika w liście
    '''

    lcd.clear() # Czyści ekran
    lcd.putstr("Wybierz opcje:") 

    # Przeszukuje liste opcji i wybiera z nich pierwszy element krotki (samą nazwę)
    nazwa_opcji = opcje_menu[liczba_menu][0] 
    lcd.move_to(0, 1)

    lcd.putstr(f"{nazwa_opcji:<16}") # Wyświetla nazwę opcji  

def dzialania(nazwa_dzialania):
    '''
    Funkcja odpowiadająca za obliczenie wyniku wcześniej sprecyzowanego działania (zmienna 'nazwa_dzialania) dwóch liczb zdefiniowanych przez użytkownika na fizycznym panelu

    Przyjmuje:
    :nazwa_dzialania: ('dodawanie', 'odejmowanie', 'mnozenie', 'dzielenie') odpowiada za dane działanie

    Oddaje: wynik działania dwóch liczb
    '''

    def wybierz_liczbe(tekst):
        '''
        Funkcja która odpowiada za wyświetlenie tekstu oraz obecnie wybranej liczby przez użytkownika w czasie rzeczywistym

        Przyjmuje:
        :tekst: string który ma być pokazany na wyświetlaczu 
        '''

        lcd.clear()
        lcd.putstr(tekst)
        lcd.move_to(0, 1)
        liczba = 0
        lcd.putstr(f"{liczba:<16}")

        while True:
            # Przeszukuje słownik dla nazwy przycisku i odpowiadającego mu pinu 
            for nazwa_przycisku, obiekt_pin in przyciski_slownik.items():

                # Kiedy dowolny przycisk jest wciśnięty
                if obiekt_pin.value() == aktywowany:
                    
                    # Zmienna przechowująca aktualną pozycję użytkownika w menu
                    wynik_operacji = wybor_opcji(nazwa_przycisku, liczba, obiekt_pin)

                    if wynik_operacji is None:
                        return liczba
                    
                    if wynik_operacji == "COFNIJ":
                        return "COFNIJ"
                    
                    else:
                        
                        # Wyświetla obecną opcję 
                        liczba = wynik_operacji
                        lcd.move_to(0, 1)
                        lcd.putstr(f"{liczba:<16}")
                        
    a = None
    b = None

    # Pierwszy krok całej funkcji: wybranie liczby A
    krok = "WYBIERZ_A"

    # Pętla główna która steruje krokami
    while True: 

        if krok == "WYBIERZ_A":
            a = wybierz_liczbe("Liczba a:")

            # Sprawdza czy użytkownik nie wybrał przycisku "COFNIJ"
            if a == "COFNIJ":
                # Jeżeli wybrał, nie ma dokąd się cofnąć, więc wychodzi do menu głównego
                return "COFNIJ_Z_DODAWANIA"

            # Ustawia nową flagę wyboru opcji B (drugi krok)
            krok = "WYBIERZ_B"

        elif krok == "WYBIERZ_B":
            b = wybierz_liczbe("Liczba b:")
            
            # Sprawdza czy użytkownik nie wybrał przycisku "COFNIJ"
            if b == "COFNIJ":
                # Jeżeli wybrał, cofa się do wyboru liczby A
                krok = "WYBIERZ_A"
                continue
            
            # Ustawia nową flagę wyświetlającą wynik (trzeci, ostatni krok)
            krok = "WYSWIETL_WYNIK"

        elif krok == "WYSWIETL_WYNIK":

            # Sprawdza czy zmienna a oraz b to są liczby typu int lub float
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):

                # Sprawdza dla którego działania ma zostać wyświetlony wynik 

                if nazwa_dzialania == 'dodawanie':
                    wynik_ostateczny = a + b

                elif nazwa_dzialania == 'odejmowanie':
                    wynik_ostateczny = a - b

                elif nazwa_dzialania == 'mnozenie':
                    wynik_ostateczny = a * b

                elif nazwa_dzialania == 'dzielenie':
                    wynik_ostateczny = a / b

            # Wyświetla gotowy wynik na ekranie
            lcd.clear()
            lcd.putstr("Wynik to:")
            lcd.move_to(0, 1)
            lcd.putstr(f"{wynik_ostateczny}")

            # Czeka na to aż użytkownik wciśnie dowolny przycisk
            czeka_na_input()
            lcd.clear()

            return wynik_ostateczny


# ----- GŁÓWNA FUNKCJA KALKULATORA -----

def kalkulator():

    # Ta lista przechowuje krotki zawierające nazwę funkcji oraz samą jej definicję, którs dzięki lambdzie nie jest przekazywana
    # programowi jako już gotowe liczby, tylko jako funkcje z podawaną wartością dla każdego działania. Gdyby nie było lambdy, 
    # menu nie działałoby poprawnie.
    opcje_menu = [
        ("Dodawanie", lambda: dzialania('dodawanie')), 
        ("Odejmowanie", lambda: dzialania('odejmowanie')), 
        ("Mnozenie", lambda: dzialania('mnozenie')), 
        ("Dzielenie", lambda: dzialania('dzielenie'))
        ]
    
    # Zmienna przechodująca obecną pozycję użytkownika w menu (obecnie wybraną opcję)
    liczba_menu = 0

    # Zmienna przechowująca obecną nazwę opcji 
    nazwa_opcji = opcje_menu[liczba_menu][0]

    # Zmienna przechowująca listę opcji przy wyborze Tak lub Nie
    lista_tak_nie = ['Tak', 'Nie']

    # Wiadomość powitalna
    lcd.clear()
    lcd.putstr("Witaj w")
    lcd.move_to(0, 1)
    lcd.putstr("kalkulatorze!")
    czeka_na_input()
    lcd.clear()

    # Funkcja wyświetlająca menu
    wyswietl_menu(opcje_menu, liczba_menu)

    while True:

        # Program otrzymuje informacje o tym który przycisk został naciśnięty
        for nazwa_przycisku, obiekt_pin in przyciski_slownik.items():
            if obiekt_pin.value() == aktywowany:

                # Użytkownik chce zobaczyć następną opcję w menu
                if nazwa_przycisku == "Przycisk NASTEPNY":
                    liczba_menu = nastepna_opcja(liczba_menu, len(opcje_menu))

                    nazwa_opcji = opcje_menu[liczba_menu][0]
                    lcd.move_to(0, 1)
                    lcd.putstr(f"{nazwa_opcji:<16}")

                    time.sleep(0.2)

                    break
                
                # Użytkownik chce zobaczyć poprzednią opcję w menu
                elif nazwa_przycisku == "Przycisk POPRZEDNI":
                    liczba_menu = poprzednia_opcja(liczba_menu, len(opcje_menu))
                    
                    nazwa_opcji = opcje_menu[liczba_menu][0]
                    lcd.move_to(0, 1)
                    lcd.putstr(f"{nazwa_opcji:<16}")

                    time.sleep(0.2)

                    break
                    

                # Użytkownik aktywuje obecnie wyświetloną opcję w menu 
                elif nazwa_przycisku == "Przycisk ZATWIERDZ":

                    # Dopóki nie puści przycisku, nic się nie stanie
                    # (zapogiega przypadkowemu zatwierdzeniu jakiejś opcji która jeszcze nie zdążyła się wyświetlić na ekranie)
                    while obiekt_pin.value() == aktywowany:
                        time.sleep(0.05)
                    
                    # Przypisuje do zmiennej funkcję z krotki 
                    funkcja_wywolana = opcje_menu[liczba_menu][1]

                    # Wywołuje tą funkcję
                    funkcja_wywolana()

                    # Po jej wyświetleniu ponownie użytkownik wraca do menu
                    wyswietl_menu(opcje_menu, liczba_menu)

                    # Wyjście z tej pętli zapobiega problemowi StackOverflow
                    break

                elif nazwa_przycisku == "Przycisk COFNIJ":

                    # Patrz linijka 306
                    while obiekt_pin.value() == aktywowany:
                        time.sleep(0.05)

                    # Pyta użytkownika czy na pewno chce wyjść, tworząc podwybór
                    lcd.clear()
                    lcd.move_to(0, 0)
                    lcd.putstr("Chcesz wyjsc?")

                    
                    wybor_wyjscie = 0 # Flaga wyjścia użytkownika
                    lcd.move_to(0, 1)
                    lcd.putstr(f"{lista_tak_nie[wybor_wyjscie]:<16}")
                    

                    while True:
                        opusc_program = False 

                        for nazwa_przycisku, obiekt_pin in przyciski_slownik.items():
                            if obiekt_pin.value() == aktywowany:

                                # Obsługa przycisków 'NASTĘPNY' i 'POPRZEDNI'.
                                # Ponieważ są tylko dwie opcje ('Tak'/'Nie'), oba przyciski działają tak samo - przełączają na drugą opcję.
                                if nazwa_przycisku == "Przycisk NASTEPNY" or nazwa_przycisku == "Przycisk POPRZEDNI":
                                    
                                    # Prosty sposób na przełączanie wartości między 0 a 1 (1-0=1, 1-1=0).
                                    wybor_wyjscie = 1 - wybor_wyjscie

                                    # Pobiera nową nazwę opcji ('Tak' lub 'Nie').
                                    nazwa_opcji = lista_tak_nie[wybor_wyjscie]

                                    lcd.move_to(0, 1)
                                    lcd.putstr(f"{nazwa_opcji:<16}")
                                    
                                    time.sleep(0.2)

                                # Użytkownik nacisnął 'COFNIJ' - chce anulować wyjście i wrócić do menu głównego.
                                elif nazwa_przycisku == "Przycisk COFNIJ":

                                    while obiekt_pin.value() == aktywowany:

                                        time.sleep(0.05)
                                    
                                    # Ponownie wyświetl menu główne, aby "przykryć" okno dialogowe i wrócić do poprzedniego stanu.
                                    wyswietl_menu(opcje_menu, liczba_menu)  

                                    # Ustaw flagę na `True`, aby zewnętrzna pętla `while` wiedziała, że ma się zakończyć.
                                    opusc_program = True

                                    # Przerwij wewnętrzną pętlę `for`, ponieważ akcja została już wykonana.
                                    break                         
                                
                                # Użytkownik nacisnął 'ZATWIERDŹ', aby potwierdzić swój wybór.
                                elif nazwa_przycisku == "Przycisk ZATWIERDZ":

                                    # Sprawdzenie, czy wybraną opcją było 'Tak'.
                                    if lista_tak_nie[wybor_wyjscie] == 'Tak':
                                
                                        while obiekt_pin.value() == aktywowany:
                                            time.sleep(0.05)

                                        # Wyświetl komunikat pożegnalny na konsoli i ekranie LCD.
                                        time.sleep(0.05)
                                        print("Wychodze z kalkulatora...")
                                        lcd.clear()
                                        lcd.putstr("Wychodze z")
                                        lcd.move_to(0, 1)
                                        lcd.putstr("kalkulatora...")

                                        # Czeka 3 sekudny, czyści ekran i wyłącza go
                                        time.sleep(3)
                                        lcd.clear()
                                        lcd.backlight_off()
                                        
                                        
                                        # Instrukcja `return` kończy działanie całej funkcji, w której znajduje się ten kod.
                                        return
                                    
                                    # Jeśli wybrano 'Nie', użytkownik rezygnuje z wyjścia.
                                    else:

                                        while obiekt_pin.value() == aktywowany:
                                            time.sleep(0.05)

                                        # Podobnie jak przy przycisku 'COFNIJ', odśwież menu główne.
                                        wyswietl_menu(opcje_menu, liczba_menu)

                                        # Ustaw flagę, aby wyjść z pętli dialogowej.
                                        opusc_program = True

                                        break
                                    
                        # Sprawdzenie flagi po zakończeniu pętli `for`.
                        # Jeśli flaga `opusc_program` została ustawiona na `True` (przez 'COFNIJ' lub 'ZATWIERDŹ' na 'Nie'),
                        # to przerywamy pętlę `while` tego okna dialogowego i wracamy do pętli menu głównego.
                        if opusc_program:
                            break

# Wywołuje główną funkcję
try:
    # Główna funkcja kalkulatora
    kalkulator()

# W przypadku gdy użytkownik z poziomu klawiatury kończy działanie kodu, wyświetla się stosowny komunikat, a ekran lcd się wyłącza
except KeyboardInterrupt:
    print("\nProgram zakończony przez użytkownika.")
    lcd.clear()
    lcd.backlight_off()