from haystack.sites import site
from haystack import indexes
from tribes.models import Topic, Tribe
import datetime



class TopicIndex(indexes.SearchIndex):
    
    text = indexes.CharField(document=True, use_template=True, model_attr='body')
    author = indexes.CharField(model_attr='creator')
    created = indexes.DateTimeField()
    title = indexes.CharField(model_attr='title', indexed=True)

    def get_query_set(self):
        "Used when the entire index for model is updated."

        return Topic.objects.filter(tribe__private=False)
           
    def should_update(self, instance):
        return (datetime.datetime.now() - instance.editet).seconds < 10 

site.register(Topic, TopicIndex)

site.register(Tribe)
