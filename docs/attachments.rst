=============
 Attachments
=============

Attachments are an optional feature of django-vox. In order to
to use attachments, two things must be in order. First, you need
to set them up on your models, and second you need to be using a
backend that supports them (which is just email right now).

Setting up the Models
=====================

Adding attachments is a lot like adding notifications. Instead of the
``notification`` attribute on ``VoxMeta``, you specify the ``attachments``
field


To add notifications to a model, change the parent class from
``django.db.models.Model`` to ``django_vox.models.VoxModel``.
Also, add ``VoxMeta`` inner class (much like django's ``Meta``)
which contains one attribute, a tuple named ``notifications``. Each
item in the tuple should be a ``django_vox.models.VoxParam``
instance. The result might look something like::


  class User(VoxModel):

      class VoxMeta:
          attachments = VoxAttachments(
              vcard=VoxAttach(attr='make_vcard', mime_string='text/vcard',
                  label=_('Contact Info')),
              photo=VoxAttach(mime_attr='photo_mimetype'))

          notifications = (
          ...
          )


In this case, there are two attachment options. The first, get's the file
contents from ``User.make_vcard``, and has a mime type of ``text/vcard``.
The second will get its contents from ``User.photo``, and will get its mime
type from whatever's in ``User.photo_mimetype``.

Once these have been added, attachment options should show up when editing
templates in the admin.


