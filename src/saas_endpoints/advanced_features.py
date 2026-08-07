
# Importation des bibliothèques nécessaires
import base64
from Crypto.Cipher import AES
from binascii import hexlify, unhexlify
from string import ascii_letters, digits
import hashlib


def encrypt_reports(reports):
    """
    Fonction pour chiffrement des rapports d'audit.

    :param reports: Liste de chaînes représentant les rapports à chiffrer.
    :return: Une liste de chaînes encodées et chiffrées.
    """

    # Choix du format chiffré
    encrypted_reports = []
    
    for report in reports:
        # Chiffrement XOR simple (pour illustrer)
        cipher = AES.new(b'key', AES.MODE_ECB)
        encoded_report = base64.b64encode(cipher.encrypt(report.encode()))
        
        encrypted_reports.append(encoded_report)

    return encrypted_reports


def complexity_analysis(source_code):
    """
    Fonction pour analyser la complexité algorithmique d'un code source.

    :param source_code: Une chaîne de caractères représentant le code source à analyser.
    :return: Un entier correspondant à une évaluation de la complexité algorithmique du code.
    """

    complexity_score = 0

    # Analyse de l'importance des instructions
    if 'if' in source_code.lower() or 'for' in source_code.lower():
        complexity_score += 2
    
    # Analyse de la taille du code source
    source_length = len(source_code)
    
    if source_length < 10:
        complexity_score += 1

    elif source_length >= 10 and source_length <= 50:
        complexity_score += 3

    else:
        complexity_score += 5
    
    return complexity_score


# Exemple de usage
original_source_code = """
def square(x):
    return x * x
"""

analysis_result = complexity_analysis(original_source_code)
print(f'Analyse du code : {analysis_result}')

encrypted_report_1 = encrypt_reports([original_source_code])
print('Chiffrement des rapports d\'audit...')
for encrypted in encrypted_report_1:
    print(encrypted.decode())