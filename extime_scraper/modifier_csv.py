import csv
import os

def ajouter_champs_csv(chemin_fichier, nouveaux_champs=None):
    if nouveaux_champs is None:
        nouveaux_champs = []
    
    if not os.path.exists(chemin_fichier):
        print(f"Le fichier {chemin_fichier} n'existe pas.")
        return
    
    fichier_temp = chemin_fichier + ".temp"
    
    try:
        with open(chemin_fichier, 'r', newline='', encoding='utf-8') as fichier_entree:
            lecteur = csv.reader(fichier_entree)
            
            en_tete = next(lecteur, [])
            
            en_tete_modifie = en_tete + nouveaux_champs
            
            with open(fichier_temp, 'w', newline='', encoding='utf-8') as fichier_sortie:
                ecrivain = csv.writer(fichier_sortie)
                
                ecrivain.writerow(en_tete_modifie)
                
                for ligne in lecteur:
                    nouvelle_ligne = ligne + [None] * len(nouveaux_champs)
                    ecrivain.writerow(nouvelle_ligne)
        
        os.replace(fichier_temp, chemin_fichier)
        print(f"Les champs {nouveaux_champs} ont été ajoutés avec succès.")
    
    except Exception as e:
        print(f"Une erreur est survenue: {str(e)}")
        if os.path.exists(fichier_temp):
            os.remove(fichier_temp)

if __name__ == "__main__":
    chemin_fichier = input("Entrez le chemin complet du fichier CSV: ")
    
    ajouter_champs_csv(chemin_fichier, ["materiaux", "nom_d_origine", "dimensions"])
