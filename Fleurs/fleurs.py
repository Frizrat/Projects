import numpy as np
import json

def barreProgression(progres, total):
    pourcent = (progres/float(total))*100
    barre = '█'*int(pourcent) + '-'*(100-int(pourcent))
    print(f'\r|{barre}| {pourcent:.2f}%', end='\r')

jsonFile = json.load(open('fleurs.json', 'r', encoding='utf-8'))

dimList = []
coulList = []

# creer les listes de dimensions et de couleurs à l'aide des infos du fichier JSON
for el in jsonFile:
    if el['couleur'] == 'Rouge': el['couleur'] = [1]
    elif el['couleur'] == 'Bleue': el['couleur'] = [0]

    if el['couleur'] is None: dimList += [[el['longueur'], el['largeur']]]
    else:
        dimList = [[el['longueur'], el['largeur']]]+dimList
        coulList = [el['couleur']]+coulList

# initialisation
dimensions = np.array(dimList, dtype=float)                   # crée la variable des entrées
couleur = np.array(coulList, dtype=int)                       # crée la variable de la sortie

dimensions = dimensions/np.amax(dimensions, axis=0)     # transforme nos valeurs afin d'avoir un chiffre entre 0 et 1

dimSplit = np.split(dimensions,[len(couleur)])
dimCoulConnu = dimSplit[0]
dimCoulInconnu = dimSplit[1]

class Reseau_Neuronal(object):
    def __init__(self):
        self.nbEntree = 2
        self.nbSortie = 1
        self.neuroneCache = 3

        # Crée les poids de chaque synapse
        self.W1 = np.random.randn(self.nbEntree, self.neuroneCache) # Matrice 2x3
        self.W2 = np.random.randn(self.neuroneCache, self.nbSortie) # Matrice 3x1

    def entreeVersSortie(self, dimValide):
        self.z1 = np.dot(dimValide, self.W1)           # applique le produit matriciel
        self.z2 = self.sigmoid(self.z1)                 # applique la fonction sigmoïdale
        self.z3 = np.dot(self.z2, self.W2)              # applique le produit matriciel

        return self.sigmoid(self.z3)                    # return la sortie

    def sigmoid(self, puissance): return 1/(1+np.exp(-puissance))

    def deriveSigmoid(self, puissance): return puissance * (1-puissance)

    def sortieVersEntree(self, dimValide, couleur, sortie):
        self.erreurSortie = couleur - sortie
        self.deltaSortie = self.erreurSortie * self.deriveSigmoid(sortie)

        self.erreur_z2 = self.deltaSortie.dot(self.W2.T)
        self.delta_z2 = self.erreur_z2 * self.deriveSigmoid(self.z2)

        self.W1 += dimValide.T.dot(self.delta_z2)
        self.W2 += self.delta_z2.T.dot(self.deltaSortie)

    def entrainement(self, dimValide, couleur):
        sortie = self.entreeVersSortie(dimValide)
        self.sortieVersEntree(dimValide, couleur, sortie)

    def prediction(self):
        if self.entreeVersSortie(dimCoulInconnu) <= 0.5: print('\nLa fleur est Bleue\n')
        else: print('\nLa fleur est ROUGE\n')

RN = Reseau_Neuronal()

nbEntrainement = 10000
barreProgression(0, nbEntrainement)
for i in range(nbEntrainement):
    RN.entrainement(dimCoulConnu, couleur)
    barreProgression(i+1, nbEntrainement)

RN.prediction()