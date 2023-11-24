# Zde jsou vlastní akce, které se volající při spuštění pravidla nebo příběhu

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher
import mysql.connector as mc
import bcrypt
import random
import string
import re

import datetime
from datetime import datetime, timedelta
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dateutil import parser
import pickle

find_user_phone = 456230140
find_message_owner = 789102134

# Akce pro získání jména uživatele
class ActionGetUserName(Action):

     def name(self) -> Text:
        return "action_get_user_name"

     def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
         try: 
            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
             )

            cur = db.cursor()
            select_query = "SELECT name FROM users where phone_number = (%s)"
            data = (find_user_phone,)
            cur.execute(select_query, data)

            user = cur.fetchone()
            if user:
                user_name = user[0]
                dispatcher.utter_message(text= "Hello, " + user_name + ".")
            else:
                dispatcher.utter_message(text="I apologize, I couldn't find your name in the database.")

            db.close()
         except Exception as e:
             print("Error: ", e)

         return []

# Akce pro získání počtu nových zpráv
class ActionCheckUnreadMessages(Action):

    def name(self) -> Text:
        return "action_check_unread_messages"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        delete_old_messages()
        update_spam()

        try:
            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
            )
            cur = db.cursor()
            select_query = "SELECT COUNT(*) FROM messages WHERE label = 'unread' AND category NOT IN ('bin', 'spam')"
            cur.execute(select_query)

            unread_count = cur.fetchone()[0]

            if unread_count > 0:
               if unread_count == 1:
                  dispatcher.utter_message(text=f"You have {unread_count} new message.")
               else:
                  dispatcher.utter_message(text=f"You have {unread_count} new messages.")
            else:
                dispatcher.utter_message(text="No new messages.")

            db.close()
        except Exception as e:
            print("Error: ", e)

        return []

# Metoda, která zajišťuje mazání zpráv
def delete_old_messages():
        try:
            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
            )  
            cur = db.cursor()
            delete_query = "DELETE FROM messages WHERE date_send < DATE_SUB(NOW(), INTERVAL 20 DAY)"
            cur.execute(delete_query)

            db.commit()
            db.close()
        except Exception as e:
            print("Error: ", e)
        return []   

# Akce pro čtení nové zprávy 
class ActionReadUnreadMessage(Action):

     def name(self) -> Text:
        return "action_read_new_messages"

     def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:     
         delete_old_messages()
         update_spam()

         try: 
            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
             )
            cur = db.cursor()
            select_query = "SELECT message_text, id_message, number_sender FROM messages m LEFT JOIN users u ON u.id_user = m.id_user WHERE u.phone_number= (%s) and m.label = 'unread' and m.category NOT IN ('bin', 'spam') ORDER BY m.date_send"
            data = (find_user_phone,)
            cur.execute(select_query, data)
            messages = cur.fetchall()
            if messages:
                first_id = messages [0][1]
                first_message = messages[0][0]
                number_sender = messages[0][2]
                global find_message_owner
                find_message_owner = first_id
                cur = db.cursor()
                select_query = "SELECT c.name, c.phone_number FROM contacts c LEFT JOIN users u ON u.id_user = c.id_user LEFT JOIN messages m ON u.id_user = m.id_user WHERE u.phone_number= (%s) AND (m.number_sender = c.phone_number) AND m.id_message = (%s)"
                data = (find_user_phone, first_id)
                cur.execute(select_query, data)
                contacts = cur.fetchall()
                if contacts:
                        first_name = contacts [0][0]
                        first_number = contacts [0][1]
                        dispatcher.utter_message(text=f"This is a message from {first_name}: {first_message}")

                        cur = db.cursor()
                        select_query = "UPDATE messages m INNER JOIN users u ON m.id_user = u.id_user SET m.label = 'read' WHERE m.id_message = (%s) and u.phone_number = (%s)"
                        data = (first_id, find_user_phone)
                        cur.execute(select_query, data)
                        db.commit()
                else:
                        dispatcher.utter_message(text=f"This is a message from unknown number {number_sender}: {first_message}")
                        cur = db.cursor()
                        select_query = "UPDATE messages m INNER JOIN users u ON m.id_user = u.id_user SET m.label = 'read' WHERE m.id_message = (%s) and u.phone_number = (%s)"
                        data = (first_id, find_user_phone)
                        cur.execute(select_query, data)
                        db.commit()
            else:
                dispatcher.utter_message(text="I apologize, I couldn't find any messages for you.")

            db.close()
         except Exception as e:
             print("Error: ", e)

         return []

# Akce pro čtení prioritní zprávy
class ActionReadPriorityMessage(Action):

     def name(self) -> Text:
        return "action_read_priority_message"

     def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:    
         delete_old_messages()
         update_spam()

         try: 
            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
             )
            priority1 = '%urgent%'
            priority2 = '%fast%'
            priority3 = '%important%'
            cur = db.cursor()
            select_query = "SELECT message_text, id_message, number_sender FROM messages m LEFT JOIN users u ON u.id_user = m.id_user LEFT JOIN contacts c ON u.id_user = c.id_user WHERE u.phone_number = (%s) AND (m.number_sender = c.phone_number) AND m.label = 'unread' AND m.category NOT IN ('bin', 'spam')  AND (m.message_text LIKE %s OR m.message_text LIKE %s OR m.message_text LIKE %s) ORDER BY CASE WHEN m.message_text LIKE %s THEN 1 WHEN m.message_text LIKE %s THEN 2 ELSE 3 END, m.date_send "
            data = (find_user_phone, priority1, priority2, priority3, priority1, priority2)
            cur.execute(select_query, data)
            messages = cur.fetchall()
            if messages:
                prioritynumber = len(messages)
                dispatcher.utter_message(text=f"You have {prioritynumber} high priority messages.")
                first_id = messages [0][1]
                first_message = messages[0][0]
                number_sender = messages[0][2]
                global find_message_owner
                find_message_owner = first_id
                cur = db.cursor()
                select_query = "SELECT c.name, c.phone_number FROM contacts c LEFT JOIN users u ON u.id_user = c.id_user LEFT JOIN messages m ON u.id_user = m.id_user WHERE u.phone_number= (%s) AND (m.number_sender = c.phone_number) AND m.id_message = (%s)"
                data = (find_user_phone, first_id)
                cur.execute(select_query, data)
                contacts = cur.fetchall()
                if contacts:
                        first_name = contacts [0][0]
                        first_number = contacts [0][1]
                        dispatcher.utter_message(text=f"This is a message from {first_name}: {first_message}")

                        cur = db.cursor()
                        select_query = "UPDATE messages m INNER JOIN users u ON m.id_user = u.id_user SET m.label = 'read' WHERE m.id_message = (%s) and u.phone_number = (%s)"
                        data = (first_id, find_user_phone)
                        cur.execute(select_query, data)
                        db.commit()
                else:
                        dispatcher.utter_message(text=f"This is a message from unknown number {number_sender}: {first_message}")
                        cur = db.cursor()
                        select_query = "UPDATE messages m INNER JOIN users u ON m.id_user = u.id_user SET m.label = 'read' WHERE m.id_message = (%s) and u.phone_number = (%s)"
                        data = (first_id, find_user_phone)
                        cur.execute(select_query, data)
                        db.commit()
            else:
                dispatcher.utter_message(text="You have no priority messages.")

            db.close()
         except Exception as e:
             print("Error: ", e)
         return []        

# Akce pro zopakování poslední botovi zprávy
class ActionRepeatBotMessage(Action):

     def name(self) -> Text:
        return "action_repeat_bot_message"

     def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        bot_event = next(e for e in reversed(tracker.events) if e["event"] == "bot")
        if bot_event:
            bot_message = bot_event["text"]
            dispatcher.utter_message(bot_message)
        else:
            dispatcher.utter_message(text="No message to repeat.")
        return []

# Akce pro čtení zpráv dle jména    
class ActionNameFromMessage(Action):

     def name(self) -> Text:
        return "action_name_from_message"
        
     def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
            delete_old_messages()
            update_spam()    
            try: 
                db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
                )
                latest_message = tracker.latest_message
                text_after_from = latest_message.get("text").split("from", 1)[1].strip()
                if text_after_from != "":
                    cur = db.cursor()
                    select_query = "SELECT c.name, c.phone_number FROM contacts c LEFT JOIN users u ON u.id_user = c.id_user WHERE u.phone_number= (%s) AND (LOWER(c.name) = LOWER(%s))"
                    data = (find_user_phone, text_after_from)
                    cur.execute(select_query, data)
                    contacts = cur.fetchall()
                    if contacts:
                        first_name = contacts [0][0]
                        first_number = contacts [0][1]
                        select_query = "SELECT message_text, id_message FROM messages m LEFT JOIN users u ON u.id_user = m.id_user WHERE u.phone_number= (%s) and m.number_sender= (%s) and m.label = 'unread' and m.category NOT IN ('bin', 'spam') ORDER BY m.date_send"
                        data = (find_user_phone, first_number)
                        cur.execute(select_query, data)
                        messages = cur.fetchall()
                        if messages:
                         first_id = messages [0][1]
                         first_message = messages[0][0]
                         dispatcher.utter_message(text=f"This is a message from {first_name}: {first_message}")
                         global find_message_owner
                         find_message_owner = first_id
                         cur = db.cursor()
                         select_query = "UPDATE messages m INNER JOIN users u ON m.id_user = u.id_user SET m.label = 'read' WHERE m.id_message = (%s) and u.phone_number = (%s)"
                         data = (first_id, find_user_phone)
                         cur.execute(select_query, data)
                         db.commit()
                    else:
                        dispatcher.utter_message(text=f"I apologize, I couldn't find any messages from {text_after_from}.")

                db.close()
            except Exception as e:
                print("Error: ", e)
                return []  
            return []    

# Akce pro přesunutí nepřečtených zpráv do koše od jednoho volajícího              
class ActionDeleteMessage(Action):

     def name(self) -> Text:
        return "action_delete_message"

     def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
         try: 
            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
             )
            cur = db.cursor()
            select_query = "SELECT number_sender FROM messages WHERE id_message = (%s)"
            data = (find_message_owner,)
            cur.execute(select_query, data)
            user_info = cur.fetchone()
            if user_info:
                user_phone = user_info[0]
                category = "bin"

                cur = db.cursor()
                update_query = "UPDATE messages m SET m.category = %s WHERE m.number_sender = (%s)"
                data = (category, user_phone)
                cur.execute(update_query, data)
                db.commit()
                dispatcher.utter_message(text=f"All messages from {user_phone} have been removed and put to the bin. If you wish to undo this action type restore messages.")
            else:
                dispatcher.utter_message(text="I apologize I could not delete messages, there is no caller number.")

            db.close()
         except Exception as e:
             print("Error: ", e)

         return []       

# Akce pro vrácení přesunutých zpráv z koše 
class ActionRestoreMessage(Action):

     def name(self) -> Text:
        return "action_restore_message"

     def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
         try: 
            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
             )
            cur = db.cursor()
            select_query = "SELECT number_sender FROM messages WHERE id_message = (%s)"
            data = (find_message_owner,)
            cur.execute(select_query, data)
            user_info = cur.fetchone()
            if user_info:
                user_phone = user_info[0]
                category = ""

                cur = db.cursor()
                update_query = "UPDATE messages m SET m.category = %s WHERE m.number_sender = (%s)"
                data = (category, user_phone)
                cur.execute(update_query, data)
                db.commit()
                dispatcher.utter_message(text=f"All messages from {user_phone} have been restored.")
            else:
                dispatcher.utter_message(text="I apologize I could not restore messages, there are no messages to restore.")

            db.close()
         except Exception as e:
             print("Error: ", e)

         return []          

# Akce pro zavolaní zpět volajícímu
class ActionCallBack(Action):
    def name(self) -> Text:
        return "action_call_back"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:

            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
            )

            cur = db.cursor()
            select_query = "SELECT number_sender FROM messages WHERE id_message = (%s)"
            data = (find_message_owner,)
            cur.execute(select_query, data)
            user_info = cur.fetchone()

            if user_info:
                user_phone = user_info[0]
                cur = db.cursor()
                select_query = "SELECT name FROM contacts WHERE phone_number = (%s)"
                data = (user_phone,)
                cur.execute(select_query, data)
                user_name = cur.fetchone()
                if user_name:
                    user_name_text = user_name[0]
                    dispatcher.utter_message(text=f"Calling back {user_name_text}")
                else:    
                    dispatcher.utter_message(text=f"Calling back {user_phone}")

            else:
                dispatcher.utter_message(text="I apologize I could not call back, there is no number to call.")

            db.close()
        except Exception as e:
            print("Error: ", e)

        return []     

# Akce pro zablokování volajícího     
class ActionBlockNumber(Action):
    def name(self) -> Text:
        return "action_block_number"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:

            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
            )

            cur = db.cursor()
            select_query = "SELECT number_sender FROM messages WHERE id_message = (%s)"
            data = (find_message_owner,)
            cur.execute(select_query, data)
            user_info = cur.fetchone()

            if user_info:
                user_phone = user_info[0]
                
                try:
                    cur = db.cursor()
                    insert_query = "INSERT INTO blacklist (id_user, phone_number_sender) SELECT DISTINCT u.id_user, m.number_sender FROM users u JOIN messages m ON u.id_user = m.id_user LEFT JOIN blacklist b ON u.id_user = b.id_user AND m.number_sender = b.phone_number_sender WHERE (m.number_sender = (%s) AND u.phone_number = (%s)) AND b.id_user IS NULL"

                    
                    data = (user_phone, find_user_phone)
                    cur.execute(insert_query, data)   
                    db.commit()

                    cur = db.cursor()
                    category = "spam"
                    update_query = "UPDATE messages m SET m.category = %s WHERE m.number_sender = (%s)"
                    data = (category, user_phone)
                    cur.execute(update_query, data)
                    db.commit()

                    dispatcher.utter_message(text=f"Number {user_phone} has been blocked and added on black list.") 
                except Exception as e:
                    print("Error: ", e)
                    dispatcher.utter_message(text=f"No number blocked or added on black list.")

            else:
                dispatcher.utter_message(text="I apologize I could not block or add the number on blacklist.")

            db.close()
        except Exception as e:
            print("Error: ", e)

        return []  

# Akce pro získání seznamu blokovaných čísel    
class ActionGetBlacklistedNumbers(Action):

     def name(self) -> Text:
        return "action_get_blacklisted_numbers"

     def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
         try: 
            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
             )

            cur = db.cursor()
            select_query = "SELECT phone_number_sender FROM blacklist"
            cur.execute(select_query)

            phone_number = [row[0] for row in cur.fetchall()]
            if phone_number:
                response = "Here are phone numbers you have on your blacklist: " + ", ".join(phone_number) + ". Messages from these numbers are automatically moved to spam."
                dispatcher.utter_message(response)
            else:
                dispatcher.utter_message(text="You have 0 phone numbers on your blacklist.")

            db.close()
         except Exception as e:
             print("Error: ", e)

         return []    

# Akce pro odstranění čísla ze seznamu blokovaných čísel      
class ActionRemoveBlacklistedNumbers(Action):

     def name(self) -> Text:
        return "action_remove_blacklisted_number"

     def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
         try: 
            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
             )
            number_blacklist = tracker.get_slot("number_blacklist") 
            cur = db.cursor()
            delete_query = "DELETE FROM blacklist WHERE phone_number_sender = (%s) "
            data = (number_blacklist,)
            cur.execute(delete_query, data)
            db.commit()


            cur = db.cursor()
            select_query = "SELECT phone_number_sender FROM blacklist WHERE phone_number_sender = (%s)"
            data = (number_blacklist,)
            cur.execute(select_query, data)

            phone_number = cur.fetchone()
            db.close()

            if phone_number:
                dispatcher.utter_message(text=f"Could not remove {number_blacklist} from blacklist.")
            else:
                dispatcher.utter_message(text=f"Number has been removed from blacklist. You can now receive messages from {number_blacklist}.")
                
         except Exception as e:
             print("Error: ", e)
             dispatcher.utter_message(text=f"Error occured while trying to remove {number_blacklist} from blacklist.")
         return []         

# Metoda pro označení a přesunutí zpráv do spamu dle seznamu blokovaných čísel    
def update_spam():
        try:
            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
            )  
            cur = db.cursor()
            category = "spam"
            update_query = "UPDATE messages m SET m.category = %s WHERE EXISTS (SELECT 1 FROM blacklist b WHERE b.phone_number_sender = m.number_sender)"
            data = (category,)
            cur.execute(update_query, data)

            db.commit()
            db.close()
        except Exception as e:
            print("Error: ", e)
        return []          

# Akce pro přehrání uvítací zprávy    
class ActionPlayGreetingMessage(Action):

     def name(self) -> Text:
        return "action_play_greeting_message"

     def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
         try: 
            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
             )

            cur = db.cursor()
            select_query = "SELECT greeting_message FROM users WHERE phone_number= (%s)"
            data = (find_user_phone,)
            cur.execute(select_query, data)
            greeting = cur.fetchone()
            
            if greeting:
                text_greeting = greeting[0]
                clean_text_greeting = text_greeting.strip("(')")
                dispatcher.utter_message(text=f"Your greeting message is: {clean_text_greeting}")
            else:
                dispatcher.utter_message(text="I apologize, you have no greeting message set up.")
            db.close()
         except Exception as e:
            print("Error: ", e)
         return []

# Akce pro nastavení uvítací zprávy        
class ActionSetGreetingMessage(Action):

     def name(self) -> Text:
        return "action_set_greeting_message"

     def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
         greeting_message = tracker.latest_message.get("text")    
         try: 
            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
             )
            
            cur = db.cursor()
            select_query = "UPDATE users SET greeting_message = (%s) WHERE phone_number= (%s)"
            data = (greeting_message, find_user_phone)
            cur.execute(select_query, data)
            db.commit()
            db.close()
            dispatcher.utter_message(text=f"Your new greeting message is: {greeting_message}")

         except Exception as e:
            dispatcher.utter_message(text="I apologize, you have no greeting message set up.")
            print("Error: ", e)

         return []

# Akce pro ověření pinu      
class ActionCheckPin(Action):
    def name(self) -> Text:
        return "action_check_pin"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
            
         try: 
            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
             )

            cur = db.cursor()
            select_query = "SELECT pin FROM users where phone_number = (%s)"
            data = (find_user_phone,)
            cur.execute(select_query, data)

            pin = cur.fetchone()
            db.close()
            if pin:
                pin_hashed = pin[0]
                pin_user_input = tracker.get_slot("pin") 
                
                if bcrypt.checkpw(pin_user_input.encode('utf-8'),pin_hashed.encode('utf-8')):
                 dispatcher.utter_message(text= "Your old pin is correct.")
                 dispatcher.utter_message(text= "Please tell a new pin: ")
                 return[SlotSet("old_pin",True)]
                else:
                     dispatcher.utter_message(text="The pin you have provided is wrong.")
                     return[SlotSet("old_pin",False), SlotSet("pin_verified", False)]
            else:
                dispatcher.utter_message(text="You have no pin set.")

         except Exception as e:
             print("Error: ", e)

         return []
    
# Akce pro zadání nového pinu      
class ActionNewPin(Action):

     def name(self) -> Text:
        return "action_new_pin"

     def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        

         try: 
            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
             )
            
            pin_user_input = tracker.get_slot("pin") 
            pin_user_encoded = pin_user_input.encode('utf-8')

            salt = bcrypt.gensalt()
            pin_hashed = bcrypt.hashpw(pin_user_encoded, salt)

            

            cur = db.cursor()
            select_query = "UPDATE users SET pin = (%s) WHERE phone_number= (%s)"
            data = (pin_hashed, find_user_phone)
            cur.execute(select_query, data)
            db.commit()
            dispatcher.utter_message(text= "Pin changed.")
         except Exception as e:
             dispatcher.utter_message(text= "Error occured, pin was not changed.")
             print("Error: ", e)
         return []

# Akce pro potvrzení nového pinu          
class ActionConfirmResetPin(Action):

     def name(self) -> Text:
        return "action_confirm_rest_pin"

     def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
         try: 
            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
             )

            cur = db.cursor()
            select_query = "SELECT phone_number FROM users where phone_number = (%s)"
            data = (find_user_phone,)
            cur.execute(select_query, data)

            phone_number = cur.fetchone()
            if phone_number:
                phone_number = phone_number[0]
                dispatcher.utter_message(text= "A reset pin will be sent to your phone number: " + phone_number + ".")
                dispatcher.utter_message(text= "Please confirm that you want your pin to be reset.")
            else:
                dispatcher.utter_message(text="I apologize, I couldn't find your phone number in the database.")

            db.close()
         except Exception as e:
             print("Error: ", e)

         return []

# Akce pro reset pinu        
class ActionResetPin(Action):

     def name(self) -> Text:
        return "action_reset_pin"

     def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
         try: 
            db = mc.connect(
                host="host.docker.internal",
                user="root",
                password="",
                database="rasa_assistant_db"
             )

            chars_for_random = string.digits
            reseted_pin = ''.join(random.choice(chars_for_random) for _ in range(6))
           
            pin_reseted_encoded = reseted_pin.encode('utf-8')
            salt = bcrypt.gensalt()
            pin_hashed = bcrypt.hashpw(pin_reseted_encoded, salt)

            cur = db.cursor()
            update_query = "UPDATE users SET pin = (%s) WHERE phone_number= (%s)"
            data = (pin_hashed, find_user_phone)
            cur.execute(update_query, data)
            db.commit()
            dispatcher.utter_message(text= "Pin reseted.")
            dispatcher.utter_message(text= "Your pin is: " + reseted_pin + " ,")
            dispatcher.utter_message(text= "please do not forget to change your pin next time.")

         except Exception as e:
             dispatcher.utter_message(text= "Error occured, pin was not changed.")
             print("Error: ", e)
         return []

# Akce ověřující formát nového pinu    
class ActionValidPin(Action):
    def name(self) -> Text:
        return "action_valid_pin"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        

            pin_validation = tracker.get_slot("pin") 

            if (len(pin_validation)) < 6:
              dispatcher.utter_message(text="Pin must be at least 6 digits long.")
              dispatcher.utter_message(text="Please think of a new pin:")
              return[SlotSet("valid_pin",False)]   
            
            elif re.match(r'^\d{6,}$', pin_validation):
                return[SlotSet("valid_pin",True)]  
            else:
              dispatcher.utter_message(text="Pin must be at least 6 digits long.")
              dispatcher.utter_message(text="Pin must only consist of digits. Other characters are not allowed.")
              dispatcher.utter_message(text="Please think of a new pin:")
              return[SlotSet("valid_pin",False)]  

# Akce pro přidání události do kalendáře
class AddToCalendar(Action):

    def name(self) -> Text:
        return "action_add_calendar"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        event_name = tracker.get_slot("event_name")
        event_time = tracker.get_slot("event_time")
        event_date = tracker.get_slot("event_date")
        event_location = tracker.get_slot("event_location")

        if event_name and event_time and event_date:
            try:
                reminder_datetime = parser.parse(f"{event_date} {event_time}", fuzzy=True)

            except ValueError:
                dispatcher.utter_message("I'm sorry, I couldn't understand the time. Please provide a valid time.")
                return []

            add_event(event_name, reminder_datetime, event_location)
            if event_location:
                reminder_text = f"Sure! I've added {event_name} at {event_time} on {event_date} and location {event_location} to your google calendar."
                dispatcher.utter_message(reminder_text)
                return [SlotSet("event_location", None)]
            elif event_location is None:
                reminder_text = f"Sure! I've added {event_name} at {event_time} on {event_date} to your google calendar."
                dispatcher.utter_message(reminder_text)
                return [SlotSet("event_location", None)]
        else:
            dispatcher.utter_message("I'm sorry, I couldn't extract all the necessary information for adding event to calendar. If you need help ask: help calendar")

        return []
    
SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = 'credentials.json'

# Metoda pro přístup ke kalendáři
def get_calendar_service():
   creds = None

   if os.path.exists('token.pickle'):
       with open('token.pickle', 'rb') as token:
           creds = pickle.load(token)
   # Pokud nejsou žádné validní přihlašovací údaje, tak potvrzení přístupu od uživatele
   if not creds or not creds.valid:
       if creds and creds.expired and creds.refresh_token:
           creds.refresh(Request())
       else:
           flow = InstalledAppFlow.from_client_secrets_file(
               CREDENTIALS_FILE, SCOPES)
           creds = flow.run_local_server(port=0)

       # Uložení přihlašovacích údajů pro příští přístup
       with open('token.pickle', 'wb') as token:
           pickle.dump(creds, token)

   service = build('calendar', 'v3', credentials=creds)
   return service

# Metoda pro přidání události do kalendáře, vstupními parametry je název, čas s datem a lokace 
def add_event(event_name, time, location=None):

   service = get_calendar_service()

   end = (time + timedelta(hours=1)).isoformat()

   event_result = service.events().insert(calendarId='primary',
       body={
           "summary": event_name,
           "description": 'This is a tutorial example of automating google calendar with python',
           "start": {"dateTime": time.isoformat(), "timeZone": 'Europe/Prague'},
           "end": {"dateTime": end, "timeZone": 'Europe/Prague'},
           "location": location if location else "",
       }
   ).execute()
