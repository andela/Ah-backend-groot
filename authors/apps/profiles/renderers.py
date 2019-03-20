from ..renderers import MainRenderer


class ProfileJSONRenderer(MainRenderer):
    object_label = 'profile'


class ReadingStatsJSONRenderer(MainRenderer):
    object_label = 'readstat'
