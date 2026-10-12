from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    style = db.Column(db.String, default='All Grain')
    original_volume_gal = db.Column(db.Float, nullable=False, default=5.0)
    target_og = db.Column(db.Float)
    target_fg = db.Column(db.Float)
    target_ibu = db.Column(db.Float)
    target_abv = db.Column(db.Float)
    color_srm = db.Column(db.Float)
    notes = db.Column(db.Text)
    source_url = db.Column(db.String, unique=True)

    malts = db.relationship('Malt', backref='recipe', cascade='all, delete-orphan', lazy='joined')
    hops = db.relationship('Hop', backref='recipe', cascade='all, delete-orphan', lazy='joined')
    yeasts = db.relationship('Yeast', backref='recipe', cascade='all, delete-orphan', lazy='joined')
    others = db.relationship('OtherIngredient', backref='recipe', cascade='all, delete-orphan', lazy='joined')

    def to_dict(self, target_volume_gal=None):
        vol = float(target_volume_gal) if target_volume_gal is not None else self.original_volume_gal
        orig_vol = self.original_volume_gal if (self.original_volume_gal and self.original_volume_gal > 0) else 5.0
        factor = vol / orig_vol

        return {
            'id': self.id,
            'name': self.name,
            'style': self.style or 'All Grain',
            'original_volume_gal': round(orig_vol, 2),
            'target_volume_gal': round(vol, 2),
            'scale_factor': round(factor, 4),
            'target_og': self.target_og,
            'target_fg': self.target_fg,
            'target_ibu': self.target_ibu,
            'target_abv': self.target_abv,
            'color_srm': self.color_srm,
            'notes': self.notes,
            'source_url': self.source_url,
            'malts': [
                {
                    'id': m.id,
                    'name': m.name,
                    'original_amount_lb': round(m.amount_lb, 3),
                    'amount_lb': round(m.amount_lb * factor, 2),
                    'amount_kg': round(m.amount_lb * factor * 0.453592, 2),
                    'potential_gravity': m.potential_gravity,
                    'color_srm': m.color_srm
                }
                for m in self.malts
            ],
            'hops': [
                {
                    'id': h.id,
                    'name': h.name,
                    'original_amount_oz': round(h.amount_oz, 3),
                    'amount_oz': round(h.amount_oz * factor, 2),
                    'amount_g': round(h.amount_oz * factor * 28.3495, 1),
                    'alpha_acid': h.alpha_acid,
                    'addition_time_min': h.addition_time_min,
                    'time_display': h.time_display,
                    'use': h.use
                }
                for h in self.hops
            ],
            'yeasts': [
                {
                    'id': y.id,
                    'strain_name': y.strain_name,
                    'attenuation_pct': y.attenuation_pct,
                    'temp_range_low': y.temp_range_low,
                    'temp_range_high': y.temp_range_high,
                    'amount_units': y.amount_units or '1 pack',
                    'scaled_packs': max(1, round(factor))
                }
                for y in self.yeasts
            ],
            'others': [
                {
                    'id': o.id,
                    'name': o.name,
                    'original_amount': round(o.amount, 3),
                    'amount': round(o.amount * factor, 2),
                    'unit': o.unit,
                    'type': o.item_type,
                    'use': o.use,
                    'time_display': o.time_display
                }
                for o in self.others
            ]
        }

class Malt(db.Model):
    __tablename__ = 'malts'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    amount_lb = db.Column(db.Float, nullable=False)
    potential_gravity = db.Column(db.Float)
    color_srm = db.Column(db.Float)

class Hop(db.Model):
    __tablename__ = 'hops'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    amount_oz = db.Column(db.Float, nullable=False)
    alpha_acid = db.Column(db.Float)
    addition_time_min = db.Column(db.Integer)
    time_display = db.Column(db.String)
    use = db.Column(db.String)

class Yeast(db.Model):
    __tablename__ = 'yeasts'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    strain_name = db.Column(db.String, nullable=False)
    attenuation_pct = db.Column(db.Float)
    temp_range_low = db.Column(db.Float)
    temp_range_high = db.Column(db.Float)
    amount_units = db.Column(db.String)

class OtherIngredient(db.Model):
    __tablename__ = 'other_ingredients'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String, default='unit')
    item_type = db.Column(db.String)
    use = db.Column(db.String)
    time_display = db.Column(db.String)

class Batch(db.Model):
    __tablename__ = 'batches'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    brew_date = db.Column(db.Date)
    measured_og = db.Column(db.Float)
    measured_fg = db.Column(db.Float)
    mash_ph = db.Column(db.Float)
    efficiency_pct = db.Column(db.Float)
    status = db.Column(db.String)

class FermentationLog(db.Model):
    __tablename__ = 'fermentation_logs'
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'))
    timestamp = db.Column(db.DateTime)
    gravity_reading = db.Column(db.Float)
    temperature_c = db.Column(db.Float)
    notes = db.Column(db.Text)
