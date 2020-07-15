import json

class Song:
    def __init__(self, track_id):
        self.track_id = track_id

        path = 'lastfm_subset/'
        for x in track_id[2:5]:
            path += x+'/'

        path += track_id+'.json'
        try:
            with open(path, 'r') as json_file:
                data = json.load(json_file)
                self.artist = data['artist']
                self.title = data['title']
                self.timestamp = data['timestamp']
                self.tags = data['tags']
                self.similars = data['similars']

        except:
            self.artist = "file"
            self.title = "not found"
            self.timestamp = "-1"
            self.tags = []
            self.similars = []

    def get_tags(self, limit=0):
        res = []
        for couple in self.tags:
            if int(couple[1]) >= limit:
                res.append(couple[0])
        return res

    def get_similars(self, limit=0.0):
        res = []
        for couple in self.similars:
            if float(couple[1]) >= limit:
                res.append(couple[0])
        return res

    def shared_tags(self, other):
        set1 = set([x[0] for x in self.tags])
        set2 = set([x[0] for x in other.tags])
        res = tuple(set1.intersection(set2))
        return res

    def combined_tags(self, other):
        set1 = set([x[0] for x in self.tags])
        set2 = set([x[0] for x in other.tags])
        res = tuple(set1.union(set2))
        return res
