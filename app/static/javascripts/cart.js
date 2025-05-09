        async function updateQuantity(orderId, change) {
            let quantityInput = document.getElementById(`quantity-${orderId}`);
            let newQuantity = parseInt(quantityInput.value) + change;

            if (newQuantity < 1) {
                alert("Số lượng phải lớn hơn 0!");
                return;
            }

            try {
                const response = await fetch(`/cart/update/${orderId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `quantity=${newQuantity}`
                });

                const result = await response.json();

                if (result.success) {
                    quantityInput.value = newQuantity;
                    document.getElementById(`total-price-${orderId}`).textContent = new Intl.NumberFormat('vi-VN').format(result.total_price) + ' VND';
                } else {
                    alert(result.message || "Lỗi khi cập nhật số lượng!");
                }
            } catch (error) {
                alert("Lỗi khi cập nhật số lượng: " + error.message);
            }
        }