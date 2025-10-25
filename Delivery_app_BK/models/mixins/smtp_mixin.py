import asyncio
from aiosmtplib import SMTP
from aiosmtplib.errors import *
from email.message import EmailMessage

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Delivery_app_BK.models.tables.notifications_models import EmailSMTP, MessageTemplate

class SMTPMixin:
    async def get_smtp_connection(self:"EmailSMTP"):

        try:
            smtp = SMTP(
                hostname = self.smtp_server,
                port = self.smtp_port,
                use_tls = self.use_ssl
            )
            await smtp.connect()

            # Upgrade to TLS if use_tls is True (STARTTLS)
            if self.use_tls and not self.use_ssl:
                await smtp.starttls()
                
            await smtp.login(self.smtp_username, self.smtp_password_encrypted)

            return smtp
        except Exception as e:
            raise ConnectionError(f"SMTP verification failed: {str(e)}")


    def build_message(self:"EmailSMTP", client:dict, message_template:"MessageTemplate"):
        from Delivery_app_BK.models.tables.notifications_models import SafeDict

        client_email = client.get('email')   
        if client_email is None:
            raise ValueError('Missing eamil.')
        
        message = EmailMessage()
        message["From"] = self.smtp_username                
        message["To"] = client_email        
        message["Subject"] = message_template.name     

        template:str = message_template.content     
        message.set_content(template.format_map(SafeDict(client)))
        return message
    

    async def batch_sender(
            self:"EmailSMTP", 
            target_clients, 
            message_template,
            successful_sent_messages:list,
            fail_sent_messages:list
    ):
        
        smtp = await self.get_smtp_connection()

        for client in target_clients:
            
            try: 
                message = self.build_message(client,message_template)

                client:dict
                client_response = {
                    "id": client.get('id'),
                    'server_message': 'none'
                }

                response:str
                response, _ = await smtp.send_message(message)

                if not response.startswith("250"):
                    client_response['server_message'] = response
                    fail_sent_messages.append(client_response)
                else:
                    client_response['server_message'] = response
                    successful_sent_messages.append(client_response)

            except SMTPRecipientsRefused as e:
                client_response["error_type"] = str(e) 
                client_response["server_message"] = "invalid_recipient"
                fail_sent_messages.append(client_response)

            except SMTPAuthenticationError as e:
                client_response["error_type"] = str(e) 
                client_response["server_message"] = "auth_error"
                fail_sent_messages.append(client_response)

            except SMTPConnectError as e:
                client_response["error_type"] = str(e) 
                client_response["server_message"] = "connection_error"
                fail_sent_messages.append(client_response)

            except (Exception, ValueError) as e:
                client_response["error_type"] = "unknown_error"
                client_response["server_message"] = str(e) 
                fail_sent_messages.append(client_response)


        await smtp.quit()
    
    