from mongoengine import *


class Checkpoint(EmbeddedDocument):
    """
    A MongoEngine EmbeddedDocument containing:
        distance: MongoEngine float field, required, (checkpoint distance in kilometers),
		location: MongoEngine string field, optional, (checkpoint location name),
		open_time: MongoEngine datetime field, required, (checkpoint opening time),
		close_time: MongoEngine datetime field, required, (checkpoint closing time).
    """
    distance = FloatField(min_value=0.0, required=True)
    location = StringField()
    open_time = DateTimeField(required=True)
    close_time = DateTimeField(required=True)


class Brevet(Document):
    """
    A MongoEngine document containing:
		length: MongoEngine float field, required
		start_time: MongoEngine datetime field, required
		checkpoints: MongoEngine list field of Checkpoints, required
    """
    length = FloatField(required=True)
    start_time = DateTimeField(required=True)
    checkpoints = ListField(EmbeddedDocumentField(Checkpoint), required=True)

    @classmethod
    def createBrevet(cls, request):
        start_time = request.args.get('start_time', '2021-01-01T00:00', type=str)
        length = request.args.get('length', 200, type=float)
        distances = [val for key, val in request.args.items(multi=True) if key == 'distances']
        locations = [val for key, val in request.args.items(multi=True) if key == 'locations']
        open_times = [val for key, val in request.args.items(multi=True) if key == 'open_times']
        close_times = [val for key, val in request.args.items(multi=True) if key == 'close_times']

        # Sanity checking.
        if not distances:
            raise ValueError('Request had unspecified distances')

        # Create brevet.
        return Brevet(
            length=length,
            start_time=start_time,
            checkpoints=[
                Checkpoint(
                    distance=distance,
                    location=location,
                    open_time=open_time,
                    close_time=close_time,
                )
                for distance, location, open_time, close_time in zip(distances, locations, open_times, close_times)
            ]
        )
