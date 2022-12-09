import yaml 
import pathlib 
import xml.etree.ElementTree as ET

import psycopg2
from psycopg2 import sql

import os
import datetime as dt

from typing import Any, Text, Dict, List, Optional

from rasa.shared.core.constants import ACTION_DEFAULT_ASK_AFFIRMATION_NAME, \
    ACTION_DEFAULT_FALLBACK_NAME

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.types import DomainDict
from rasa_sdk.events import ConversationPaused, UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    SlotSet,
    UserUtteranceReverted,
    ConversationPaused,
    EventType,
)

USER_INTENT_OUT_OF_SCOPE = "out_of_scope"

# names = pathlib.Path("data/names.txt").read_text().split("\n")

# class ActionDefaultAskAffirmation(Action):
class ActionDefaultAskAffirmation(Action):
    """
        Overwrite ask affirmation action
    """

    def name(self) -> Text:
        return ACTION_DEFAULT_ASK_AFFIRMATION_NAME


    async def run(self, dispatcher, tracker, domain):
            # select the top three intents from the tracker        
            # ignore the first one -- nlu fallback
            predicted_intents = tracker.latest_message["intent_ranking"][1:4]
            
    # A prompt asking the user to select an option
            message = "Sorry! What do you want to do?"

    # a mapping between intents and user friendly wordings
            intent_mappings = {
                "About_Dornier": "Information about the Dornier Group",
                "Dornier_Business": "Information about the Business presence of the Dornier group",
                "Dornier_Locations": "Information of the locations at which the Dornier group is  present",
                "Dornier_Headquarters": "Information about the Headquarters of the Dornier group",
                "Dornier_Workforce": "Information about the number of people working at the Dornier group",
                "Dornier_Projects": "Information about the number of projects completed at the Dornier group",
                "Business_sector_emobility": "Information about the contribution towards E-mobility by the Dornier group",
                "Business_sector_nuclear": "Information about the contribution towards Nuclear sector by the Dornier group",
                "Business_sector_water": "Information about the contribution towards water sector by the Dornier group",
                "Business_sector_aviation": "Information about the contribution towards Aviation by the Dornier group",
                "Business_sector_power": "Information about the contribution towards Power sector by the Dornier group",
                "Workplace_gender_equality": "Information about the Gender equality at the Dornier group",
                "Workplace_policy": "Information about the workplace policy at the Dornier group",
                "Working_ergonomics": "Information about the working ergonomics at the Dornier group",
                "Breaks": "Information about breaks allowed",
                "Nonsmoker_policy": "Information about the Non-smoker policy",
                "Medical_facilities": "Information about the medical facilities",
                "Ideal_employee": "Information about the expectations from employee",
                "Leadership_style": "Information about the Leadership style",
                "Corporate_culture": "Information about the Corporate culture",
                "Performance_evaluation": "Information about the Performance evaluation",
                "Promoting_strengths_talents": "Information about Promoting strengths and talents of employees",
                "Response_timeline": "Information about the response timeline",
                "Apply_to_dornier": "Information about how to apply for a job",
                "Application_process": "Information about the Application process",
                "Job_ticket": "Information about the Job ticket",
                "Company_pension_scheme": "Information about the company pension scheme",
                "Christmas_bonus": "Information about the Christmas bonus",
                "Holiday_pay": "Information about the Holiday pay",
                "Work_from_home": "Information about Work from Home",
                "Work_from_home_100": "Information regarding working from home everyday",
                "Benefits_provided": "Information about the benefits",
                "Interview_process": "Information about the interview process",
                "Current_job_openings": "Information about the current job openings",
                "Notice_period": "Information about the Notice period",
                "Abroad_assignment": "Information about Abroad assignment",
                "Customers": "Information about the Customers",
                "Diversity_at_dornier": "Information about Diversity at the Dornier Group",
                "Company_car": "Information about the Company car",
                "Parking_facilities": "Information about the Parking facilities",
                "Documents_needed": "Information about the Documents needed",
                "Probationary_period": "Information about the Probationary period",
                "working_hours": "Information about the Working hours",
                "Unsolicited_application": "Information about Unsolicited application",
                "Internship": "Information about Internships",
                "Bachelor_Master_thesis": "Information about Bachelor/Master thesis applications",
                "Abroad_work": "Information about the work abroad",
                "External_event": "Information about external events",
                "Inhouse_projects": "Information about inhouse projects",
                "Career_advancement_promotion": "Information about career advancements",
                "Working_student": "Information about working student",
                "Internal_job_change": "Information about internal job change",
                "Travel_expense_interview": "Information about travel expenses for the interview",
                "greet":"Greet",
                "Ask_user_details":"Ask about user details",
                "User_details":"Provide your information",
                "i_am_a_bot":"Bot challenge",
                "End_chat":"stop the conversation",
                "help":"possible actions",
                "out_of_scope":"None above them"                                                
            }
        #     print(predicted_intents['name'])
    # show the top three intents as buttons to the user
            buttons = [
                {
                    "title": intent_mappings[intent['name']],
                    "payload": "/{}".format(intent['name'])
                }
                for intent in predicted_intents
            ]

    # add a "none of these button", if the user doesn't
            # agree when any suggestion
            intent_ls = []
            for intent in predicted_intents:
                intent_ls = intent
            i = 'out_of_scope'
            if intent_ls['name'] == i:
                pass
            else:
                buttons.append({
                                "title": "None of These",
                                "payload": "/out_of_scope"
                        })
            dispatcher.utter_message(text=message, buttons=buttons)
    
            return []

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return ACTION_DEFAULT_FALLBACK_NAME

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain : DomainDict
    ) -> List[EventType]:

       
        dispatcher.utter_message(response="utter_ask_rephrase")   
        # Fallback caused by TwoStageFallbackPolicy
        # last_intent = tracker.latest_message["intent"]["name"]
        # if last_intent in ["nlu_fallback", USER_INTENT_OUT_OF_SCOPE]:
        # #     return [SlotSet("feedback_value", "negative")]
        #       dispatcher.utter_message(template="utter_ask_rephrase")                    

        # # Fallback caused by Core
        # else:
        #     dispatcher.utter_message(template="utter_ask_rephrase")
        return [ConversationPaused(), UserUtteranceReverted()]

# def clean_name(name):
#     return "".join([c for c in name if c.isalpha()])

class ValidateNameForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_name_form"

    def validate_first_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""

        # If the name is super short, it might be wrong.
        name = tracker.get_slot("first_name")
        if name is str:
            if len(name) == 0:
                dispatcher.utter_message(text="That must've been a typo.")
                return {"first_name": None}
        # print(name)    
        return {"first_name": name}

    def validate_last_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `last_name` value."""

        # If the name is super short, it might be wrong.
        name = tracker.get_slot("last_name")
        if name is str:
            if len(name) == 0:
                dispatcher.utter_message(text="That must've been a typo.")
                return {"last_name": None}
        
        # first_name = tracker.get_slot("first_name")
        # if len(first_name) + len(name) < 3:
        #     dispatcher.utter_message(text="That's a very short name. We fear a typo. Restarting!")
        #     return {"first_name": None, "last_name": None}
        # print(name)      
        return {"last_name": name}

    def validate_email_address(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `last_name` value."""
        email_address = tracker.get_slot("email_address")
        # If the name is super short, it might be wrong.
        if email_address is str:
            print(email_address)
            if len(email_address) < 4:
                dispatcher.utter_message(text="That must've been a typo.")
                return {"email_address": None}
        # print(email_address)      
        return {"email_address": email_address}


class ValidateJobForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_job_form"

    # async def extract_job_level(
    #     self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    # ) -> Dict[Text, Any]:
    #     level = tracker.get_intent_of_latest_message()
    #     # print('level')
    #     if level == 'student':
    #         # print('student')
    #         return {"job_level": 'Student'}
    #         # return{"job_level_student" : True}

    #     if level == 'Graduate':
    #         # print('Graduate')
    #         return {"job_level": 'Graduate'}
    #         # return{"job_level_graduate" : True}

    #     if level == 'Working Professional':
    #         # print('Working Professional')
    #         return {"job_level": 'Working_professional'}
    #         # return{"job_level_Working Professional" : True}   


    def validate_job_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""
        level = tracker.get_slot("job_type")

        # If the name is super short, it might be wrong.
        # level_student = tracker.get_slot("job_level_student")
        # level_graduate = tracker.get_slot("job_level_graduate")
        # level_working_professional = tracker.get_slot("job_level_Working Professional")

        # level = tracker.get_intent_of_latest_message()

        
        # if level_student is True :
        #     return [SlotSet("job_level", 'Student')]
        #     # return {"job_level": 'Student'}

        # if level_graduate is True :
        #     return [SlotSet("job_level", 'Graduate')]
        #     # return {"job_level": 'Graduate'}

        # if level_working_professional is True :
        #     return [SlotSet("job_level", 'Working_professional')]
        #     # return {"job_level": 'Working_professional'}
        print(level)
        return[SlotSet("job_type", level)]

    def validate_job_domain(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `JOb domain` value."""

        # If the name is super short, it might be wrong.
        domain = tracker.get_slot("job_domain")
        
        # if len(domain) == 0:
        #     dispatcher.utter_message(text="That must've been a typo.")
        #     return {"job_domain": None}

        # if len(first_name) + len(name) < 3:
        #     dispatcher.utter_message(text="That's a very short name. We fear a typo. Restarting!")
        #     return {"first_name": None, "last_name": None}
        # print(name)      
        return {"job_domain": domain}

    def validate_job_keywords(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        """Validate `last_name` value."""

        job_keywords = tracker.get_slot("job_keywords")
        # If the name is super short, it might be wrong.
        # if years_exp < 0:
        #     dispatcher.utter_message(text="That must've been a typo.")
        #     return {"years_experience": None}

        # if years_exp.isalpha():
        #     dispatcher.utter_message(text="Please enter a valid number")
        #     return {"years_experience": None}  

             
        return {"job_keywords": job_keywords}

    # def validate_job_field_form(
    #     self,
    #     slot_value: Any,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: DomainDict,
    # ) -> Dict[Text, Any]:
    #     """Validate `last_name` value."""
        
    #     # If the name is super short, it might be wrong.
    #     dispatcher.utter_message(response = "utter_ask_job_form_confirmation_search")

    #     affirm = tracker.get_slot("affirm_job")

    #     if affirm == "Yes":
    #         dispatcher.utter_message(response = "utter_remember")
        
    #     else :
    #         return {"years_experience": None, "job_level": None, "job_level": None}

# class ActionAskJobSearchConfirmation(Action):

#     def name(self) -> Text:
#         return "action_ask_job_search_confirmation"

#     # async def extract_job_form_confirmation_search(
#     #     self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
#     # ) -> Dict[Text, Any]:
        
#     #     # dispatcher.utter_message(response = "utter_ask_job_form_confirmation_search")
#     #     intent = tracker.get_intent_of_latest_message()
#     #     return {"job_form_confirmation_search": intent == "affirm_job"}
#     #     # return {"job_form_confirmation_search": intent == "affirm_job"}
         

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         """Validate `first_name` value."""

#         # job_level = tracker.get_slot("job_level")
#         # job_domain = tracker.get_slot("job_domain")
#         # years_exp = tracker.get_slot("years_experience")

#         intent = tracker.get_intent_of_latest_message()
#         print(intent)
#         return {"job_form_confirmation_search": intent == "affirm_job"}

#         # intent = tracker.get_slot("job_form_confirmation_search")
#         # print(intent)
#         # return[intent]
            

class ActionGetJobSearchConfirmation(Action):

    def name(self) -> Text:
        return "action_get_job_search_confirmation"

    # def run(self, dispatcher: CollectingDispatcher,
    #         tracker: Tracker,
    #         domain:  DomainDict) -> List[Dict[Text, Any]]:
    
    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        job_type = tracker.get_slot("job_type")
        job_domain = tracker.get_slot("job_domain")
        job_keywords = tracker.get_slot("job_keywords")

        intent = tracker.get_slot("job_form_clear_field")
        job_found_dict = {}
        
        if intent is False :
            print('Searching for the job')
            job_found = job_search(job_type, job_domain, job_keywords)

            if type(job_found) is list:
                job_found_dict = job_found[0]
                
            elif type(job_found) is dict:
                job_found_dict = job_found

            else:
                msg = job_found
                dispatcher.utter_message(text = msg)

            j = 1

            for key, value in job_found_dict.items():
                
                # job_buttons.append({'payload': ' /job_results{"id": "' + key +'"}','title': value})
                    dispatcher.utter_message(text = str(j) + ' : ' + '[' + value + ']' +'('+ 'https://dornier-group.jobs.personio.com/job/' + key + ')')
                    j = j + 1

            
            return []
            
                # dispatcher.utter_message(text = 'Cancelling job search')
            #     job_buttons.append({'title': value, 'payload': '/Job_ticket'})
            # dispatcher.utter_message(text = 'job_found : ', buttons = job_buttons)
            
            
            # id_slot = tracker.get_slot("id") 
            # print(id_slot)
            # print(job_buttons
            

        else:
            print('Not searching for a job')
            dispatcher.utter_message(text = 'Cancelling job search')
            return [SlotSet("job_type", None), SlotSet("job_domain", None), SlotSet("job_keywords", None), SlotSet("job_form_confirmation_search", None)]

        # dispatcher.utter_message(text = 'job_found : ', buttons = job_buttons)
        # return []
        


def job_search( slot_job_type, slot_job_domain, slot_job_keywords):

    tree = ET.parse('job.xml')
    root = tree.getroot()

    print(root.tag)

    job_available_id = []
    job_available_name = []

    # if int(slot_years_exp)<1:
    #     years_of_experience = 'lt-1'

    # elif int(slot_years_exp) < 2:
    #     years_of_experience =  '1-2'

    # elif int(slot_years_exp) < 5:
    #     years_of_experience =  '2-5'

    # elif int(slot_years_exp) < 7:
    #     years_of_experience =  '5-7'

    # else:
    #     years_of_experience =  '7-10'
    

    # if slot_job_level == 'student':
    #     level = 'entry-level'

    # elif slot_job_level == 'Graduate':
    #     level = 'entry-level'

    # elif slot_job_level == 'Working Professional':
    #     level = 'experienced'


    i = 0
    j = 0
    
    dict = {}

    for position in root.findall('position'):

        type = position.find('employmentType').text
        domain = position.find('occupationCategory').text
        keywords = position.find('name').text

        if type == slot_job_type and slot_job_keywords in keywords and domain == slot_job_domain:
            print('element found')

            j = 1

            for id in position.iter():

                if id.tag == 'id':
                    # print(id.tag)
                    id_job = id.text

                if id.tag == 'name' and slot_job_keywords in id.text:
                    # print(id.text)
                    job_name = id.text
                # print(names[0])
            
            job_available_id.append(id_job)
            # job_available_name.append(job_name)
            # id = root[i][0].text
            # job_name = root[i][4].text
            # job_available_id.append(id)
            # job_available_name.append(job_name)

            # new_string = str(j) + ' :' +' https://dornier-group.jobs.personio.com/job/' + id + ' : ' + job_name
            # new_list.append(new_string)
            dict[id_job] = job_name
        else:
            # print('job not found')
            # return("job not found")
            pass
            
        i = i+1
    


    string = 'https://dornier-group.jobs.personio.com/job/'
    my_new_list = [string + x for x in job_available_id]

    list= [job_available_name, my_new_list]

    if len(job_available_id) == 0:
        return("job not found")
    else:
        print(dict)
        return dict
        # for a in zip(*list): 
        #     j = j+1
        #     print(j,':', *a)
        #     return(j,':', *a)

    # for a in zip(*list_of_lists):
    #     print(*a)

    # for a in zip(*list): 
    #     j = j+1
    #     return(j,':', *a)


class ActionJobResults(Action):

    def name(self) -> Text:
        return "action_job_results"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain:  DomainDict) -> List[Dict[Text, Any]]:
        print("job_result action started")
        intent = tracker.get_intent_of_latest_message()
        slot_id = tracker.get_slot("id")
        if intent == 'job_results' :
            print('slot was set and results can be shown')
            print(slot_id)
            dispatcher.utter_message(response = "utter_job_results")
            return []
        else:
            print('Not searching for a job')
            return[]

class ActionAskJobParamsClear(Action):

    def name(self) -> Text:
        return "action_ask_job_params_clear"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain:  DomainDict) -> List[Dict[Text, Any]]:
        print("field clearing started")
       
        slot_id = tracker.get_slot("job_form_clear_field")

        if slot_id is True:
            
            dispatcher.utter_message(response = "utter_ask_clear_params_job")
            return []
        else:
            dispatcher.utter_message(text = "Thanks for confirming! Proceeding with the search")
            print('Not searching for a job')
            return[]       

class ActionJobParamsClear(Action):

    def name(self) -> Text:
        return "action_job_params_clear"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain:  DomainDict) -> List[Dict[Text, Any]]:
        print("field clearing ****executing***")
       
        slot_params = tracker.get_slot("job_form_clear_field_params")

        if slot_params == 'clear_all':
            
            dispatcher.utter_message(text = "Clearing All Parameters")
            return [SlotSet("job_type", None), SlotSet("job_domain", None), SlotSet("job_keywords", None), SlotSet("job_form_confirmation_search", None)]
        else:
            dispatcher.utter_message(text = "Cleared the requested field")
            print('Not searching for a job')
            return[SlotSet(slot_params, None), SlotSet("job_form_confirmation_search", None)]  


class ActionAskNameCorrect(Action):

    def name(self) -> Text:
        return "action_ask_name_correct"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain:  DomainDict) -> List[Dict[Text, Any]]:
        print("field clearing started")
       
        slot_id = tracker.get_slot("name_form_clear_field")

        if slot_id is True:
            
            dispatcher.utter_message(text = "Thanks for confirming!")
            return []
        else:
            dispatcher.utter_message(response = 'utter_ask_clear_params_name')
            
            return[]       

class ActionNameParamsClear(Action):

    def name(self) -> Text:
        return "action_name_params_clear"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain:  DomainDict) -> List[Dict[Text, Any]]:
        print("field clearing ****executing***")
       
        slot_params = tracker.get_slot("name_form_clear_field_params")

        if slot_params == 'all_name':
            
            dispatcher.utter_message(text = "Clearing All Parameters")
            return [SlotSet("first_name", None), SlotSet("last_name", None), SlotSet("email_address", None)]
        else:
            dispatcher.utter_message(text = "Cleared the requested field")
            print('Not searching for a job')
            return[SlotSet(slot_params, None)]  


class ActionSaveConversation(Action):

    def name(self) -> Text:
        return "action_save_conversation"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain:  DomainDict) -> List[Dict[Text, Any]]:

        conn = psycopg2.connect("host=db_pgsql dbname=Rasa user=postgres password=7644")

        cur = conn.cursor()

        conversation = tracker.events
        
        dt_time = dt.datetime.now()
        # cur.execute(sql.SQL("insert into {table} values (%s, %s)").format(table=sql.Identifier('my_table')),[10, 20])

        sql_table_create = str('"CREATE TABLE '+ 'table_test' + ' (id serial PRIMARY KEY, Intent varchar, user_input varchar, Bot_reply varchar, entity_name varchar, entity_value varchar, action varchar);"')

        # cur.execute(sql_table_create)
        time = str(dt_time)
        cur.execute(sql.SQL("CREATE TABLE {table} (id serial PRIMARY KEY, Intent varchar, user_input varchar, Bot_reply varchar, entity_name varchar, entity_value varchar, action varchar);").format(table=sql.Identifier(time)))

        print("table created")
        

        for i in conversation:
            if i['event'] == 'user':
                # SQL_intent = "INSERT INTO authors (intent) VALUES (%s);"  
                # SQL_intent = str('"INSERT INTO ' + str(dt_time) + ' (Intent) VALUES (%s);"')
                # SQL_user_convo = str('"INSERT INTO ' + str(dt_time) + ' (user_input) VALUES (%s);"')
                intent_convo = i['parse_data']['intent']['name']
                user_convo = i['text']
                
                # cur.execute(SQL_intent, str(intent_convo))
                cur.execute(sql.SQL("INSERT INTO {table} (Intent) VALUES (%s);").format(table=sql.Identifier(str(dt_time))),[str(intent_convo)])
                cur.execute(sql.SQL("INSERT INTO {table} (user_input) VALUES (%s);").format(table=sql.Identifier(str(dt_time))),[str(user_convo)])

                conn.commit()
                # print('user: {}'.format(i['text']))
                if len(i['parse_data']['entities']) > 0:
                    # SQL = "INSERT INTO authors (name) VALUES (%s);"
                    # SQL_entity_type = str('"INSERT INTO ' + str(dt_time) + ' (entity_name) VALUES (%s);"')
                    # SQL_entity_value = str('"INSERT INTO ' + str(dt_time) + ' (entity_value) VALUES (%s);"')
                    entity_type = i['parse_data']['entities'][0]['entity']
                    entity_value = i['parse_data']['entities'][0]['value']

                    cur.execute(sql.SQL("INSERT INTO {table} (entity_name) VALUES (%s);").format(table=sql.Identifier(str(dt_time))),[str(entity_type)])
                    cur.execute(sql.SQL("INSERT INTO {table} (entity_value) VALUES (%s);").format(table=sql.Identifier(str(dt_time))),[str(entity_value)])

                    conn.commit()
                else:
                    #insert blank to handle blank user convos
                    pass
            elif i['event'] == 'bot':
                print('Bot: {}'.format(i['text']))
                try:
                    # SQL_action_bot = str('"INSERT INTO ' + str(dt_time) + ' (action) VALUES (%s);"')
                    # SQL_bot_convo = str('"INSERT INTO ' + str(dt_time) + ' (Bot_reply) VALUES (%s);"')

                    action_bot = i['metadata']['utter_action']
                    bot_convo = i['text']

                    cur.execute(sql.SQL("INSERT INTO {table} (action) VALUES (%s);").format(table=sql.Identifier(str(dt_time))),[str(action_bot)])
                    cur.execute(sql.SQL("INSERT INTO {table} (Bot_reply) VALUES (%s);").format(table=sql.Identifier(str(dt_time))),[str(bot_convo)])

                    conn.commit()
      
                except KeyError:
                    pass

        sql_query = sql.SQL("COPY (SELECT * FROM {table}) TO STDOUT WITH CSV HEADER").format(table=sql.Identifier(time))
        
        time = time.replace(' ','-')

        time = time.replace('.','-')

        time = time.replace(':','-')

        name = time + ".csv"

        chat_path = 'chat_hist'

        if os.path.exists(chat_path):
            pass
        else:
            os.makedirs(chat_path)

        new_file_path = os.path.join(chat_path, name)

        with open(new_file_path, "a") as file:
            cur.copy_expert(sql_query, file)    
        
        cur.close()
        # dispatcher.utter_message(text="All Chats saved.")

        return[]