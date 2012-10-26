import urllib2
import os

from django.shortcuts import redirect
from django.http import HttpResponse
from django.conf import settings

from PIL import Image

from storages.backends.s3boto import S3BotoStorage
from boto.s3.key import Key


def thumb(request):

    # get the width height and source
    width = int(request.GET.get('width', 0))
    height = int(request.GET.get('height', 0))
    src = request.GET.get('src')

    # only continue if they passed a source
    
    if src:

        # the parts of our url
        parts = src.split('/')

        # some logical size limits
        if width > settings.MAX_IMAGE_SIZE:
            width = settings.MAX_IMAGE_SIZE

        if height > settings.MAX_IMAGE_SIZE:
            height = settings.MAX_IMAGE_SIZE

        # get the stuff we need out of our parts
        bucket = parts[3]
        filename = parts[-1]
        ext = filename.split('.')[-1]

        # create a thumbname for the image
        thumb_name = '%s_thumber_%s_%s.%s' % (''.join( filename.split('.')[0:-1] ), width, height, ext)    
        thumb_src =  '%s/_thumber/%s' % ('/'.join(parts[0:-1]), thumb_name)
        
        # put the thumbs in a dir called _thumber
        thumb_path = '/%s/_thumber/%s' %  ('/'.join(parts[4:-1]), thumb_name)

        # check to see if our thumb exists with a head request
        try:
            response = urllib2.urlopen(HeadRequest(thumb_src))
        except urllib2.HTTPError:
            response = None
            pass

        # PROCESS THE IMAGE HERE
        # handle the image being missing
        # this is where we actually do the image thumbing and upload it to amazon
        if not response:

            # setup a place to store the local file and download it
            local_thumb_path = 'tmp/' + filename
            image = urllib2.urlopen(src)

            # write out the file
            with open(local_thumb_path, 'wb') as f:
                f.write(image.read())

            # do the resizing, save our image
            image = Image.open(local_thumb_path)
            image = image.resize(( width, height ), Image.ANTIALIAS)
            image.save(local_thumb_path)

            # send it back to where it came from
            upload_image(local_thumb_path, thumb_path, bucket)

        return redirect(thumb_src)


def upload_image(local_file_path, external_file_path, bucket):
    """
    Uploads an image to amazon S3

    Arguments
        local_file_path: the place on the local file system the file exists
        external_file_path: the file path from the root of the bucket where the file is going
        bucket: the amazon s3 bucket its going into
    """
    # create the connection
    storage = S3BotoStorage()
    conn = storage.connection
    bucket = conn.get_bucket(bucket)
    
    # new key for bucket
    k = Key(bucket)
    k.key = external_file_path
    k.set_contents_from_filename(local_file_path)
    k.set_acl('public-read')
    
    # remove the tmp file
    os.remove(local_file_path)


class HeadRequest(urllib2.Request):
    """
    A class for doing head requests only
    """
    def get_method(self):
        return "HEAD"