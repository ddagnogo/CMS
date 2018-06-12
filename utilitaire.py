# coding: utf8

class Utilitaire:
    def verifier_donnee_date(annee, mois, jour):
        try:
            aa = int(annee)
            mm = int(mois)
            jj = int(jour)
            if (mm == 1 or mm == 3 or mm == 5 or mm == 7 or mm == 8 or mm== 10 or mm == 12) and jj >= 1 and jj <= 31:
                return False
            elif (mm == 4 or mm == 6 or mm == 9 or mm == 11) and jj >=1 and jj <= 30:
                return False
            elif mm == 2 and (((aa % 4 == 0) and (aa % 100 != 0)) or (aa % 400 == 0)) and jj >= 1 and jj <= 29:
                return False
            elif mm == 2 and (not(((aa % 4 == 0) and (aa % 100 != 0)) or (aa % 400 == 0))) and jj >= 1 and jj <= 28:
                return False
            else:
                return True
        except ValueError:
            return True
    verifier_donnee_date = staticmethod(verifier_donnee_date)
    
    
    def verifier_donnee_identifiant(identifiant):
        tab = identifiant.split('-')
        for each in tab:
            if not each.isalnum():
                return True
        return False
    verifier_donnee_identifiant = staticmethod(verifier_donnee_identifiant)
