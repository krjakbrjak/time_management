from PIL import Image
import tempfile

def create_image(suffix='.jpg'):
    ''' Creates a dummy image
    '''

    image = Image.new('RGB', (100, 100))
    tmp_file = tempfile.NamedTemporaryFile(suffix=suffix)
    image.save(tmp_file)
    tmp_file.seek(0)

    return tmp_file
