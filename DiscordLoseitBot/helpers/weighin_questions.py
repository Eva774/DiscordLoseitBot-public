# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 15:45:12 2020

@author: Eva
"""
import urllib.request
import json 

from bs4 import BeautifulSoup
import requests, warnings
def get_questions(in_url):
    res = urllib.request.urlopen(in_url)
    soup = BeautifulSoup(res.read(), 'html.parser')
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
    
    return questions_dict


with open('../Information/loseit_information.txt') as f:
    loseit_information = json.load(f)
    
weighin_url = loseit_information['weighin_form']
weighin_questions_dict = get_questions(weighin_url)
with open('../Information/weighin_questions.txt', 'w') as outputfile: 
	json.dump(weighin_questions_dict,outputfile)
    
activity_url = loseit_information['activity_form']
activity_questions_dict = get_questions(activity_url)
with open('../Information/activity_questions.txt', 'w') as outputfile: 
	json.dump(activity_questions_dict,outputfile)