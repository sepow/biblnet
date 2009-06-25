from haystack.sites import site
from haystack import indexes
from tribes.models import Topic, Tribe



class TopicIndex(indexes.SearchIndex):
    title = indexes.CharField(model_attr='title')
    text = indexes.CharField(model_attr='body', document=True, use_template=True)
    author = indexes.CharField(model_attr='creator')
    created = indexes.DateTimeField()

    def get_query_set(self):
        "Used when the entire index for model is updated."
        return Topic.objects.filter(tribe__private=False)


site.register(Topic, TopicIndex)

site.register(Tribe)
