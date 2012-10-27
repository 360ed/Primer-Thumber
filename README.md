Primer-Thumber
==============

A generic thumbnailing server built in Django that ties in directly with Amazon S3. 


Why?
====
Sometimes it's not feasible to generate thumbnails ahead of time. Maybe you don't know the sizes, or your clients keep jumping between the profile images being 30 x 30 and 40 x 40. Whatever the case may be, Thumber is an easy way to request images from your Amazon S3 account at any dimensions, get them resized, and uploaded back to the server.


Installation
============

You're going to want to fire this up on a server somewhere, my preference being EC2, Ubuntu, Nginx, and Gunicorn. Once you have your server in place, you're going to want to install the following libs with apt-get, instructions have been taken from http://obroll.com/install-python-pil-python-image-library-on-ubuntu-11-10-oneiric/. These extra libs prevent an issue with interlaced images.

sudo apt-get install libjpeg8 libjpeg62-dev libfreetype6 libfreetype6-dev

sudo ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib<br/>
sudo ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib<br/>
sudo ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib<br/>

After those libs are installed, you can install the Python requirements listed in requirements.txt manually, or use the pip shortcut. sudo pip install -r requirements.txt

Last step is to go into your settings.py file and plug in your AWS S3 information. Make sure you have write permissions on the buckets that you will be trying to access and that they are set to public.

Pending you have the server setup correctly, you're ready to go.


Useage
======
Now, anytime you want to request an image, you'll pass it through your Thumber server. The required params are:

width: An int width for the image
height: An int height for the image
src: The Amazon S3 path to your image. Obviously, the Thumber server must have write priveleges to this particular S3 account.

&lt;img src="http://your-thumber-url-or-ip.com/?width=100&height=100&src=https://s3.amazonaws.com/my-bucket/my-image.png"/&gt;


How it works
============
When an image is requested, Thumber does a quick HEAD request to Amazon to check for the resized files existence. If it does exist, a redirect to the image is returned. In the event that it is not, Thumber will pull down the image, resize it with PIL, upload the newly resized version back to S3, and then redirect to it. Thumbs are stored in a directory called _thumber that is created at the same level as the requested image.

