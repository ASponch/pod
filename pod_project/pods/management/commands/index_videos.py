from django.core.management.base import BaseCommand, CommandError
from django.utils import translation
from pods.models import Pod
from elasticsearch import Elasticsearch
from django.conf import settings
import json

ES_URL = getattr(settings, 'ES_URL', ['http://127.0.0.1:9200/'])

class Command(BaseCommand):
	args = '__ALL__ or <pod_id pod_id ...>'
	help = 'Index in elasticsearch the specified video'
	
	def handle(self, *args, **options):	
		# Activate a fixed locale fr
		translation.activate('fr')

		es = Elasticsearch(ES_URL)
		if args:
			if args[0]=='__ALL__':
				delete = es.delete_by_query(index="pod", doc_type='pod', body={"query":{"match_all":{}}})
				from pods.views import VIDEOS
				for pod in VIDEOS:
					res = es.index(index="pod", doc_type='pod', id=pod.id, body=pod.get_json_to_index(), refresh=True)
			else:
				for pod_id in args:
					try:
						pod = Pod.objects.get(pk=int(pod_id))
					except Pod.DoesNotExist:
						raise CommandError('Pod "%s" does not exist' % pod_id)
					res = es.index(index="pod", doc_type='pod', id=pod.id, body=pod.get_json_to_index(), refresh=True)
		else:
			print "******* Warning : you must give some arguments : %s *******" %self.args


"""
es = Elasticsearch()
time = datetime.utcnow().replace(tzinfo=pytz.utc)
msg = {'_id': 1, 'text': 'Hello World'}
es.index(index='idx', doc_type='dtype', id=msg['_id'], body=msg, timestamp=time, ttl='30d')
msg2 = '''{"doc": {"text": "New Message"}}'''
es.update(index='idx', doc_type='dtype', id=msg['_id'], body=msg2, timestamp=time, ttl='30d')
"""