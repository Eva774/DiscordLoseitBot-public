import requests
import json

def submit_response(form_url, answers, verbose=False):
    submit_url = form_url.replace('/viewform', '/formResponse')
    user_agent = {'Referer':form_url}
    
    return requests.post(submit_url, answers, headers=user_agent)


def activity_answers(questions_dict, team, user, date, steps, minutes):
    answers = {}
    msg = 'none'
    if ',' in minutes or '.' in minutes or ',' in steps or '.' in steps: 
        msg = 'Please enter numbers only, without commas or decimals'
    elif any(c.isalpha() for c in minutes) == True or any(c.isalpha() for c in steps) == True:
        msg = 'Please do not enter any letters for your steps or minutes'
    elif float(minutes) > 999:
        msg = 'For activity over 999 minutes, message your captain.'
    elif float(steps) > 99999:
        msg = 'For 100k or more steps in a day, message your captain.'
    else:
        if 'dates' in questions_dict.keys():
            del questions_dict['dates']
        for key, item in questions_dict.items(): 
            if 'username' in item['name']:
                answers['{0}'.format(item['id'])] = user
            elif date in item['name'].split(" ") and 'steps' in item['name'].lower():
                answers['{0}'.format(item['id'])] = steps
            elif date in item['name'].split(" ") and 'minutes' in item['name'].lower():
                answers['{0}'.format(item['id'])] = minutes
            elif 'team' in item['name']:
                for key, option in item['choices'].items():
                    if team.lower() in option.lower():
                        answers['{0}'.format(item['id'])] = option
            else:
                pass
    return msg, answers


def weighin_answers(questions_dict, user, weight, goal = None):
    answers = {}
    msg = 'none'
    if any(c.isalpha() for c in weight) == True:
        msg = 'Please enter only numbers for your weight'
    elif goal != None and any(c.isalpha() for c in goal) == True:
        msg = 'Please enter only numbers for your goal'
    for key, item in questions_dict.items(): 
        if 'goal' in item['name'].lower():
            # if goal == None:
            #     msg = 'Since it is week 0, you have to enter a goal weight'
            # else:
            answers['{}'.format(item['id'])] = weight
            msg = "I submitted your weighin with the reddit username `{0}`!\nA goal of {1} lbs".format(user,weight,goal) # and a goal of {2} lbs
        elif 'username' in item['name'].lower():
            answers['{}'.format(item['id'])] = user
        elif 'weight'in item['name'].lower() and not 'goal' in item['name'].lower():
            answers['{}'.format(item['id'])] = weight

    return msg, answers

# with open('Information/loseit_information.txt') as f:
#     loseit_information = json.load(f)
    
# weighin_url = "https://docs.google.com/forms/d/e/1FAIpQLSezeTZPbOh7gvNWBQ1ur4pYM6CseGelfq3iD5jNxOQu-T17OQ/viewform"#loseit_information['weighin_form']
# activity_url = "https://docs.google.com/forms/d/1YdSTm4crLmTcp59VXRAA5Rfe7Z9hsjory27agp5pxLg/viewform"#loseit_information['activity_form']

# with open('Information/weighin_questions.txt') as f:
#     weighin_questions_dict = json.load(f)
# with open('Information/activity_questions.txt') as f:
#     activity_questions_dict = json.load(f)

# user = 'uncertain_belgian'
# date = '10'
# steps = '200'
# minutes = '50'
# weight = '172.'
# goal = '170.'

# activity_dict = activity_answers(activity_questions_dict, user, date, steps, minutes)
# weighin_dict = weighin_answers(weighin_questions_dict, user, weight, goal)

# form_data = submit_response(activity_url, activity_dict)
# form_data = submit_response(weighin_url, weighin_dict)
