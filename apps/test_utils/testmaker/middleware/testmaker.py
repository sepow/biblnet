from django.conf import settings
from django.test import Client
from django.test.utils import setup_test_environment

from test_utils.testmaker.base_processor import Processer
from test_utils.testmaker.base_serializer import Serializer

#Remove at your own peril.
#Thar be sharks in these waters.
debug = getattr(settings, 'DEBUG', False)
if not debug:
    print "THIS CODE IS NOT MEANT FOR USE IN PRODUCTION"
else:
    print "Loaded Testmaker Middleware"

class TestMakerMiddleware(object):
    def __init__(self):
        """
        Assign a Serializer and Processer
        Serializers will be pluggable and allow for custom recording.
        Processers will process the serializations into test formats.
        """
        self.serializer = Serializer()
        self.processer = Processer()

    def process_request(self, request):
        """
        Run the request through the testmaker middleware.
        This outputs the requests to the chosen Serializers.
        Possible running it through one or many Processors
        """
        #This is request.REQUEST to catch POST and GET
        if 'test_client_true' not in request.REQUEST:
            self.serializer.save_request(request)
            self.processer.process_request(request)
            if request.method.lower() == "get":
                setup_test_environment()
                c = Client(REMOTE_ADDR='127.0.0.1')
                getdict = request.GET.copy()
                getdict['test_client_true'] = 'yes' #avoid recursion
                response = c.get(request.path, getdict)
                self.serializer.save_response(request.path, response)
                self.processer.process_response(request, response)
