from flask_wtf import FlaskForm
from wtforms.fields import BooleanField, IntegerField, FormField
from wtforms.validators import Email
from wtforms_alchemy import model_form_factory, ModelFormField, ModelFieldList
from autochannel.data import db
from autochannel.data.models import Guild, Category

BaseModelForm = model_form_factory(FlaskForm)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session

class CategoryForm(ModelForm):
    class meta:
        model = Category
        #include_primary_keys = True
        # include = ['id', 'name', 'enabled', 'prefix']

class GuildForm(ModelForm):
    class Meta:
        model = Guild
        include = ['id']
        include_primary_keys = True
    categories = []
    #categories = ModelFieldList(CategoryForm)
    #categories = ModelFieldList(CategoryForm)
    #categories = ModelFieldList(FormField(CategoryForm))
    #hanks = ModelFieldList(FormField(CategoryForm))




