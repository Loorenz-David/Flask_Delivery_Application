from sqlalchemy.exc import IntegrityError, DataError, OperationalError, ProgrammingError, SQLAlchemyError
import asyncio
from aiosmtplib import SMTP
from typing import TYPE_CHECKING

from Delivery_app_BK.models import db, EmailSMTP, TwilioMod, MessageTemplate
from Delivery_app_BK.models.managers.object_searcher import GetObject

if TYPE_CHECKING:
    from Delivery_app_BK.routers.utils.response import Response


action_type_map ={
    'create':['created','creating'],
    'update':['updated','updating'],
    'delete':['deleted','deleting']
}


"""
{
    "sms":{
        "template_id": id
        "target_clients": [ { id: id, target_address: sms, info_for_filling_template... } ]
    }

    "email":{
        "template_id": id
    }
}

"""

class ObjectNotificator:

    def __init__(
            self,
            response:"Response",
            identity=None
    ):
        
        self.response = response
        self.identity:dict = identity or getattr(response, "identity", None)
        
        incoming_data:dict = response.incoming_data or {}
        self.sms_messages:dict = incoming_data.get('sms',None)
        self.email_messages:dict = incoming_data.get('email',None)

        self.fail_email_messages = []
        self.successful_email_messages = []

        self.fail_sms_messages = []
        self.successful_sms_messages = []

        self.message_report = {}

        

    def send_message_sync(self):
        asyncio.run( self.send_messages() )
        
    async def send_messages(self):
        try:

            tasks = []

            if self.email_messages:
                tasks.append(self.send_email_messages())
            
            if self.sms_messages:
                tasks.append(self.send_sms_messages())
            
            if tasks:
                await asyncio.gather(*tasks)
            
            if not self.email_messages and not self.sms_messages:
                raise ValueError("no sms or email key in request",
                                 "to send messages, one must provide a dictionary with keys pointing to the type channel",
                                 "Example:",
                                 """{
                                        "sms":{
                                            "template_id": id
                                            "target_clients": [ { id: id, target_address: sms, info_for_filling_template... } ]
                                        }

                                        "email":{
                                            "template_id": id
                                        }
                                    }"""
                                 )


        
        except ValueError as e:
            self.response.set_message(
                message= "Value Error when sending messages."
            )
            self.response.set_error(
                message = str(e),
                status = 400
            )
        except ConnectionError as e:
            self.response.set_message(
                message= "Connection Error when sending messages."
            )
            self.response.set_error(
                message = str(e),
                status = 400
            )

        except Exception as e:
            self.response.set_message(
                message= "Error when sending messages."
            )
            self.response.set_error(
                message = str(e),
                status = 400
            )
        
        self.build_message_report()

        self.response.set_payload(self.message_report)
        self.response.compress_payload()

    async def send_email_messages(self):

        required_auth: "EmailSMTP"
        message_template: MessageTemplate
        target_clients: list

        required_auth, message_template, target_clients = self.set_up_auth(
            AuthModel = EmailSMTP,
            template_id = self.email_messages.get( 'template_id', None ),
            target_clients = self.email_messages.get( 'target_clients', None ),
            action = 'emails'
        )

        if message_template.channel != 'email':
            raise ValueError("Template channel mismatch: expected 'email'")

        
        for i in range( 0, len(target_clients), required_auth.max_per_session ):
            batch = target_clients[ i: i + required_auth.max_per_session ]
            await required_auth.batch_sender(
                batch,
                message_template,
                self.successful_email_messages,
                self.fail_email_messages
                )
            

    async def send_sms_messages(self):
        required_auth: "TwilioMod"
        message_template: MessageTemplate
        target_clients: list

        required_auth, message_template, target_clients = self.set_up_auth(
            AuthModel = TwilioMod,
            template_id = self.sms_messages.get( 'template_id', None ),
            target_clients = self.sms_messages.get( 'target_clients', None ),
            action = 'sms'
        )

        if message_template.channel != 'sms':
            raise ValueError("Template channel mismatch: expected 'sms'")

        await required_auth.batch_sender(
            target_clients,
            message_template,
            self.successful_sms_messages,
            self.fail_sms_messages
        )
        
    
    def set_up_auth( self, AuthModel: EmailSMTP | TwilioMod, template_id, target_clients, action="" ):
        team_id = self.identity.get( 'team_id', None )

        # validates there is list of targets and template id is of type 'int'
        if not isinstance(target_clients,list):
            raise ValueError(f"Missing to pass a list of dictionaries 'target clients'.",
                                "Each  client dictionary must have:",
                                " * the client id as found in db, ",
                                " * the client contanct. ",
                                " * the keys for filling the target template. ",
                                )
     
        if not isinstance(template_id,int):
            raise ValueError(f"Missing to pass the template id as found in the db. this will be use to fill the messages")

        if not isinstance( team_id, int ):
            raise ValueError('Invalid team_id type, or missing team_id.')

        required_auth = AuthModel.query.filter_by( team_id = team_id).first()
        if not required_auth:
            raise Exception (f" Not authentification set for sending {action}")
        message_template: MessageTemplate = GetObject.get_object( MessageTemplate, template_id, self.identity )
        
        return required_auth, message_template, target_clients
        
       
   
    


    def build_message_report(self):

        if self.sms_messages:
            self.message_report['sms'] = {
                'sent_sms': self.successful_sms_messages,
                'fail_sms': self.fail_sms_messages
            }

        if self.email_messages:
            self.message_report['email'] = {
                'sent_emails': self.successful_email_messages,
                'fail_emails': self.fail_email_messages
            }



    

