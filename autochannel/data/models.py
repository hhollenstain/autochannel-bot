from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Channel(db.Model):
    __tablename__ = 'channel'
    id = db.Column(db.BigInteger, primary_key=True)
    cat_id = db.Column(db.BigInteger, db.ForeignKey('category.id'), nullable=False)
    chan_type = db.Column(db.String(10), unique=False, nullable=False, default='voice')
    num_suffix = db.Column(db.Integer, unique=False, nullable=False)

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.BigInteger, primary_key=True)
    guild_id = db.Column(db.BigInteger, db.ForeignKey('guild.id'), nullable=False)
    enabled = db.Column(db.Boolean, default=False, nullable=False)
    prefix = db.Column(db.String(10), unique=False, nullable=False, default='AC!')
    empty_count = db.Column(db.Integer, default=1, nullable=False)
    channel_size = db.Column(db.Integer, default=10, nullable=False)
    custom_enabled = db.Column(db.Boolean, default=False, nullable=False)
    custom_prefix = db.Column(db.String(10), unique=False, nullable=False, default='VC!')
    channels = db.relationship(Channel, backref='channels')

    def get_channels(self):
        channels = []

        for channel in self.channels:
            channels.append(channel.id)
        return channels

    def get_chan_suffix(self):
        suffix = []
        for channel in self.channels:
            suffix.append(channel.num_suffix)
        return suffix
    
    
class Guild(db.Model):
    __tablename__ = 'guild'
    id = db.Column(db.BigInteger, primary_key=True)
    categories = db.relationship(Category, backref='categories')
        
    def __repr__(self):
        return f'Guild({self.id})'
    
    def get_categories(self):
        cats = {}

        for category in self.categories:
            cats[category.id] = {}
            cats[category.id]['prefix'] = category.prefix
            cats[category.id]['enabled'] = category.enabled
            cats[category.id]['channel_size'] = category.channel_size
            cats[category.id]['empty_count'] = category.empty_count
            cats[category.id]['custom_enabled'] = category.custom_enabled
            cats[category.id]['custom_prefix'] = category.custom_prefix
        
        return cats