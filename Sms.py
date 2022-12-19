from twilio.rest import Client


class Sms:

    def send(self, from_phone, to_phone, msg) -> bool:
        # send txt message
        account_sid = "AC90376bda6dc96c54255c8b5658e312d9"
        auth_token  = "dcd1e93a3081c8cc6c0e00762df92f97"

        sms_client = Client(account_sid, auth_token)

        message = sms_client.messages.create(body=msg,
                                             from_=from_phone,
                                             to=to_phone)

        #print(message.sid)
        return True
