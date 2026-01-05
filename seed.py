
from app import app  
from db import db 
from models.brand import Brand 
tunisian_brands = ["Délice", "Vitalait", "Sicam", "Poulina", "Saida"] 
with app.app_context(): 
    for name in tunisian_brands: 
        if not Brand.query.filter_by(name=name).first(): 
            db.session.add(Brand(name=name, boycott_status=False)) 
            db.session.commit() 
        print("Seed complete.")