import twitter
from authors.settings import (TWITTER_APP_CONSUMER_API_KEY,
                              TWITTER_APP_CONSUMER_API_SECRET_KEY)


class TwitterAuthHandler:
    """
    Class to handle twitter auth tokens
    by splitting the two tokens and validating them
    """
    @staticmethod
    def split_twitter_auth_tokens(tokens):
        """
        Splits the token sent in the request into two:
        access token and access_token_secret
        """
        auth_tokens = tokens.split(' ')
        if len(auth_tokens) < 2:
            return 'invalid token'
        access_token = auth_tokens[0]
        access_token_secret = auth_tokens[1]
        return access_token, access_token_secret

    @staticmethod
    def validate_twitter_auth_tokens(tokens):
        """
        Validates twitter auth and returns user info as a dict
        """
        access_token_key, access_token_secret = TwitterAuthHandler\
            .split_twitter_auth_tokens(tokens)
        try:
            consumer_api_key = TWITTER_APP_CONSUMER_API_KEY
            consumer_api_secret_key = TWITTER_APP_CONSUMER_API_SECRET_KEY

            api = twitter.Api(
                consumer_key=consumer_api_key,
                consumer_secret=consumer_api_secret_key,
                access_token_key=access_token_key,
                access_token_secret=access_token_secret
            )

            user_profile_info = api.VerifyCredentials(include_email=True)
            return user_profile_info.__dict__
        except Exception:
            return None
