from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status


class UpdateView(RetrieveUpdateDestroyAPIView):

    def update(self, request, *args, **kwargs):
        self.serializer_instance = self.get_object()
        # if 'article' in kwargs:
        serializer_data = request.data.get('article', {})
        # return serializer_data
        serializer = self.serializer_class(
            self.serializer_instance, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
