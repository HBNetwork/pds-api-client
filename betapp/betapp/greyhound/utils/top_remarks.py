import json
import collections
from .models import *
from collections import Counter

remarks = list()
for history in History.objects.all():
    for remark in history.remarks.split(','):
        remarks.append(remark.strip())

remarks = Counter(remarks)
remarks = collections.OrderedDict(sorted(remarks.items(), key=lambda x: x[1], reverse=True))
file = open('remarks.json', 'w')
file.write(json.dumps(remarks))
file.close()