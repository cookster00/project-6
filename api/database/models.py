from mongoengine import *
import datetime


class Checkpoint(EmbeddedDocument):
    """
    A MongoEngine EmbeddedDocument containing:
        distance: MongoEngine float field, required, (checkpoint distance in kilometers),
		location: MongoEngine string field, optional, (checkpoint location name),
		open_time: MongoEngine datetime field, required, (checkpoint opening time),
		close_time: MongoEngine datetime field, required, (checkpoint closing time).
    """
    km = FloatField(required=True)
    location = StringField()
    open_time = StringField(required=True)
    close_time = StringField(required=True)
    miles = FloatField()


class Brevet(Document):
    """
    A MongoEngine document containing:
		length: MongoEngine float field, required
		start_time: MongoEngine datetime field, required
		checkpoints: MongoEngine list field of Checkpoints, required
    """
    brevet_dist_km = FloatField(required=True)
    start_time = StringField(required=True)
    items = EmbeddedDocumentListField(Checkpoint, required=True)
