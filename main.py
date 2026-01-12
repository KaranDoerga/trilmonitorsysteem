from machine import Pin, PWM
import time

# --- Pin Definities ---
TILT_PIN = 17
LED_G = 1       
LED_O = 41      
LED_R = 42      
SERVO_PIN = 13
RESET_PIN = 14

# --- Initialisatie ---
tilt_sensor = Pin(TILT_PIN, Pin.IN, Pin.PULL_UP)
reset_button = Pin(RESET_PIN, Pin.IN, Pin.PULL_UP)
led_veilig = Pin(LED_G, Pin.OUT)
led_risico = Pin(LED_O, Pin.OUT)
led_gevaar = Pin(LED_R, Pin.OUT)

# Servo setup
servo = PWM(Pin(SERVO_PIN), freq=50)

def set_slagboom(dicht):
    # Dicht (90 graden) of Open (0 graden)
    angle = 90 if dicht else 0
    duty = int(((angle / 180) * 2 + 0.5) / 20 * 1023)
    servo.duty(duty)

# Variabelen voor logica
huidige_status = "VEILIG"
start_trilling = 0
is_trillend = False
laatste_update = time.ticks_ms()

print("Trilmonitorsysteem gestart op GPIO 17, 41, 42...")

while True:
    nu = time.ticks_ms()
    
    if time.ticks_diff(nu, laatste_update) >= 5000:
        print(f"Status Update: {huidige_status}")
        laatste_update = nu

    if huidige_status == "GEVAAR":
        led_gevaar.value(1)
        led_veilig.value(0)
        led_risico.value(0)
        set_slagboom(True) # Slagboom dicht
        
        if reset_button.value() == 0: # Knop ingedrukt
            huidige_status = "VEILIG"
            print("Systeem gereset door onderhoudspersoneel.")
            time.sleep(0.5)
    else:
        if tilt_sensor.value() == 0: # Sensor detecteert beweging
            if not is_trillend:
                start_trilling = nu
                is_trillend = True
            
            duur = time.ticks_diff(nu, start_trilling)
            
            if duur > 5000:
                huidige_status = "GEVAAR"
            elif duur > 3000:
                huidige_status = "RISICO"
        else:
            is_trillend = False
            if huidige_status != "GEVAAR":
                huidige_status = "VEILIG"

        # Update LEDs en Slagboom voor Veilig/Risico
        led_veilig.value(huidige_status == "VEILIG")
        led_risico.value(huidige_status == "RISICO")
        led_gevaar.value(0)
        set_slagboom(False) # Open houden bij Veilig/Risico

    time.sleep(0.01) # Stabiliteit