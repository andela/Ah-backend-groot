import json

from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList


class MainRenderer(JSONRenderer):
    """
    Override default renderer to customise output
    """
    charset = 'utf-8'
    object_label = 'object'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if(type(data) != ReturnList):
            errors = data.get('errors', None)
            if errors is not None:
                return super(MainRenderer, self).render(data)
        if type(data) == ReturnDict:
            return json.dumps(
                {self.object_label: data}
            )
        else:
            if(self.object_label == 'history'):
                return json.dumps({
                    self.object_label: data
                })
            return json.dumps({
                self.object_label + 's': data
            })
