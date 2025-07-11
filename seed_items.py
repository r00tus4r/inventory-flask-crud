from app import app, db, Item

with app.app_context():
    items = [
        Item(name="Laptop", description="Lenovo ThinkPad X1", quantity=5, price=1200.00),
        Item(name="Mouse", description="Logitech MX Master 3", quantity=15, price=85.99),
        Item(name="Keyboard", description="Mechanical Keyboard", quantity=10, price=150.50),
        Item(name="Monitor", description="Dell 24-inch FHD", quantity=7, price=200.00),
        Item(name="Smartphone", description="Samsung Galaxy S21", quantity=12, price=999.99),
        Item(name="Webcam", description="1080p HD Webcam", quantity=20, price=59.90),
        Item(name="USB-C Cable", description="1m charging cable", quantity=30, price=9.99),
        Item(name="External HDD", description="2TB USB 3.0 drive", quantity=8, price=75.25),
        Item(name="Headphones", description="Sony WH-1000XM4", quantity=6, price=299.00),
        Item(name="Office Chair", description="Ergonomic mesh chair", quantity=4, price=180.00)
    ]

    db.session.bulk_save_objects(items)
    db.session.commit()
    print("✅ Items added successfully!")
