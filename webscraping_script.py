# ******************* Hunter Thorpe 1079893 ELODP Project 1 Tasks1-5 **********

import requests
import csv
from bs4 import BeautifulSoup
import json
import re
import matplotlib.pyplot as plt
import numpy

# ************************* Function definitions ******************************

def parse_url_headline_name_score(url, soup):
    """takes an articles url and its soup object, decomposes body of article
    into body_list, uses regex to find match scores and player names,
    returns a list with url, header, player mentioned and match score"""
    player_value = 'none'
    score_value = []
    body_list = re.sub("\n", " ", soup.body.text)
    body_list = body_list.split(' ')

    # iterating through body of article in pairs of words at a time
    for place in range(0, len(body_list) - 2):
        
        # stripping words of puncuation and changing it to uppercase
        word_1 = (re.sub('[^\w\d\s\)\(-]', '', body_list[place]
                .strip('\n').upper()))
        word_2 = (re.sub('[^\w\d\s\)\(-]', '', body_list[place + 1]
                .strip('\n').upper()))
        
        # using regex to see if pair of words forms a potential match score 
        word_1_status = re.search("^[0-9]-[0-9]$", word_1)
        word_2_status = re.search("^[0-9]-[0-9]$", word_2)
        word_2_status_tb = re.search("^\([0-9]{1}-[0-9]{1}\)$", word_2)
        
        # checking if potential scores satisfy above regex and  
        if ((word_1_status and (word_2_status or word_2_status_tb)) and 
                score_value == []):
            # checking if they form complete sets
            if max([int(word_1[0]), int(word_1[2])]) > 5 and \
                (len(word_2) > 3 or max([int(word_2[0]), int(word_2[2])]) > 5):
                
                score_value.append(word_1)
                score_value.append(word_2)
            
                # checking following words to see if part of match score
                counter = 2
                while (re.search("^[0-9]-[0-9]$", re.sub('[^\w\d\s\)\(-]', '',
                        body_list[place + counter].strip('\n').upper())) or 
                        re.search(
                        "^\([0-9]{1}-[0-9]{1}\)$", re.sub('[^\w\d\s\)\(-]', '', 
                        body_list[place + counter].strip('\n').upper()))):
            
                    score_value.append(re.sub('[^\w\d\s\)\(-]', '', 
                        body_list[place + counter].strip('\n').upper()))
                    counter = counter + 1
        
        # removing brackets and dashes to find first player mentioned 
        word_1 = re.sub('[^\w\d\s]', '', body_list[place].strip('\n').upper())
        word_2 = (re.sub('[^\w\d\s]', '', body_list[place + 1]
            .strip('\n').upper()))
        word_list = word_1 + ' ' + word_2
        
        if word_list in player_dict.keys() and player_value == 'none':
             player_value = word_list
        
        # triggers when player name and match score is found 
        if (player_value != 'none') and (score_value != []):
            # calculating game difference by iterating through each set 
            game_difference = 0
            for set_ in score_value:
                # selecting non tie breaker scores 
                if set_[0] != '(':
                    game_difference = (game_difference + 
                        int(set_[0]) - int(set_[2]))
            
            # incrementing number of articles written by player, 
            # and increasing total game difference
            player_dict[player_value][1] = player_dict[player_value][1] + 1 
            player_dict[player_value][2] = (player_dict[player_value][2] + 
                abs(game_difference))
            
            # changing score value into string representation 
            str_score_value = ''
            for set_ in score_value:
                str_score_value = str_score_value + set_ + ' '
            score_value = str_score_value
            break 
                
        
    return [url, soup.h1.text, player_value, score_value]
    
def parse_page(url, soup):
    """Takes the url of an article and its relevant soup object and parses it 
    using the parse_url_headline_name_score function 
    then writes url and header to task1.csv, and url, header, player and 
    match score to task2.csv where appropriate"""
    
    page_info = parse_url_headline_name_score(url, soup)
    
    # writing url and header to task1.csv
    with open('task1.csv', 'a+') as file1:
        writer1 = csv.writer(file1)
        writer1.writerow(page_info[0:2])
    
    # writing url, header, player and match score to task2.csv where needed
    if (page_info[2] != 'none') and (page_info[3] != []):
        with open('task2.csv', 'a+') as file2:
            writer2 = csv.writer(file2)
            writer2.writerow(page_info[0:4])
 
# ************************* Script Body ********************************

# opening csv files for tasks 1-3 and writing appropriate headings 
with open('task1.csv', 'w') as file1:
    writer1 = csv.writer(file1)
    writer1.writerow(['url', 'headline'])    
with open('task2.csv', 'w') as file2:
    writer2 = csv.writer(file2)
    writer2.writerow(['url', 'headline', 'player', 'score'])     
with open('task3.csv', 'w') as file3:
    writer3 = csv.writer(file3)
    writer3.writerow(['player', 'avg_game_difference']) 

# creating a player dict and filling it with data from json file, 
# keys made up of player names, values are a list of 
# [win%, articles about them (with scores), total game difference]
player_dict = {}
input_file = open('player_info.json', 'r')
json_decode = json.load(input_file)
for item in json_decode:
    player_dict[item.get("name")] = [item.get("wonPct"), 0, 0]

# parsing seed page to access first article 
seed_url = 'http://comp20008-jh.eng.unimelb.edu.au:9889/main/'
seed_page = requests.get(seed_url).text
seed_soup = BeautifulSoup(seed_page, "lxml")
first_url = seed_url + (seed_soup.a.get('href'))
first_page = requests.get(first_url).text
first_soup = BeautifulSoup(first_page, "lxml")

# parsing 1st article page and establishing 2nd article page as current page
parse_page(first_url, first_soup)
current_url = (seed_url + 
    (first_soup.find('p', {"class" : "nextLink"}).a.get('href')))
current_page = requests.get(current_url).text
current_soup = BeautifulSoup(current_page, "lxml")
  
# iterating through the remainder of article pages and 
# parsing them until the first articled parsed is reached again 
while (current_url != first_url):
    parse_page(current_url, current_soup)
    current_url = (seed_url + 
        (current_soup.find('p', {"class" : "nextLink"}).a.get('href')))
    current_page = requests.get(current_url).text
    current_soup = BeautifulSoup(current_page, "lxml")
  
# initialising data strucutures to aid in iterating and performing tasks 3,4,5
top_5_players = []
players_1_or_more = []
avg_game_diff = []
win_percentage = []
for player in player_dict.keys():
    if player_dict[player][1] >= 1:
        # calculating average game difference and outputing it to task3.csv
        with open('task3.csv', 'a+') as file3:
            writer3 = csv.writer(file3)
            writer3.writerow([player, 
                player_dict[player][2]/player_dict[player][1]])
        
        # creating list of top 5 players 
        # filling list with 5 players
        if len(top_5_players) < 5:
            top_5_players.append([player_dict[player][1], player])
        
        # when listlen is 5 add player, sort list then pop last player 
        else:
            top_5_players.append([player_dict[player][1], player])
            top_5_players.sort()
            top_5_players.reverse()
            top_5_players.pop()
            
        # add player, avg game diff and win % to equivalent position 
        # in associated lists for task 5
        players_1_or_more.append(player)
        avg_game_diff.append(player_dict[player][2]/player_dict[player][1])
        win_percentage.append(player_dict[player][0])

# creating bar chart of 5 players that articles are most frequently about             
fig = plt.figure(figsize = (9,5))
names = []
scores = []
for num in range(0,5):
    names.append(top_5_players[num][1])
    scores.append(top_5_players[num][0])
positions = [0, 1, 2, 3 ,4]
plt.bar(positions, scores, width = 0.5)
plt.xticks(positions, names)
plt.yticks(numpy.arange(0, max(scores)+1, 1.0))
plt.title("Frequency of articles mentioning players vs\
 5 of the most written about player's names")
plt.ylabel("Frequency of articles")
plt.xlabel("Player names")
plt.savefig("task4.png")
            
# creating scatterplot with all players written about at least once,
# y axis- win %, x axis- avg game diff
fig = plt.figure(figsize = (10,10))
plt.scatter(avg_game_diff, win_percentage)
for i, txt in enumerate(players_1_or_more):
    plt.annotate(txt, (avg_game_diff[i], win_percentage[i]))
plt.gca().invert_yaxis()
plt.title("Win percentage vs\
 Average game difference for players with at least 1 article")
plt.xlabel("Average game difference")
plt.ylabel("Win percentage")
plt.savefig("task5.png")

# ********************** End of Script **************************
