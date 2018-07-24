import collections
import copy
import json

from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class JSONEditorWidget(forms.Widget):
    template_name = 'django_admin_json_editor/editor.html'

    def __init__(self, schema, collapsed=True, sceditor=False, attrs=None):
        default_attrs = {'theme': 'bootstrap3', 'iconlib': 'fontawesome4'}
        if attrs:
            default_attrs.update(attrs)

        super(JSONEditorWidget, self).__init__(default_attrs)

        self._schema = schema
        self._collapsed = collapsed
        self._sceditor = sceditor

    def render(self, name, value, attrs=None, renderer=None):
        if callable(self._schema):
            schema = self._schema(self)
        else:
            schema = copy.copy(self._schema)

        self.schema_updater(schema)

        schema['title'] = ' '
        schema['options'] = {'collapsed': int(self._collapsed)}

        context = {
            'name': name,
            'editor_options': json.dumps(dict(schema=schema, **self.attrs)),
            'data': value,
            'sceditor': int(self._sceditor),
        }
        return mark_safe(render_to_string(self.template_name, context))

    @classmethod
    def schema_updater(cls, nested):
        """Updates schema to format allowed by JS"""
        for key, value in nested.items():
            if isinstance(value, collections.Mapping):
                cls.schema_updater(value)
            else:
                # Replace bool values with integers
                nested[key] = int(value) if isinstance(value, bool) else value

    @property
    def media(self):
        css = {
            'all': [
                'django_admin_json_editor/fontawesome/css/font-awesome.min.css',
                'django_admin_json_editor/style.css',
            ]
        }
        js = [
            'django_admin_json_editor/jquery/jquery.min.js',
            'django_admin_json_editor/bootstrap/js/bootstrap.min.js',
            'django_admin_json_editor/jsoneditor/jsoneditor.min.js',
        ]
        if self.attrs.get('theme', '').startswith('bootstrap'):
            css['all'].append('django_admin_json_editor/bootstrap/css/bootstrap.min.css')
        if self._sceditor:
            css['all'].append('django_admin_json_editor/sceditor/themes/default.min.css')
            js.append('django_admin_json_editor/sceditor/jquery.sceditor.bbcode.min.js')
        return forms.Media(css=css, js=js)
