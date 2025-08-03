# manualny-kalkulator
Prosty kalkulator napisany w MicroPythonie wykorzystujący 4 przyciski oraz ekran LCD przy pomocy Raspberry Pi Pico 2.

Żeby kalkulator zadziałał, należy podłączyć 4 fizyczne przyciski do Pico oraz ekran LCD.

Dany przycisk na PIN'ie odpowiada:
- Pin 12: Przycisk POPRZEDNI,
- Pin 13: Przycisk COFNIJ,
- Pin 14: Przycisk ZATWIERDŹ,
- Pin 15: Przycisk NASTĘPNY.

Należy je podłączyć do odpowiadających im pinów (można to naturalnie zmienić w kodzie).

Kod jest pisany pod magistralę I2C ekranu LCD gdzie piny trzeba podłączyć:
- Pin 16: SDA,
- Pin 17: SCL.

Podczas pisania kodu skorzystałem z repozytorium które ułatwia konfigurację ekranu LCD:
https://github.com/T-622/RPI-PICO-I2C-LCD
