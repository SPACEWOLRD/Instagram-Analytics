from Instagram_Analytics import Instagram_Analytics
import sys
from colorama import init

init()

# Rediriger stderr vers nul
sys.stderr = open('nul', 'w')

analytics = Instagram_Analytics()
print(f'Nom de Compte possible: {analytics.get_possible_username()}')

analytics.setup_name(input('Nom de compte: '))

def show_menu():
    menu = """
1.rechercher mot(s)
2.Conversations trié par nombre de messages
3.Nombre de message par jour pour une conversation
4.Nombre de message par mois
5.Voir tous les messages d'une date (au mois ou jour près)
6.Voir tous les messages d'une date d'une conversation (au mois ou jour près)
7.Graphique en Camenbert du nombre de message pour les conversations
8.Graphique en Camenbert du nombre de message pour les conversations pour une année
9.Graphique du nombre total de message par mois
10.Graphique en Camenbert du nombre de message par année pour une conversation
11.Graphique en Camenbert du nombre de message par année
12.Graphique en Camenbert du nombre de message par personne autour d'un personne
13.Graphique en Camenbert des messages les plus dit
14.Graphique en Camenbert des messages les plus dit par année
15.Graphique en Camenbert des messages les plus dit d'une conversation
16.Voir tous les messages envoyer avants un message qui contient un/des mot/s
17.Voir tous les messages envoyer après un message qui contient un/des mot/s
18.Voir les 10 message autour d'un/des mot/s d'un utilisateur
19.Temps médian d'attente entre deux messages par conversation
20.Obtenir tous les noms de conversations
"""
    print(menu)
def func(val):
    if val=='1':
        key = input('Mot(s) rechercher: ')
        analytics.find_str(key)
    elif val=='2':
        analytics.sorted_number_message()
    elif val=='3':
        username = input('utilisateur: ')
        if not(analytics.historic_user(username)):
            print(f"Pas d'utilisateur: {username}")
    elif val=='4':
        analytics.number_message_month()
    elif val=='5':
        date = input('Date (AAAA/MM ou AAAA/MM/JJ): ')
        analytics.message_by_date(date)
    elif val=='6':
        date = input('Date (AAAA/MM ou AAAA/MM/JJ): ')
        username = input('utilisateur: ')
        if not(analytics.message_by_date_user(date, username)):
            print(f"Pas d'utilisateur: {username}")
    elif val=='7':
        analytics.pie_chart()
    elif val=='8':
        annee = input('Année (AAAA): ')
        analytics.pie_chart_year(annee)
    elif val=='9':
        analytics.total_messages_in_time()
    elif val=='10':
        username = input('utilisateur: ')
        if not(analytics.pie_chart_user_by_years('totole')):
            print(f"Pas d'utilisateur: {username}")
    elif val=='11':
        analytics.pie_chart_message_by_years()
    elif val=='12':
        username = input('utilisateur: ')
        analytics.pie_chart_focus(username)
    elif val=='13':
        maxi = int(input('maximum de messages: '))
        analytics.pie_chart_message(maxi)
    elif val=='14':
        annee = input('Année (AAAA): ')
        analytics.pie_chart_message_years(annee)
    elif val=='15':
        username = input('utilisateur: ')
        if not(analytics.pie_chart_message_user(username)):
            print(f"Pas d'utilisateur: {username}")
    elif val=='16':
        key = input('Mot(s) rechercher: ')
        analytics.find_before(key)
    elif val=='17':
        key = input('Mot(s) rechercher: ')
        analytics.find_after(key)
    elif val=='18':
        key = input('Mot(s) rechercher: ')
        username = input('utilisateur: ')
        if not(analytics.get_conv_user(username, key)):
            print(f"Pas d'utilisateur: {username}")
    elif val=='19':
        analytics.pie_chart_median_delay()
    elif val=='20':
        analytics.get_conv_name()
    else:
        print(f"l'entrée est invalide: {val}")

if __name__ == '__main__':
    show_menu()
    print("ATTENTION, NE PAS METTRE D'EMOJI MEME POUR LES PSEUDOS")
    while True:
        choix = input('Choix: ')
        func(choix)