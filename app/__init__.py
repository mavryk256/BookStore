from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_dropzone import Dropzone
from datetime import timedelta

db = SQLAlchemy()
dropzone = Dropzone()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'magic2004'
    app.permanent_session_lifetime = timedelta(days=1)

    # Cấu hình database và Dropzone
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
    # app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image'
    app.config['DROPZONE_MAX_FILE_SIZE'] = 3  # MB
    app.config['DROPZONE_UPLOAD_DEST'] = 'app/static/uploads'

    db.init_app(app)
    dropzone.init_app(app)

    # Đăng ký routes
    from app.routes.admin import init_admin_routes
    from app.routes.user import init_user_routes
    init_admin_routes(app)
    init_user_routes(app)

    # Tạo database và dữ liệu mẫu
    with app.app_context():
        db.create_all()
        from app.models import User, Product, Order
        if not User.query.first():
            admin = User(lastname='Admin', firstname='User', username='admin', email='admin123@gmail.com', phone='0123456789', password='admin123', is_admin=True, is_locked=False)
            db.session.add(admin)
            db.session.commit()
        if not Product.query.first():
            sample_products = [
                Product(name='Sách Harry Potter', price=200000, discount=10, image='/static/image/logo.png', description='Cuốn sách nổi tiếng', category='Truyện Trinh Thám'),
                Product(name='Văn Học Việt Nam', price=150000, discount=5, image='', description='Tuyển tập văn học', category='Văn Học Việt Nam'),
            ]
            db.session.bulk_save_objects(sample_products)
            db.session.commit()

    return app