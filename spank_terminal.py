import os
import time
import math
import random
import argparse
import pygame
from winsdk.windows.devices.sensors import Accelerometer

# --- GESTION DES COMMANDES DU TERMINAL ---
parser = argparse.ArgumentParser(description="Spank (Version Surface)")
parser.add_argument("--sexy", action="store_true", help="Activer le mode sexy")
parser.add_argument("--halo", action="store_true", help="Activer le mode halo")
args = parser.parse_args()

# --- SÉLECTION DU DOSSIER ---
if args.sexy:
    DOSSIER_AUDIO = "audio/sexy"
elif args.halo:
    DOSSIER_AUDIO = "audio/halo"
else:
    DOSSIER_AUDIO = "audio/pain"  # Mode normal par défaut

# --- PARAMÈTRES ---
SEUIL_FORCE = 1.5  # Sensibilité (1.0 = gravité normale).
COOLDOWN = 0.75  # Temps d'attente entre deux sons (en secondes)

# 1. Initialisation du moteur audio
pygame.mixer.init()

# 2. Chargement de la liste des fichiers audio
fichiers_sons = []
if os.path.exists(DOSSIER_AUDIO):
    for fichier in os.listdir(DOSSIER_AUDIO):
        if fichier.endswith(".mp3"):
            fichiers_sons.append(os.path.join(DOSSIER_AUDIO, fichier))

if not fichiers_sons:
    print(f"Erreur : Aucun fichier .mp3 trouvé dans le dossier '{DOSSIER_AUDIO}'.")
    exit(1)

# 3. Récupération de l'accéléromètre de la Surface
accel = Accelerometer.get_default()

if not accel:
    print("Aucun accéléromètre détecté sur cet appareil Windows.")
    exit(1)

print(f"Spank (Version Surface) démarré en mode '{DOSSIER_AUDIO}' !")
print(f"{len(fichiers_sons)} sons chargés. En attente d'une tape... (Ctrl+C pour quitter)")

dernier_choc = 0.0


# 4. Fonction déclenchée à chaque mouvement
def on_reading_changed(sender, args):
    global dernier_choc
    reading = args.reading

    # Calculer la force G totale
    force = math.sqrt(reading.acceleration_x ** 2 + reading.acceleration_y ** 2 + reading.acceleration_z ** 2)
    temps_actuel = time.time()

    # Si la tape est assez forte et que le délai est respecté
    if force > SEUIL_FORCE and (temps_actuel - dernier_choc) > COOLDOWN:
        son_choisi = random.choice(fichiers_sons)
        print(f"Tape détectée ! (Force: {force:.2f}G) -> Lecture de {os.path.basename(son_choisi)}")

        pygame.mixer.music.load(son_choisi)
        pygame.mixer.music.play()
        dernier_choc = temps_actuel


# Réglage de la réactivité du capteur
accel.report_interval = max(accel.minimum_report_interval, 20)
token = accel.add_reading_changed(on_reading_changed)

# Boucle principale
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nArrêt de Spank.")
    accel.remove_reading_changed(token)