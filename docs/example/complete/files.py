from flask.ext.uploads import UploadSet, IMAGES

UPLOAD_SETS = {
    'resumes': UploadSet(name='resumes', extensions=('pdf')),
    'images': UploadSet(name='images', extensions=IMAGES)
    }


def upload_sets():
    return tuple(UPLOAD_SETS.values())
