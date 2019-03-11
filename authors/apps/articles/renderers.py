
import json

from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList


class CategoryJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        render response data
        :param data:
        :param accepted_media_type:
        :param renderer_context:
        :return:
        """
        if type(data) != ReturnList:
            errors = data.get('errors', None)
            if errors is not None:
                return super(CategoryJSONRenderer, self).render(data)

        if type(data) == ReturnDict:
            return json.dumps({
                'category': data
            })

        else:
            return json.dumps({
                'categories': data
            })


class ArticleJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        if(type(data) != ReturnList):
            errors = data.get('errors', None)
            if errors is not None:
                return super(ArticleJSONRenderer, self).render(data)

        if type(data) == ReturnDict:
            return json.dumps({
                'article': data
            })

        return json.dumps({
            'articles': data
        })
