from pymongo import Connection, ASCENDING, DESCENDING
from pymongo.son import SON

# PyMongo
# http://api.mongodb.org/python/1.6%2B/index.html


class Document(object):

    def __init__(self, instance, owner, db, collection, _id, host='localhost', port=27017):
        self._meta = {'db': db, 'collection': collection, 'host': host, 'port': port}
        self.pk = _id
        self._collection = get_collection(db, collection, host, port)
        self._db = get_db(db, host, port)
        self._instance = instance
        self._owner = owner

    # emulate a dictionary

    def __repr__(self):
        return repr(self.d())

    def __getitem__(self, key):
        return self.d()[key]

    def __setitem__(self, key, value):
        self.update({key: value})

    def  __delitem__(self, key):
        self.pop(key)

    def __contains__(self, key):
        return self.has_key(key)

    def __iter__(self):
        return self.iterkeys()

    def __len__(self):
        return len(self.d())

    def d(self):
        if not self._collection.find_one({'_id': self.pk}):
            self._collection.insert({'_id': self.pk})
        return self._collection.find_one({'_id': self.pk})

    def update(self, attrs):
        '''uses $set to update the attrs of the Document like a dict'''
        return self._collection.update({'_id': self.pk}, {'$set': attrs})

    def keys(self):
        return self.d().keys()

    def values(self):
        return self.d().values()

    def items(self):
        return self.d().items()

    def has_key(self, key):
        return self.d().has_key(key)

    def get(self, key, default=None):
        return self.d().get(key, default)

    def clear(self):
        return self._collection.remove({'_id': self.pk})

    def setdefault(self, key, value):
        if self.d().get(key):
            return self.d().get(key)
        else:
            self.update({key: value})
        return value

    def iterkeys(self):
        return self.d().iterkeys()

    def itervalues(self):
        return self.d().itervalues()

    def iteritems(self):
        return self.d().iteritems()

    def _get_pop_command(self, key):
        return SON({
            'findandmodify': self._meta['collection'],
            'update': {'$unset': {key: 1}}
        })


    def pop(self, key, default=None):
        '''Atomically pop the value from the document and return it'''

        ret = self._db.command(
                self._get_pop_command(key)
        )['value']

        if key in ret:
            return ret[key]

        else:
            return default

    def popitem(self):
        raise NotImplementedError, 'hard to do atomically, avoid popping _id, pick a random key, use case?'

    # special mongo update methods

    def inc(self, key, value):
        return self.mod('inc', key, value)

    def _update(self, d):
        '''http://www.mongodb.org/display/DOCS/Updating

        d can be in the form::

            {
                '$inc': {'field': 1, 'other': 10},
                '$set': {'foofield': value},
                '$unset': ...,
                '$push':
            }
        '''
        return self._collection.update({'_id': self.pk}, d)

    def mod(self, op, key, value):
        '''perform a single modification

        call like::

            instance.mongo.mod('push', 'mylist', 'somevalue')
        '''

        d = {'$%s' % op: {key: value}}
        self._update(d)



class Collection(object):

    def __init__(self, instance, owner, db, collection, host='localhost', port=27017):
        self._meta = {'db': db, 'collection': collection, 'host': host, 'port': port}
        self._collection = get_collection(db, collection, host, port)
        self._instance = instance
        self._owner = owner
        self._db = get_db(db, host, port)

    def __repr__(self):
        return u'%s, %s' % (type(self), repr(self._meta))

    def __len__(self):
        return self._collection.count()

    def all(self, return_type=None):
        return self.filter(return_type)

    def filter(self, return_type=None, **kwargs):
        if not return_type:
            # return the cursor
            return self._collection.find(kwargs)

        # turn the list of dicts into a list of ids eg [2, 5, 6] if return_type is queryset
        if return_type == 'queryset':
            mongo_ids = [x['_id'] for x in self._collection.find(kwargs, {'_id': 1}).sort('_id')]
            return self._owner.objects.filter(pk__in=mongo_ids)

        if return_type == 'documents':
            raise NotImplementedError, 'hrm ..'

    def update(self, spec, doc, **kwargs):
        '''simple wrapper around http://www.mongodb.org/display/DOCS/Updating'''
        return self._collection.update(spec, doc, **kwargs)

    def upsert_one(self, attrs):
        '''insert if no _id, else upsert'''
        return self._collection.save(attrs)

    def update_one(self, _id, attrs):
        '''Updates the document with _id in the collection with attrs'''
        self._collection.update({'_id': _id}, {'$set': attrs})

    def create_index(self, arg, deprecated_unique=None, ttl=300, **kwargs):
        '''arg can be a single string, or a list of 2-tuples:

        [('mykey', pymongo.ASCENDING), ('other', pymongo.DESCENDING), ('mygeofield', pymongo.GEO2D)]
        '''
        self._collection.create_index(arg, deprecated_unique, ttl, **kwargs)

    def score_for_string(self, string, field_score_tuples):
        pass


def get_db(db, host='localhost', port=27017):
    c = Connection(host, port)
    return c[db]


def get_collection(db, collection, host='localhost', port=27017):
    c = Connection(host, port)
    db = c[db]
    col = db[collection]
    return col


def get_document(db, collection, _id, host='localhost', port=27017):
    col = get_collection(db, collection, host='localhost', port=27017)

    if not col.find_one({'_id': _id}):
        col.insert({'_id': _id})

    return col.find_one({'_id': _id})


class Mongo(object):
    def __init__(self, db=None, collection=None, host='localhost', port=27017,
            document_class=Document, collection_class=Collection):
        self._db = db
        self._collection = collection
        self._host = host
        self._port = port
        self._doc = document_class
        self._coll = collection_class

    def __get__(self, instance, owner):
        if instance:
            return self._doc(instance, owner, self._db or instance._meta.app_label,
                            self._collection or instance._meta.module_name,
                            instance.pk, self._host, self._port)

        return self._coll(instance, owner, self._db or owner._meta.app_label,
                            self._collection or owner._meta.module_name,
                            self._host, self._port)


