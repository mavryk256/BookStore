from flask import render_template, request, redirect, url_for, flash, session
from app import db
from app.models import User, Product, Order
from werkzeug.utils import secure_filename
import os


def init_admin_routes(app):
    def is_admin():
        return 'username' in session and User.query.filter_by(username=session['username'], is_admin=True).first()

    @app.route('/admin/products', methods=['GET', 'POST'])
    def manage_products():
        if not is_admin():
            flash('Bạn không có quyền truy cập trang này.')
            return redirect(url_for('login'))

        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'add':
                name = request.form['name']
                price = float(request.form['price'])
                discount = float(request.form['discount']) if request.form['discount'] else 0.0
                description = request.form['description']
                category = request.form['category']
                image = 'default.jpg'
                if 'file' in request.files:
                    file = request.files['file']
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        file.save(os.path.join('app/static/image', filename))
                        image = filename
                new_product = Product(name=name, price=price, discount=discount, image=image, description=description,
                                      category=category)
                db.session.add(new_product)
                db.session.commit()
                flash('Thêm sản phẩm thành công!')
            elif action == 'edit':
                product_id = int(request.form['product_id'])
                product = Product.query.get(product_id)
                if product:
                    product.name = request.form['name']
                    product.price = float(request.form['price'])
                    product.discount = float(request.form['discount']) if request.form['discount'] else 0.0
                    product.description = request.form['description']
                    product.category = request.form['category']
                    if 'file' in request.files:
                        file = request.files['file']
                        if file and file.filename:
                            filename = secure_filename(file.filename)
                            file.save(os.path.join('app/static/image', filename))
                            product.image = filename
                    db.session.commit()
                    flash('Sửa sản phẩm thành công!')
            elif action == 'delete':
                product_id = int(request.form['product_id'])
                product = Product.query.get(product_id)
                if product:
                    db.session.delete(product)
                    db.session.commit()
                    flash('Xóa sản phẩm thành công!')

        products = Product.query.all()
        return render_template('admin/manage_products.html', products=products)

    @app.route('/admin/users', methods=['GET', 'POST'])
    def manage_users():
        if not is_admin():
            flash('Bạn không có quyền truy cập trang này.')
            return redirect(url_for('login'))

        if request.method == 'POST':
            user_id = int(request.form['user_id'])
            action = request.form['action']
            user = User.query.get(user_id)
            if user:
                if action == 'delete':
                    db.session.delete(user)
                    db.session.commit()
                    flash('Xóa tài khoản thành công!')
                elif action == 'lock':
                    user.is_locked = True
                    db.session.commit()
                    flash('Khóa tài khoản thành công!')
                elif action == 'unlock':
                    user.is_locked = False
                    db.session.commit()
                    flash('Mở khóa tài khoản thành công!')

        users = User.query.filter_by(is_admin=False).all()
        return render_template('admin/manage_users.html', users=users)

    @app.route('/admin/orders', methods=['GET', 'POST'])
    def manage_orders():
        if not is_admin():
            flash('Bạn không có quyền truy cập trang này.')
            return redirect(url_for('login'))

        if request.method == 'POST':
            order_id = int(request.form['order_id'])
            new_status = request.form['status']
            order = Order.query.get(order_id)
            if order:
                order.status = new_status
                db.session.commit()
                flash('Cập nhật trạng thái đơn hàng thành công!')

        orders = Order.query.all()
        return render_template('admin/manage_orders.html', orders=orders)

    @app.route('/admin/user/<int:user_id>')
    def view_user(user_id):
        if not is_admin():
            flash('Bạn không có quyền truy cập trang này.')
            return redirect(url_for('login'))

        user = User.query.get_or_404(user_id)
        orders = Order.query.filter_by(user_id=user.id).all()
        return render_template('admin/view_user.html', user=user, orders=orders)