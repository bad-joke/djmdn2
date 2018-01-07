# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-07 00:19
from __future__ import unicode_literals

from django.db import migrations

def add_permissions(apps, schema_editor):
    pass


def remove_permissions(apps, schema_editor):
    """Reverse the above additions of permissions."""
    ContentType = apps.get_model('contenttypes.ContentType')
    Permission = apps.get_model('auth.Permission')
    content_type = ContentType.objects.get(
        model='author',
        app_label='catalog',
    )
    # This cascades to Group
    Permission.objects.filter(
        content_type=content_type,
        codename__in=('can_create', 'can_update', 'can_delete'),
    ).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_auto_20180106_1906'),
    ]

    operations = [
        migrations.RunPython(remove_permissions, add_permissions),
    ]
