import json
from os import listdir
import pandas as pd
from colorama import Fore, init, Style
import matplotlib.pyplot as plt
from datetime import datetime
from time import sleep
init()

# base function
def highlight_word(text, word, color:bool=False):
    # Create the highlighted word
    if not(color):
        highlighted_word = f"{Fore.YELLOW}{word}{Style.RESET_ALL}"
    else:
        highlighted_word = f"{Fore.YELLOW}{word}{Fore.CYAN}"
    # Replace the word in the text with the highlighted word
    highlighted_text = text.lower().replace(word, highlighted_word)
    return highlighted_text
def fix_encode(text):
    return text.encode('latin1').decode('utf-8')
def get_year(timestamp, ymd:int=2):
    """:ymd: 1=year 2=year/month 3=year/month/day"""
    date = pd.to_datetime(int(timestamp), utc=True, unit='ms')
    if ymd==-1:
        return date
    if ymd==0:
        return f"{date.replace(microsecond=0, tzinfo=None)}"
    if ymd==1:
        return f"{date.year}"
    elif ymd==2:
        return f"{date.year}/{str(date.month).zfill(2)}"
    elif ymd==3:
        return f"{date.year}/{str(date.month).zfill(2)}/{str(date.day).zfill(2)}"
    else:
        False
def split_tuple_to_list(my_list:list, add:bool=False, box:bool = False, info:bool=False):
    temp1 = []
    temp2 = []
    # my_list = fix_list(my_list)

    if not(add):
        for a, b in my_list:
            if box:
                if info: temp1.append(f"{a}\n({b[0]})")
                else: temp1.append(a)
                temp2.append(b[0])
            else:
                if info: temp1.append(f"{a}\n({b})")
                else: temp1.append(a)
                temp2.append(b)
        return temp1, temp2
    else:
        for a, b in my_list:
            if info: temp1.append(f"{a}\n({b})")
            else: temp1.append(a)
            try:
                nbr = b[0]+temp2[-1]
            except:
                nbr = b[0]
            temp2.append(nbr)
        return temp1, temp2
def show_conv(index, messages, window, key):
    # if index < window//2: mini = 0
    # else: mini = index - window//2
    # if index+window//2 < len(messages): maxi = len(messages)-1
    # else: maxi = index + window//2
    mini = index - window//2
    maxi = index + window//2
    for indux, message in enumerate(messages[mini:maxi]):
        try:
            content = fix_encode(message['content'])
            if window//2 == indux:
                print(Fore.CYAN + f"{fix_encode(message['sender_name'])}: {highlight_word(content, key, True)}, ({get_year(message['timestamp_ms'], 3)})"+ Style.RESET_ALL)
            else:
                print(f"{fix_encode(message['sender_name'])}: {content}, ({get_year(message['timestamp_ms'], 3)})")
        except:
            print(f"{fix_encode(message['sender_name'])}: MEDIA SHARED, ({get_year(message['timestamp_ms'], 3)})")
    print('\n')
def date_to_timestamp(date:str):
    dt_obj = datetime.strptime(date, '%Y/%m/%d %H:%M:%S')
    return int(dt_obj.timestamp()*1000)
def element_in_list(element_list, list_cible):
    for element in element_list:
        if element['name'] in list_cible:
            return True
    return False
def get_name(participants):
    return [x['name'] for x in participants]
def fix_name(string:str):
    # Créez un dictionnaire pour supprimer les caractères spéciaux
    remove_punctuation_map = dict((ord(char), None) for char in "'\\/*?:\"<>|")
    # Appliquez la traduction pour supprimer les caractères spéciaux
    return string.translate(remove_punctuation_map)

class Instagram_Analytics:
    def __init__(self, messages_path='messages/inbox') -> None:
        """get the path of the dir inbox'"""
        self.path = messages_path
    def setup_name(self, username:str):
        self.username = username
    def get_data(self, dir):
        with open(f"{self.path}/{dir}/message_1.json", encoding='utf-8') as f:
            return json.load(f)
    def get_dir_name(self, user:str):
        for dir in listdir(self.path):
            if '/'+fix_name(user).lower()+'_'.lower() in '/'+dir.lower():
                return str(dir)
        return False
    def get_possible_username(self):
        for dir in listdir(self.path):
            data = self.get_data(dir)
            if len(data['participants'])==2 and data['title'] in get_name(data['participants']):
                for par in data['participants']:
                    if par['name'] != data['title']:
                        return fix_encode(par['name'])
    def find_str(self, keyword:str):
        """find the keyword in all messages"""
        count=0
        for dir in listdir(self.path):
            data = self.get_data(dir)
            
            for message in data['messages']:
                try:
                    if keyword.lower() in message['content'].lower():
                        content = fix_encode(message['content'])
                        print(f"{message['sender_name']}: {highlight_word(content, keyword)}, ({get_year(message['timestamp_ms'], 3)})")
                        count+=1
                except:
                    pass # no content like when there is shared media or vocal
        print(f"count: {count}")
    def sorted_number_message(self):
        """create a graph of sorted conv by number of messages"""
        nbrs_messages = []
        for dir in listdir(self.path):
            data = self.get_data(dir)
            if not(data['title'] == 'Instagram User'):
                nbrs_messages.append((data['title'], len(data['messages'])))
        nbrs_messages_sorted = sorted(nbrs_messages, key=lambda x: x[1], reverse=True)

        users, numbers = split_tuple_to_list(nbrs_messages_sorted)

        plt.plot(users, numbers, 'r')
        plt.show()
    def historic_user(self, username:str):
        """get the historic of number of messages send and recieve by day"""
        path = self.get_dir_name(username)
        if path:
            analyse = {}
            data = self.get_data(path)

            # debug
            # print(data['title'], len(data['messages']))

            # Analyser les messages
            for message in data['messages']:
                try:
                    analyse[get_year(message['timestamp_ms'], 3)][0] += 1
                except:
                    analyse[get_year(message['timestamp_ms'], 3)] = [1, int(message['timestamp_ms'])]

            # Trier les dates et extraire les valeurs
            sorted_analyse = sorted(analyse.items(), key=lambda x: x[1][1])

            dates = [datetime.strptime(date, "%Y/%m/%d") for date, _ in sorted_analyse]
            numbers = [number[0] for _, number in sorted_analyse]

            # Créer une série temporelle avec toutes les dates du premier au dernier jour
            date_range = pd.date_range(start=dates[0], end=dates[-1])

            # Créer un DataFrame avec les données analysées
            df = pd.DataFrame({'date': dates, 'number': numbers})

            # Régler l'index du DataFrame sur les dates
            df.set_index('date', inplace=True)

            # Réindexer le DataFrame pour inclure toutes les dates de l'intervalle et remplir les valeurs manquantes avec 0
            df = df.reindex(date_range, fill_value=0)

            # Filtrer les dates et les valeurs où number n'est pas égal à 0
            filtered_dates = df.index[df['number'] != 0]
            filtered_numbers = df['number'][df['number'] != 0]

            # Tracer les données
            plt.figure(figsize=(10, 5))
            plt.plot(df.index, df['number']) # , marker='o', linestyle='-'

            # Afficher les étiquettes seulement pour les dates où number n'est pas égal à 0
            plt.gca().set_xticks(filtered_dates)
            plt.gca().set_xticklabels(filtered_dates.strftime('%Y-%m-%d'))

            plt.xlabel('Date')
            plt.ylabel('Number of Messages')
            plt.title('Messages Over Time')
            plt.gcf().autofmt_xdate()
            plt.show()
            return True
        else:
            return False
    def number_message_month(self):
        """get number of messages by month"""
        analyse = {}
        for dir in listdir(self.path):
            data = self.get_data(dir)
            for message in data['messages']:
                try:
                    analyse[get_year(message['timestamp_ms'])][0] += 1
                except:
                    analyse[get_year(message['timestamp_ms'])] = [1, int(message['timestamp_ms'])]
        sorted_analyse = sorted(analyse.items(), key=lambda x: x[1][1])

        dates, numbers = split_tuple_to_list(sorted_analyse, box=True)
        plt.plot(dates, numbers, 'r')
        plt.show()
    def message_by_date(self, date:str):
        """get message for a date (day, month, ect)
        example: d1: 2021/05/11 d2: 2023/11"""
        ymd = len(date.split('/'))
        count = 0
        for dir in listdir(self.path):
            data = self.get_data(dir)
            for message in reversed(data['messages']):
                try:
                    if date == get_year(message['timestamp_ms'], ymd):
                        print(f"{message['sender_name']}: {fix_encode(message['content'])}")
                        count += 1
                except:
                    pass
        print(f"count: {count}")
    def message_by_date_user(self, date:str, user_name:str):
        path = self.get_dir_name(user_name)
        if path:
            ymd = len(date.split('/'))
            data = self.get_data(path)
            count = 0
            for message in reversed(data['messages']):
                try:
                    if date == get_year(message['timestamp_ms'], ymd):
                        print(f"{message['sender_name']}: {fix_encode(message['content'])}")
                        count += 1
                except:
                    pass
            print(f"count: {count}")
            return True
        else:
            return False
    def pie_chart(self, maxi:int=10):
        nbrs_messages = []
        for dir in listdir(self.path):
            data = self.get_data(dir)
            if data['title'] in [x['name'] for x in data['participants']]: # avoid group
                nbrs_messages.append((data['title'], len(data['messages'])))
        nbrs_messages_sorted = sorted(nbrs_messages, key=lambda x: x[1], reverse=True)

        users, numbers = split_tuple_to_list(nbrs_messages_sorted[:maxi], info=True)

        # Creating plot
        fig = plt.figure(figsize=(10, 7))
        plt.pie(numbers, labels=users)
        plt.title(f"user by number of messages")
        
        # show plot
        plt.show()
    def pie_chart_year(self, years:int, maxi:int=10):
        nbrs_messages = []
        for dir in listdir(self.path):
            data = self.get_data(dir)
            if data['title'] in [x['name'] for x in data['participants']]:
                count = 0
                for message in reversed(data['messages']):
                    if int(get_year(message['timestamp_ms'], 1)) == years:
                        count += 1
                    elif int(get_year(message['timestamp_ms'], 1)) > years:
                        break
                nbrs_messages.append((data['title'], count))
        nbrs_messages_sorted = sorted(nbrs_messages, key=lambda x: x[1], reverse=True)

        users, numbers = split_tuple_to_list(nbrs_messages_sorted[:maxi], info=True)

        # Creating plot
        fig = plt.figure(figsize=(10, 7))
        plt.pie(numbers, labels=users)
        plt.title(f"user by number of messages in {years}")
        
        # show plot
        plt.show()
    def total_messages_in_time(self, ymd:int = 2):
        analyse = {}
        for dir in listdir(self.path):
            data = self.get_data(dir)
            for message in data['messages']:
                try:
                    analyse[get_year(message['timestamp_ms'], ymd)][0] += 1
                except:
                    analyse[get_year(message['timestamp_ms'], ymd)] = [1, int(message['timestamp_ms'])]
        sorted_analyse = sorted(analyse.items(), key=lambda x: x[1][1])
        dates, numbers = split_tuple_to_list(sorted_analyse, True)
        plt.plot(dates, numbers, 'r')
        plt.show()
    def pie_chart_user_by_years(self, username:str):
        path = self.get_dir_name(username)
        if path:
            analyse = {}
            data = self.get_data(path)
            # Analyser les messages
            for message in data['messages']:
                try:
                    analyse[get_year(message['timestamp_ms'], 1)][0] += 1
                except:
                    analyse[get_year(message['timestamp_ms'], 1)] = [1, int(message['timestamp_ms'])]

            sorted_analyse = sorted(analyse.items(), key=lambda x: x[1][1])
            years, nbrs = split_tuple_to_list(sorted_analyse, box=True)
            # Creating plot
            fig = plt.figure(figsize=(10, 7))
            plt.pie(nbrs, labels=years)
            plt.title(f"Message of {username} over Time")
            
            # show plot
            plt.show()
            return True
        else:
            return False
    def pie_chart_message_by_years(self):
        analyse = {}
        for dir in listdir(self.path):
            data = self.get_data(dir)
            for message in data['messages']:
                try:
                    analyse[get_year(message['timestamp_ms'], 1)][0] += 1
                except:
                    analyse[get_year(message['timestamp_ms'], 1)] = [1, int(message['timestamp_ms'])]

        sorted_analyse = sorted(analyse.items(), key=lambda x: x[1][1])
        years, numbers = split_tuple_to_list(sorted_analyse, box=True, info=True)
        # Creating plot
        fig = plt.figure(figsize=(10, 7))
        plt.pie(numbers, labels=years)
        plt.title(f"Message over Time")
        
        # show plot
        plt.show()
    def pie_chart_focus(self, username:str, maxi:int=8):
        nbrs_messages = []
        for dir in listdir(self.path):
            data = self.get_data(dir)
            if data['title'] in [x['name'] for x in data['participants']]:
                count = 0
                for _ in data['messages']:
                    count+=1
                nbrs_messages.append((data['title'], count))
        nbrs_messages_sorted = sorted(nbrs_messages, key=lambda x: x[1], reverse=True)
        temp = [k[0] for k in nbrs_messages_sorted]
        index = temp.index(username)
        mini = index-(maxi//2)
        if mini < 0: mini = 0
        maxi = index+(maxi//2)+1
        if maxi > len(nbrs_messages_sorted): maxi = len(nbrs_messages_sorted)
        users, numbers = split_tuple_to_list(nbrs_messages_sorted[mini:maxi], info=True)

        # Creating plot
        fig = plt.figure(figsize=(10, 7))
        plt.pie(numbers, labels=users)
        plt.title(f"user by number of messages near: {username}")
        
        # show plot
        plt.show()
    def pie_chart_message(self, maxi:int=5):
        analyse = {}
        ban_word = ['A aimé un message', 'A réagi ❤️ à votre message ', '?', 'Discussion vidéo terminée', 'Appel vocal terminé']
        for dir in listdir(self.path):
            data = self.get_data(dir)
            for message in data['messages']:
                try:
                    if not(fix_encode(message['content']) in ban_word):
                        try:
                            analyse[fix_encode(message['content']).lower()] += 1
                        except:
                            analyse[fix_encode(message['content']).lower()] = 1
                except:
                    pass
        analyse_sorted = sorted(analyse.items(), key=lambda x: x[1], reverse=True)
        messages, numbers = split_tuple_to_list(analyse_sorted[:maxi], info=True)

        # Creating plot
        fig = plt.figure(figsize=(10, 7))
        plt.pie(numbers, labels=messages)
        plt.title(f"top {maxi} of messages")
        
        # show plot
        plt.show()
    def pie_chart_message_years(self, year, maxi:int=5):
        analyse = {}
        ban_word = ['A aimé un message', 'A réagi ❤️ à votre message ', '?', 'Discussion vidéo terminée', 'Appel vocal terminé']
        for dir in listdir(self.path):
            data = self.get_data(dir)
            for message in data['messages']:
                try:
                    if not(fix_encode(message['content']) in ban_word) and int(get_year(message['timestamp_ms'], 1)) == year:
                        try:
                            analyse[fix_encode(message['content']).lower()] += 1
                        except:
                            analyse[fix_encode(message['content']).lower()] = 1
                    elif int(get_year(message['timestamp_ms'], 1)) > year:
                        break
                except:
                    pass
        analyse_sorted = sorted(analyse.items(), key=lambda x: x[1], reverse=True)
        messages, numbers = split_tuple_to_list(analyse_sorted[:maxi], info=True)

        # Creating plot
        fig = plt.figure(figsize=(10, 7))
        plt.pie(numbers, labels=messages)
        plt.title(f"top {maxi} of messages in {year}")
        
        # show plot
        plt.show()
    def pie_chart_message_user(self, username, maxi:int=5):
        analyse = {}
        path = self.get_dir_name(username)
        if path:
            data = self.get_data(path)
            ban_word = ['A aimé un message', 'A réagi ❤️ à votre message ', '?', 'Discussion vidéo terminée', 'Appel vocal terminé']
            for message in data['messages']:
                try:
                    if not(fix_encode(message['content']) in ban_word):
                        try:
                            analyse[fix_encode(message['content']).lower()] += 1
                        except:
                            analyse[fix_encode(message['content']).lower()] = 1
                except:
                    pass
            analyse_sorted = sorted(analyse.items(), key=lambda x: x[1], reverse=True)
            messages, numbers = split_tuple_to_list(analyse_sorted[:maxi], info=True)

            # Creating plot
            fig = plt.figure(figsize=(10, 7))
            plt.pie(numbers, labels=messages)
            plt.title(f"top {maxi} of messages")
            
            # show plot
            plt.show()
            return True
        else:
            return False
    def find_before(self, keyword:str):
        count = 0
        for dir in listdir(self.path):
            data = self.get_data(dir)
            for index, message in enumerate(data['messages']):
                try:
                    if keyword.lower() in message['content'].lower() and index > 0:
                        count += 1
                        mess = data['messages'][index-1]
                        content = fix_encode(mess['content'])
                        print(f"{fix_encode(mess['sender_name'])}: {content}, ({get_year(mess['timestamp_ms'], 3)})")
                        content = fix_encode(message['content'])
                        print(f"{fix_encode(message['sender_name'])}: {highlight_word(fix_encode(message['content']), keyword)}, ({get_year(message['timestamp_ms'], 3)})")
                except:
                    pass
        print(f"count: {count}")
    def find_after(self, keyword:str):
        count = 0
        for dir in listdir(self.path):
            data = self.get_data(dir)
            for index, message in enumerate(data['messages']):
                try:
                    if keyword.lower() in message['content'].lower() and index > 0:
                        content = fix_encode(message['content'])
                        print(f"{fix_encode(message['sender_name'])}: {highlight_word(fix_encode(message['content']), keyword)}, ({get_year(message['timestamp_ms'], 3)})")
                        count += 1
                        mess = data['messages'][index+1]
                        content = fix_encode(mess['content'])
                        print(f"{fix_encode(mess['sender_name'])}: {content}, ({get_year(mess['timestamp_ms'], 3)})")
                except:
                    pass
        print(f"count: {count}")
    def get_conv_user(self, username:str, key:str, window:int = 10):
        path = self.get_dir_name(username)
        if path:
            data = self.get_data(path)
            count = 0
            for index, message in enumerate(reversed(data['messages'])):
                try:
                    content = fix_encode(message['content']).lower()
                except:
                    content = False
                if content:
                    if key.lower() in content:
                        count += 1
                        show_conv(index, list(reversed(data['messages'])), window, key)
            print(f"count: {count}")
            return True
        else:
            return False
    def realtime_conv(self, username: str, start_time: str, end_time: str, speed: int = 1):
        path = self.get_dir_name(username)
        if path:
            data = self.get_data(path)
            start = False
            count = 0
            start_time = date_to_timestamp(start_time)
            end_time = date_to_timestamp(end_time)
            
            for message in list(reversed(data['messages'])):
                message_time = int(message['timestamp_ms'])
                
                if start_time < message_time:
                    count += 1
                    if not start:
                        start = message_time
                        try:
                            content = fix_encode(message['content'])
                        except:
                            content = 'MEDIA SHARED'
                    else:
                        elapsed_time = (message_time - previous_message_time) / 1000  # Convertir ms en secondes
                        adjusted_sleep_time = elapsed_time / speed  # Ajuster par la vitesse
                        
                        print(Fore.CYAN + f"{fix_encode(message['sender_name'])}:" + Fore.GREEN + f" {content} " + Fore.YELLOW + f"({get_year(message['timestamp_ms'], 0)})")
                        sleep(adjusted_sleep_time)
                        
                        try:
                            content = fix_encode(message['content'])
                        except:
                            content = 'MEDIA SHARED'
                    
                    previous_message_time = message_time
                
                if end_time < message_time:
                    break
            
            print(Fore.CYAN + f"{fix_encode(message['sender_name'])}:" + Fore.GREEN + f" {content} " + Fore.YELLOW + f"({get_year(message['timestamp_ms'], 0)})")
            print(f"count: {count}")
            return True
        else:
            return False
    def pie_chart_median_delay(self, maxi:int = 10):
        median_delay = {}
        for dir in listdir(self.path):
            data = self.get_data(dir)
            for part in data['participants']:
                if part['name'] in data['title']:
                    timestamp = []
                    for message in list(reversed(data['messages'])):
                        timestamp.append(message['timestamp_ms'])
                    delay = []
                    for index in range(len(timestamp)-1):
                        delay.append(timestamp[index+1]-timestamp[index])
                    delay_sorted = sorted(delay)
                    if not(len(delay_sorted)==0):
                        median_delay[fix_encode(data['title'])] = delay_sorted[len(delay_sorted)//2]/1000
                    break
        median_delay_sorted = sorted(median_delay.items(), key=lambda x: x[1])
        users, numbers = split_tuple_to_list(median_delay_sorted[:maxi], info=True)

        # Creating plot
        fig = plt.figure(figsize=(10, 7))
        plt.pie(numbers, labels=users)
        plt.title(f"median time to respond")
        
        # show plot
        plt.show()
    def pie_chart_median_delay_list(self, users_list:list, maxi:int = 10):
        median_delay = {}
        for dir in listdir(self.path):
            data = self.get_data(dir)
            for part in data['participants']:
                if part['name'] in data['title']:
                    if fix_encode(part['name']) in users_list:
                        timestamp = []
                        for message in list(reversed(data['messages'])):
                            timestamp.append(message['timestamp_ms'])
                        delay = []
                        for index in range(len(timestamp)-1):
                            delay.append(timestamp[index+1]-timestamp[index])
                        delay_sorted = sorted(delay)
                        if not(len(delay_sorted)==0):
                            median_delay[fix_encode(data['title'])] = delay_sorted[len(delay_sorted)//2]/1000
                        break
        median_delay_sorted = sorted(median_delay.items(), key=lambda x: x[1])
        users, numbers = split_tuple_to_list(median_delay_sorted[:maxi], info=True)

        # Creating plot
        fig = plt.figure(figsize=(10, 7))
        plt.pie(numbers, labels=users)
        plt.title(f"median time to respond")
        
        # show plot
        plt.show()
    def get_conv_name(self):
        for dir in listdir(self.path):
            data = self.get_data(dir)
            if element_in_list(data['participants'], data['title']):
                print(f"{fix_encode(data['title'])}")
    def find_str_RT(self, keyword:str):
        """find the keyword in all messages"""
        count=0
        for dir in listdir(self.path):
            data = self.get_data(dir)
            
            for message in data['messages']:
                try:
                    if keyword.lower() in message['content'].lower():
                        content = fix_encode(message['content'])
                        print(f"{message['sender_name']}: {highlight_word(content, keyword)}, ({get_year(message['timestamp_ms'], 3)})")
                        count+=1
                except:
                    pass # no content like when there is shared media or vocal
        # print(f"count: {count}')
        return count