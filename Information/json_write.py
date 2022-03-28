# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 12:21:23 2020

@author: Eva
"""

import json
import datetime

loseit_information = {'LoseitChallenges_subreddit': "https://www.reddit.com/r/LoseItChallenges/",
				'challenge_tracker': "https://docs.google.com/spreadsheets/d/1dzC3LaeJSbbCCKSfrdIYfAq0BkpAfpOabO0Dcf6N06M/edit?usp=sharing",
				'weighin_form': "https://docs.google.com/forms/d/e/1FAIpQLSef8-qePXqq63OYtrCTeldSVy0vSc22wKWWsULbsWAFqPMQmg/viewform",
				'activity_form': "https://docs.google.com/forms/d/e/1FAIpQLSe5X73F5GY1baG-Itd_rdoP9BM8HuG2w6l4jLjB4uPlRv-F4g/viewform",
				'covid_channel_name': 'covid-19-team-isolation-☢',
				'stridekick_channel_name': 'stridekick-🚶',
               'reminder_channel': 'bot-chat',
               'until': '2020-08-21 18:00:00',
               'week' : 'W5'
				}

# with open('loseit_information.txt', 'w') as outputfile: 
# 	json.dump(information,outputfile, indent = 4)

import urllib.request
import json

from bs4 import BeautifulSoup
import requests, warnings
def get_questions(in_url):
    res = urllib.request.urlopen(in_url)
    soup = BeautifulSoup(res.read(), 'html.parser')
    title = soup.title.string.split(" ")
    week = 'W' + str([item for item in title if item.isnumeric()][0])
    all_questions = soup.form.findChildren(attrs={'data-params': lambda x: x and x.startswith('%.')})
    questions_dict = dict()
    question_types = {'0': 'short','2': 'multiple choice','4': 'checkboxes'}

    for question in all_questions:
        list_q = question['data-params'][4:].split(',')
        questions_dict['{0}'.format(list_q[1]).replace('"','')] = {'name':list_q[1].replace('"',''),
                                                   'id':'entry.{0}'.format(list_q[4].replace('[','')),
                                                   'choices': {},
                                                   'type': question_types['{0}'.format(list_q[3])],
                                                   'validation': None}

        number_texts = sum(map(lambda x : '"' in x, list_q))
        if number_texts >4 and list_q[3]!='0':
            text_fields = [x for x in list_q if '"' in x][1:-3]
            i=0
            for text in text_fields:
                questions_dict['{0}'.format(list_q[1].replace('"',''))]['choices']['Option {0}'.format(i+1)] = text.replace('[','').replace(']','').replace('"','')
                i+=1
        for level2 in question.children:
            for level3 in level2.children:
                if 'freebirdFormviewerComponentsQuestionTextRoot' in level3['class']:# == ['freebirdFormviewerComponentsQuestionTextRoot']:
                    for level4 in level3.children:
                        if 'freebirdFormviewerComponentsQuestionTextNumber' in  level4['class']:
                            questions_dict['{0}'.format(list_q[1]).replace('"','')]['validation'] = 'number'

    return questions_dict, week

def update_questions(weighin_url, activity_url,location):
    with open(location+'loseit_information.txt') as f:
        loseit_information = json.load(f)

    
    weighin_questions_dict,week = get_questions(weighin_url)
    with open(location+'weighin_questions.txt', 'w+') as outputfile: 
        json.dump(weighin_questions_dict,outputfile, indent = 4)
       
    
    activity_questions_dict, week2 = get_questions(activity_url)

    dates = []
    for name, question in activity_questions_dict.items():
        for word in name.replace("(","").replace(")","").replace("?","").split(" "):
            if not word.isalpha():
                number = word.translate(str.maketrans('','','abcdefghijklmnopqrstuvwxyz'))
                if number not in dates:
                    dates.append(number)
    activity_questions_dict['dates'] = dates
    with open(location+'activity_questions.txt', 'w+') as outputfile: 
        json.dump(activity_questions_dict,outputfile, indent = 4)
    return week

if __name__ == '__main__':
    weighin_url = 'https://docs.google.com/forms/d/e/1FAIpQLSef8-qePXqq63OYtrCTeldSVy0vSc22wKWWsULbsWAFqPMQmg/viewform'
    activity_url = 'https://docs.google.com/forms/d/e/1FAIpQLSe5X73F5GY1baG-Itd_rdoP9BM8HuG2w6l4jLjB4uPlRv-F4g/viewform'
    location=''
    update_questions(weighin_url,activity_url,location)
    
    # with open('activity_questions.txt') as f:
    #     activity_questions_dict = json.load(f)
    # dates_list = activity_questions_dict['dates']
    # today = datetime.datetime.today()
    # this_month = today.strftime('%B')
    # if today.month == 12:
    #     next_month = today.replace(month = 1).strftime('%B')
    # else: 
    #     next_month = today.replace(month = today.month + 1).strftime('%B')
    # days = []
    # day_1 = dates_list[0]+' '+this_month
    # if dates_list[0]<dates_list[-1]:
    #     day_2 = dates_list[-1]+' '+this_month
    # else:
    #     day_2 = dates_list[-1]+' '+next_month
    # print(days)