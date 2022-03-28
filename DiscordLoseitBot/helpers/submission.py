# import requests
# url = "https://docs.google.com/forms/d/e/1FAIpQLSdv0qGfaf99DX40NQV09JNLAzyicDdjKi1TtrTh0dEL0J3C1g/formResponse"

# form_data = {'entry.920838485': 'Option 2',
# 'entry.1631574063': '370'}

# user_agent = {'Referer':'https://docs.google.com/forms/d/e/1FAIpQLSdv0qGfaf99DX40NQV09JNLAzyicDdjKi1TtrTh0dEL0J3C1g/viewform'}
# r = requests.post(url, data = form_data, headers = user_agent)
# print(r)

import urllib.request
from bs4 import BeautifulSoup
import requests, warnings

def get_questions(in_url):
    res = urllib.request.urlopen(in_url)
    soup = BeautifulSoup(res.read(), 'html.parser')
    for content in soup.contents:
        print(content)
    all_questions = soup.form.findChildren(attrs={'class': lambda x: x and x.startswith('%.')})
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


def submit_response(form_url, cur_questions, verbose=False, **answers):
    submit_url = form_url.replace('/viewform', '/formResponse')
    form_data = {'draftResponse':[],
                'pageHistory':0}
    for v in cur_questions.values():
        form_data[v] = ''
    for k, v in answers.items():
        if k in cur_questions:
            form_data[cur_questions[k]] = v
        else:
            warnings.warn('Unknown Question: {}'.format(k), RuntimeWarning)
    if verbose:
        print(form_data)
    
    user_agent = {'Referer':form_url}#,
#                  'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}
    return requests.post(submit_url, data=cur_questions, headers=user_agent)

url = "https://docs.google.com/forms/d/e/1FAIpQLSdv0qGfaf99DX40NQV09JNLAzyicDdjKi1TtrTh0dEL0J3C1g/viewform"
#url = "https://docs.google.com/forms/d/e/1FAIpQLSctejauXqVsNEU_XElmk1mhWAb70zT_03M17qm-hUxrBHq_Pg/viewform"
#url = "https://docs.google.com/forms/d/1YdSTm4crLmTcp59VXRAA5Rfe7Z9hsjory27agp5pxLg/viewform"

questions_dict = get_questions(url)

#def activity(questions_dict, user, date, steps, minutes):
#    answers = {}
#    if ',' in minutes or '.' in minutes or ',' in steps or '.' in steps: 
#        print('Please enter numbers only, without commas or decimals')
#    elif float(minutes) > 481:
#        print('For activity minutes over greater 8 hours, message your captain.')
#    elif float(steps) > 50000:
#        print('For steps over 50k in a day, message your captain.')
#    else:
#        for key, item in questions_dict.items(): 
#            if 'username' in item['name']:
#                answers['{}'.format(item['id'])] = user
#            elif date in item['name'] and 'steps' in item['name'].lower():
#                answers['{}'.format(item['id'])] = steps
#            elif date in item['name'] and 'minutes' in item['name'].lower():
#                answers['{}'.format(item['id'])] = minutes
#            elif 'team' in item['name']:
#                for key, option in item['choices'].items():
#                    if 'hairy' in option.lower():
#                        answers['{}'.format(item['id'])] = option
#    return answers
#
#user = 'uncertain_belgian'
#date = '10'
#steps = '200'
#minutes = '50'
#
#answer_dict = activity(questions_dict, user, date, steps, minutes)

