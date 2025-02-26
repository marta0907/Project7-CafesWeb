from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
Bootstrap5(app)
SECRET_PASSWORD = os.getenv('SECRET_PASS')


# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    address: Mapped[str] = mapped_column(String(250), nullable=False)
    website: Mapped[str] = mapped_column(String(250), nullable=False)
    has_alcohol: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_lunch: Mapped[bool] = mapped_column(Boolean, nullable=False)
    google_rate: Mapped[str] = mapped_column(String(250), nullable=True)
    price_range: Mapped[str] = mapped_column(String(250), nullable=True)
    
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
        
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    if request.method == 'POST':
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            address=request.form.get("address"),
            website=request.form.get("website"),
            has_alcohol=bool(request.form.get("has_alcohol")),
            has_lunch=bool(request.form.get("has_lunch")),
            google_rate=request.form.get("google_rate"),
            price_range=request.form.get("price_range"),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('cafes'))
    return render_template('add.html')

@app.route('/cafes', methods=['GET'])
def cafes():
    name = request.args.get('name', '')  # Get search term from the URL
    if name:
        # Filter cafes based on location
        filtered_cafes = Cafe.query.filter(Cafe.name.like(f'%{name}%')).order_by(Cafe.name).all()
    else:
        # Show all cafes if no search term is provided
        filtered_cafes = Cafe.query.order_by(Cafe.name).all()
    return render_template('cafes.html', cafes=filtered_cafes)

@app.route('/delete', methods=['GET', 'POST'])
def delete_cafe():
    secret_key = SECRET_PASSWORD
    # Check if the correct secret key is provided in the request
    if request.args.get('secret') != secret_key:
        abort(403)  # Forbidden access if the secret key is incorrect
    if request.method == 'POST':
        cafe_id = request.form.get('cafe_id')
        cafe = Cafe.query.get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            # After deleting, redirect to the /delete route with the secret key
            return redirect(url_for('delete_cafe', secret=secret_key))
    cafes_all = Cafe.query.all()  # Get all cafes to display for deletion
    return render_template('delete.html', cafes=cafes_all)

@app.route('/edit/<int:cafe_id>', methods=['GET', 'POST'])
def edit_cafe(cafe_id):
    secret_key = request.args.get('secret')
    if secret_key != SECRET_PASSWORD:
        abort(403)
    cafe = Cafe.query.get_or_404(cafe_id)
    if request.method == 'POST':
        cafe.name = request.form.get('name')
        cafe.map_url = request.form.get('map_url')
        cafe.address = request.form.get("address")
        cafe.website = request.form.get("website")
        cafe.price_range = request.form.get("price_range")
        cafe.google_rate=request.form.get("google_rate")
        cafe.has_alcohol=bool(request.form.get("has_alcohol"))
        cafe.has_lunch=bool(request.form.get("has_lunch"))
        db.session.commit()
        return redirect(url_for('cafes'))
    return render_template('edit.html', cafe=cafe, secret=secret_key)

if __name__ == '__main__':
    app.run(debug=True)
