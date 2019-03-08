import json
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList


class ProfileJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        if(type(data) != ReturnList):
            errors = data.get('errors', None)
            if errors is not None:
                return super(ProfileJSONRenderer, self).render(data)

        if type(data) == ReturnDict:
            return json.dumps({
                'profile': data
            })

        return json.dumps({
            'profiles': data
        })
