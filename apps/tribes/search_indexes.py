from haystack.sites import site
from haystack import indexes
from tribes.models import Topic, Tribe
<<<<<<< HEAD:apps/tribes/search_indexes.py
=======
import datetime

>>>>>>> 120bfe5e62318729193421dc27089abfeb0a60d1:apps/tribes/search_indexes.py

class TopicIndex(indexes.SearchIndex):
    
    text = indexes.CharField(document=True, use_template=True, model_attr='body')
    author = indexes.CharField(model_attr='creator')
    created = indexes.DateTimeField()
    title = indexes.CharField(model_attr='title', indexed=True)

    def get_query_set(self):
        "Used when the entire index for model is updated."
<<<<<<< HEAD:apps/tribes/search_indexes.py
        return Topic.objects.filter(tribe__private=False)
    
    def should_update(self, instance):
        return (datetime.datetime.now() - instance.modified).seconds > 30 
        
    #def should_update(self, instance):
        #skal ikke reindekseres ved views ++ og ligende. 
    
    
=======
        return Topic.objects.all()
    
    def should_update(self, instance):
        return (datetime.datetime.now() - instance.editet).seconds < 10 

>>>>>>> 120bfe5e62318729193421dc27089abfeb0a60d1:apps/tribes/search_indexes.py
site.register(Topic, TopicIndex)

site.register(Tribe)
