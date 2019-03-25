from google.auth.transport import requests
from google.oauth2 import id_token


class GoogleAuthHandler:
    """Class to handle Google user info"""

    @staticmethod
    def validate(auth_token):
        """
        Gets and validates Google the user info from the auth token
        """
        try:
            idinfo = id_token.verify_oauth2_token(
                auth_token, requests.Request())
            if idinfo['iss'] not in ['accounts.google.com',
                                     'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            return idinfo
        except ValueError:
            return "The token is either invalid or has expired"