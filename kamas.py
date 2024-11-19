import RPi.GPIO as GPIO
from time import sleep
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import uvicorn
import threading  # Pour exécuter la détection en parallèle

# Initialisation des GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(YOUR_PIN, GPIO.IN)
GPIO.setup(YOUR_PIN, GPIO.OUT)
buzz = GPIO.PWM(YOUR_PIN, 100 ) #You can adjust the frenquency that as you wish

# Initialisation de l'application FastAPI
app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index():
    return templates.TemplateResponse("index.html", {"request": {}})


@app.get("/gas-status", response_class=JSONResponse)
async def gas_status():
    gas_detected = GPIO.input(YOUR_PIN) == GPIO.HIGH
    return {"gas_detected": gas_detected}


# Fonction pour surveiller en permanence la détection de gaz
def gas_detection_loop():
    try:
        while True:
            gas_detected = GPIO.input(YOUR_PIN) == GPIO.HIGH
            if gas_detected:
                buzz.start(1)
                print("-------------------------------------------")
                print(f"Valeur de sortie du MQ2 : {GPIO.input(YOUR_PIN)}")
                print("Un gaz a été détecté dans la pièce.")
                print("L'alarme a été activé.")
                print("-------------------------------------------")
            else:
                buzz.stop()
                print("-------------------------------------------")
                print(f"Valeur de sortie du MQ2 : {GPIO.input(YOUR_PIN)}")
                print("Pas de gaz détecté")
                print("L'alarme est désactivé.")
                print("-------------------------------------------")
            sleep(1)  # Vérifie toutes les secondes
    except KeyboardInterrupt:
        print("Arrêt de la détection de gaz.")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    # Démarrer la boucle de détection dans un thread séparé
    detection_thread = threading.Thread(target=gas_detection_loop, daemon=True)
    detection_thread.start()

    # Démarrer le serveur web FastAPI
    uvicorn.run(app, host="0.0.0.0", port=8000)

