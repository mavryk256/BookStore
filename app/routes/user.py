import re
from flask import render_template, request, redirect, url_for, session, make_response, jsonify
from app import db
from app.models import User, Product, Order

def init_user_routes(app):
    @app.route('/home')
    @app.route('/')
    def home():
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
            if user and user.is_admin:
                return redirect(url_for('admin'))
        products = Product.query.all()
        user = User.query.filter_by(username=session.get('username')).first() if 'username' in session else None
        orders = Order.query.filter_by(user_id=user.id, status='Chờ duyệt').all() if user else []
        return render_template('home.html', products=products, orders=orders)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            lastname = request.form['lastname']
            firstname = request.form['firstname']
            username = request.form['username']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            confirm_password = request.form['confirm-password']

            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_pattern, email):
                return render_template('register.html', alert_message="Email không hợp lệ!")

            if len(password) < 8:
                return render_template('register.html', alert_message="Mật khẩu phải từ 8 ký tự trở lên!")

            if User.query.filter((User.username == username) | (User.email == email)).first():
                return render_template('register.html', alert_message="Tên người dùng hoặc email đã tồn tại!")

            if password != confirm_password:
                return render_template('register.html', alert_message="Mật khẩu không khớp!")

            new_user = User(lastname=lastname, firstname=firstname, username=username, email=email, phone=phone,
                            password=password)
            db.session.add(new_user)
            db.session.commit()
            return render_template('register.html', alert_message="Đăng ký thành công! Vui lòng đăng nhập.")

        response = make_response(render_template('register.html'))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
            if user:
                return redirect(url_for('home' if not user.is_admin else 'admin'))
            else:
                session.pop('username', None)

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter((User.username == username) | (User.email == username)).first()
            if user:
                if user.password == password:
                    if user.is_locked:
                        return render_template('login.html', alert_message="Tài khoản của bạn đã bị khóa!")
                    session.permanent = True
                    session['username'] = user.username
                    # Order.query.filter_by(user_id=user.id, status='Chờ duyệt').delete()
                    # db.session.commit()
                    return render_template('login.html', alert_message="Đăng nhập thành công!", redirect_url=url_for('home' if not user.is_admin else 'admin'))
                else:
                    return render_template('login.html', alert_message="Mật khẩu không đúng!")
            else:
                return render_template('login.html', alert_message="Tên người dùng hoặc email không tồn tại!")

        response = make_response(render_template('login.html'))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response

    @app.route('/logout')
    def logout():
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
            # if user:
            #     Order.query.filter_by(user_id=user.id, status='Chờ duyệt').delete()
            #     db.session.commit()
            session.pop('username', None)
        return redirect(url_for('home'))

    @app.route('/products')
    def products():
        products = Product.query.all()
        return render_template('products.html', products=products)

    @app.route('/products/<int:product_id>')
    def product_detail(product_id):
        product = Product.query.get_or_404(product_id)
        return render_template('product_detail.html', product=product)

    @app.route('/cart', methods=['GET', 'POST'])
    def cart():
        if 'username' not in session:
            return render_template('login.html', alert_message="Vui lòng đăng nhập để đặt hàng!", redirect_url=url_for('login'))

        user = User.query.filter_by(username=session['username']).first()
        if request.method == 'POST':
            product_id = int(request.form['product_id'])
            quantity = int(request.form.get('quantity', 1))
            product = Product.query.get(product_id)
            if product:
                effective_discount = min(product.discount, 1.0)
                total_price = max(0, (product.price - (product.price * effective_discount) / 100) * quantity)
                new_order = Order(user_id=user.id, product_id=product_id, quantity=quantity, total_price=total_price)
                db.session.add(new_order)
                db.session.commit()

                session['alert_message'] = f"Đã thêm {quantity} {product.name} vào giỏ hàng!"
                return redirect(url_for('cart'))

        alert_message = session.pop('alert_message', None)
        orders = Order.query.filter_by(user_id=user.id, status='Chờ duyệt').all()
        return render_template('user/cart.html', orders=orders, alert_message=alert_message)

    @app.route('/cart/delete/<int:order_id>', methods=['POST'])
    def delete_order(order_id):
        if 'username' not in session:
            return render_template('login.html', alert_message="Vui lòng đăng nhập để thực hiện thao tác này!",
                                   redirect_url=url_for('login'))

        user = User.query.filter_by(username=session['username']).first()
        if not user:
            session.pop('username', None)
            return render_template('login.html', alert_message="Phiên đăng nhập không hợp lệ! Vui lòng đăng nhập lại.",
                                   redirect_url=url_for('login'))

        order = Order.query.filter_by(id=order_id, user_id=user.id, status='Chờ duyệt').first()
        if not order:
            session['alert_message'] = "Đơn hàng không tồn tại hoặc bạn không có quyền xóa!"
            return redirect(url_for('cart'))

        try:
            db.session.delete(order)
            db.session.commit()
            session['alert_message'] = "Đã xóa sản phẩm khỏi giỏ hàng!"
        except Exception as e:
            db.session.rollback()
            session['alert_message'] = f"Lỗi khi xóa sản phẩm: {str(e)}"

        return redirect(url_for('cart'))

    @app.route('/cart/update/<int:order_id>', methods=['POST'])
    def update_order_quantity(order_id):
        if 'username' not in session:
            return jsonify({"success": False, "message": "Vui lòng đăng nhập để thực hiện thao tác này!"}), 401

        user = User.query.filter_by(username=session['username']).first()
        if not user:
            return jsonify({"success": False, "message": "Phiên đăng nhập không hợp lệ! Vui lòng đăng nhập lại."}), 401

        order = Order.query.filter_by(id=order_id, user_id=user.id, status='Chờ duyệt').first()
        if not order:
            return jsonify({"success": False, "message": "Đơn hàng không tồn tại hoặc bạn không có quyền chỉnh sửa!"}), 404

        try:
            new_quantity = int(request.form.get('quantity', 1))
            if new_quantity < 1:
                return jsonify({"success": False, "message": "Số lượng phải lớn hơn 0!"}), 400

            # Cập nhật số lượng và tổng giá
            product = Product.query.get(order.product_id)
            if not product:
                return jsonify({"success": False, "message": "Sản phẩm không tồn tại!"}), 404

            effective_discount = min(product.discount, 1.0)
            order.quantity = new_quantity
            order.total_price = max(0, (product.price - (product.price * effective_discount) / 100) * new_quantity)

            db.session.commit()
            return jsonify({
                "success": True,
                "message": f"Đã cập nhật số lượng cho {product.name}!",
                "total_price": order.total_price
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"Lỗi khi cập nhật số lượng: {str(e)}"}), 500

    @app.route('/checkout', methods=['POST'])
    def checkout():
        if 'username' not in session:
            return render_template('login.html', alert_message="Vui lòng đăng nhập để thanh toán!", redirect_url=url_for('login'))

        user = User.query.filter_by(username=session['username']).first()
        orders = Order.query.filter_by(user_id=user.id, status='Chờ duyệt').all()
        for order in orders:
            order.status = 'Đã thanh toán'
        db.session.commit()
        return redirect(url_for('profile'))

    @app.route('/account')
    def profile():
        if 'username' not in session:
            return render_template('login.html', alert_message="Vui lòng đăng nhập để xem trang này!", redirect_url=url_for('login'))
        user = User.query.filter_by(username=session['username']).first()
        orders = Order.query.filter_by(user_id=user.id).all()
        return render_template('user/profile.html', user=user, orders=orders)

    @app.route('/account/update', methods=['POST'])
    def update_profile():
        if 'username' not in session:
            return render_template('login.html', alert_message="Vui lòng đăng nhập để thực hiện thao tác này!", redirect_url=url_for('login'))

        user = User.query.filter_by(username=session['username']).first()
        if request.method == 'POST':
            lastname = request.form['lastname']
            firstname = request.form['firstname']
            email = request.form['email']
            phone = request.form['phone']

            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_pattern, email):
                return render_template('user/profile.html', user=user, orders=Order.query.filter_by(user_id=user.id).all(),
                                       alert_message="Email không hợp lệ!")

            existing_user = User.query.filter(User.email == email, User.id != user.id).first()
            if existing_user:
                return render_template('user/profile.html', user=user, orders=Order.query.filter_by(user_id=user.id).all(),
                                       alert_message="Email đã được sử dụng bởi người dùng khác!")

            user.lastname = lastname
            user.firstname = firstname
            user.email = email
            user.phone = phone
            db.session.commit()
            return render_template('user/profile.html', user=user, orders=Order.query.filter_by(user_id=user.id).all(),
                                   alert_message="Cập nhật thông tin thành công!")

    @app.route('/admin/products')
    def admin():
        if 'username' not in session:
            return render_template('login.html', alert_message="Vui lòng đăng nhập với vai trò admin!", redirect_url=url_for('login'))
        user = User.query.filter_by(username=session['username']).first()
        if not user.is_admin:
            return render_template('home.html', alert_message="Bạn không có quyền truy cập trang admin!")
        return render_template('admin/manage_products.html', user=user)

    @app.route('/search')
    def search():
        category = request.args.get('category', '')
        query = request.args.get('q', '').strip()
        products = Product.query.all()
        if query:
            products = [p for p in products if query.lower() in p.name.lower()]
        if category:
            pass
        return render_template('search_results.html', products=products, query=query, category=category)