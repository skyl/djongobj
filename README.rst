
Djongobj
========

An abstraction atop PyMongo for working with Django pythonically (or so we hope).


Requirements
------------

I'm developing with mongodb 1.4.3 and pymongo 1.6.
Lesser versions will not work.
Django is not necesarily required but is assumed here (1.2+)


Installation
------------

Put djongobj on your path in your favored way.

Usage
-----

A simple way to use the module is to add an instance of Mongo to your normal Django class::

    from djongobj.models import Mongo

    class Blog(models.Model):
        
        mongo = Mongo()

Using this descriptor, you can add in some arguments if you must::

    Mongo(database='mydatabase', collection='mycollection', host='12.XX...', port=27017,
            document_class=MyDocument, collection_class=MyCollection)

MyDocument and MyCollection can be subclasses of ``djongobj.models.Document`` and
``djongobj.models.Collection`` respectively.

For the sake of these samples, we will assume that ``Mongo`` was instantiated without arguments.


Class attr - Collection
```````````````````````

Now, with your ``class``, the mongo attr will be a lightly-wrapped pymongo ``collection``::

    >>> Blog.mongo
    <class 'djongobj.models.Collection'>, {'host': 'localhost', 'db': 'content', 'port': 27017, 'collection': 'blog'}
    >>> Blog.mongo.all()
    <pymongo.cursor.Cursor object at 0x9b5040c>

Do some basic queries::

    >>> Blog.mongo.filter(_id=1)
    <pymongo.cursor.Cursor object at 0x9b5338c>
    >>> # get the query back as a queryset from the Django ORM: 
    >>> Blog.mongo.filter(_id=1, return_type='queryset')
    [<Blog: this is the title>]
    >>> len(Blog.mongo) # number of documents in the collection
    3

Update some documents::

    >>> Blog.mongo.update_one(1, {'foo': [12, 32]})
    >>> Blog.mongo.upsert_one({'_id': 1, 'foo': [12, 32]}) # same as above in this case
    >>> Blog.mongo.update({'foo': [12, 32]}, # the query params
    ...     {'$set': {'bar': 'baz'}}         # the update instructions
    ... )

Create some indices::
    
    >>> from pymongo import ASCENDING, DESCENDING, GEO2D
    >>> Blog.mongo.create_index(
    ... [ ('somekey', ASCENDING), ('other', DESCENDING), ('mypoint', GEO2D) ])

Advanced queries and map reduce are facilitated::

    pass

You can get at the pymongo objects underneath::

    >>> Blog.mongo._collection
    Collection(Database(Connection('localhost', 27017), u'content'), u'blog')
    >>> Blog.mongo._db
    Database(Connection('localhost', 27017), u'content')


Instance attr - Document
`````````````````````````

The document that is currently implemented here
acts just like a dictionary that eagerly interacts with the database.
On the surface, it looks like you are just interacting with
regular dictionary but each operation incurs database traffic.
This may or may not be desirable depending on the case.
Input is welcome!

The pk field for SQL database and our collection are the same::

    >>> b = Blog.objects.get(id=1) # get an object.
    >>> b.mongo
    {u'_id': 1, u'bar': u'baz'}
    >>> b.mongo['foo'] = 'the next bar'
    >>> del(b.mongo['bar'])


