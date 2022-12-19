from twilio.rest import Client


class Sms:

    def send(self, from_phone, to_phone, msg) -> bool:
        # send txt message
        account_sid = "put account sid here"
        auth_token  = "put auth token here"

        sms_client = Client(account_sid, auth_token)

        message = sms_client.messages.create(body=msg,
                                             from_=from_phone,
                                             to=to_phone)

        #print(message.sid)
        return True
