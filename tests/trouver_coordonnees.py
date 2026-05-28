# tests/trouver_coordonnees.py
import cv2

image = cv2.imread("data/dataset/30.png")
h, w = image.shape[:2]
print(f"Taille image : {w} x {h} pixels")

# Réduire l'affichage à 50% pour rentrer dans l'écran
scale = 0.5
image_affichage = cv2.resize(image, None, fx=scale, fy=scale)

print("Dessine un rectangle autour du champ voulu")
print("ESPACE ou ENTREE pour confirmer — C pour annuler\n")

# Sélection sur l'image réduite
roi = cv2.selectROI("Selectionne la zone", image_affichage, False)
cv2.destroyAllWindows()

# Coordonnées sur l'image réduite
x_small, y_small, larg_small, haut_small = roi

# Reconvertir en coordonnées réelles (image originale)
x    = int(x_small    / scale)
y    = int(y_small    / scale)
larg = int(larg_small / scale)
haut = int(haut_small / scale)

print(f"Coordonnées réelles (pixels) :")
print(f"  x={x}, y={y}, largeur={larg}, hauteur={haut}")

# Convertir en % pour zone_config.py
print(f"\nCoordonnées en % :")
print(f"  h1={round(y/h, 3)}, h2={round((y+haut)/h, 3)}")
print(f"  w1={round(x/w, 3)}, w2={round((x+larg)/w, 3)}")

# Vérifier visuellement la zone sélectionnée
zone = image[y:y+haut, x:x+larg]
cv2.imshow("Zone selectionnee", zone)
cv2.waitKey(0)
cv2.destroyAllWindows()