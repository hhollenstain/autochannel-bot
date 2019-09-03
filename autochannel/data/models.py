from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.Integer, db.ForeignKey('guild.id'), nullable=False)
    enabled = db.Column(db.Boolean, default=False, nullable=False)
    prefix = db.Column(db.String(10), unique=False, nullable=False, default='AC!')
    
    
class Guild(db.Model):
    __tablename__ = 'guild'
    id = db.Column(db.Integer, primary_key=True)
    categories = db.relationship(Category, backref='categories')
        
    def __repr__(self):
        return f'Guild({self.id})'
    
    def get_categories(self):
        cats = {}

        for category in self.categories:
            cats[category.id] = {}
            cats[category.id]['prefix'] = category.prefix
            cats[category.id]['enabled'] = category.enabled
        
        return cats