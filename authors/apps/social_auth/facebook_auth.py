import facebook


class FacebookAuthHandler:
    """
    Class to get Facebook user information and return it
    """

    @staticmethod
    def validate(auth_token):
        try:
            graph = facebook.GraphAPI(access_token=auth_token)
            profile = graph.request('/me?fields=id,name,email')
            return profile
        except Exception:
            message = "The token is invalid or expired."
            return message