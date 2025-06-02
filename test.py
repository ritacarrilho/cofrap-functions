import pyotp
import base64

secret = base64.b64decode("Vlo2WEk0U1FaTVFPNEVJTE5TUDRSWE5FV0xTM0pNNlE=").decode()
print(secret)  
totp = pyotp.TOTP(secret)
print(totp.now())