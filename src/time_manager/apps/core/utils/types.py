''' A module containing handy types
'''

class Image():
    ''' Convenience class to hold image data
    '''

    def __init__(self, mime_type, blob):
        self.mime_type = mime_type
        self.blob = blob

    def is_valid(self):
        return self.mime_type.startswith('image/')
