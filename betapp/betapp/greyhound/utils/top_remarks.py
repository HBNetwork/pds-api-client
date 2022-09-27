import json
import collections
from .models import *
from collections import Counter

remarks = []
for history in History.objects.all():
    remarks.extend(remark.strip() for remark in history.remarks.split(','))
remarks = Counter(remarks)
remarks = collections.OrderedDict(sorted(remarks.items(), key=lambda x: x[1], reverse=True))
with open('remarks.json', 'w') as file:
    file.write(json.dumps(remarks))