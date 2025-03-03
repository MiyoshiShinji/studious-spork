from flask import Blueprint, render_template, request, jsonify
from .models import Food, Order, OrderItem
from . import db

views = Blueprint('views', __name__) 


@views.route('/')
def home():
    order = Order.query.all()
    order_item = OrderItem.query.all()

    # Calcular as somas das quantidades de OrderItem com o mesmo food_id
    quantities = {}
    for item in order_item:
        if item.food_id in quantities:
            quantities[item.food_id] += item.quantity
        else:
            quantities[item.food_id] = item.quantity

    show_section1 = OrderItem.query.filter_by(food_id=1).first() is not None
    show_section2 = OrderItem.query.filter_by(food_id=2).first() is not None
    show_section3 = OrderItem.query.filter_by(food_id=3).first() is not None
    show_section4 = OrderItem.query.filter_by(food_id=4).first() is not None
    show_section5 = OrderItem.query.filter_by(food_id=5).first() is not None

    return render_template('home.html', order=order, order_item=order_item, quantities=quantities, show_section1=show_section1, show_section2=show_section2, show_section3=show_section3, show_section4=show_section4, show_section5=show_section5)

@views.route('/foodSelection')
def foodSelection():
    order = Order.query.all()
    return render_template('foodSelection.html', order=order)






@views.route('/create_order', methods=['POST'])
def create_order():
    data = request.get_json()
    quantities = data.get('quantities') #(food)food_id, (orderItem)quantity

    if not quantities:
        return jsonify({'success': False, 'message': 'No quantities provided'}), 400

    order = Order.query.all()
    if not order:
        new_order = Order(tot_bill=0, table_id=1)  
        db.session.add(new_order)
        db.session.commit()

        total_bill = 0

        # Cria OrderItems para cada quantidade
        for item in quantities:
            food = Food.query.get(item['food_id'])
            if food:
                order_item = OrderItem(
                    order_id=new_order.id,
                    food_id=item['food_id'],
                    quantity=item['quantity'],
                    table_id=1  # Ajuste conforme necessário
                )
                db.session.add(order_item)
                total_bill += item['quantity'] * food.price

        # Atualiza o valor total da conta no Order
        new_order.tot_bill = total_bill
        db.session.commit()
        return jsonify({'success': True}), 200
    
    
    
    
    
    total_bill = order[0].tot_bill

    # Cria OrderItems para cada quantidade
    for item in quantities:
        food = Food.query.get(item['food_id'])
        if food:
            order_item = OrderItem(
                order_id=1,
                food_id=item['food_id'],
                quantity=item['quantity'],
                table_id=1  # Ajuste conforme necessário
            )
            db.session.add(order_item)
            db.session.commit()

    for item in quantities:
        food = Food.query.get(item['food_id'])
        total_bill += item['quantity'] * food.price
    
    order[0].tot_bill = total_bill
    db.session.commit()
    return jsonify({'success': True}), 200

@views.route('/delete_orders', methods=['POST'])
def delete_orders():
    try:
        Order.query.delete()
        OrderItem.query.delete()
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@views.route('/delete_order_items', methods=['POST'])
def delete_order_items():
    data = request.get_json()
    food_id = data.get('food_id')
    
    if food_id is None:
        return jsonify({'success': False, 'message': 'No food_id provided'}), 400

    try:
        # Get the price of the food item
        food = Food.query.filter_by(id=food_id).first()
        if not food:
            return jsonify({'success': False, 'message': 'Food item not found'}), 404

        # Calculate the total amount to be subtracted from the order's total bill
        order_items_to_delete = OrderItem.query.filter_by(food_id=food_id).all()
        total_to_subtract = sum(item.quantity * food.price for item in order_items_to_delete)

        # Update the order's total bill
        order = Order.query.first()  # Adjust this if you need to target a specific order
        if order:
            order.tot_bill -= total_to_subtract

        # Delete the order items
        OrderItem.query.filter_by(food_id=food_id).delete()
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
    

@views.route('/update_order_item', methods=['POST'])
def update_order_item():
    data = request.get_json()
    food_id = data['food_id']
    quantity = data['quantity']
    print(f"Received update request: food_id={food_id}, quantity={quantity}")

    try:
        order_item = OrderItem.query.filter_by(food_id=food_id).first()
        if order_item:
            order_item.quantity = quantity
        else:
            order_item = OrderItem(food_id=food_id, quantity=quantity)
            db.session.add(order_item)

        db.session.commit()

        recalculate_tot_bill()

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        print(f"Error updating order item: {e}")
        return jsonify({'success': False, 'error': str(e)})

@views.route('/delete_order_item', methods=['POST'])
def delete_order_item():
    data = request.get_json()
    food_id = data['food_id']
    print(f"Received delete request: food_id={food_id}")

    try:
        order_item = OrderItem.query.filter_by(food_id=food_id).first()
        if order_item:
            db.session.delete(order_item)
            db.session.commit()

        recalculate_tot_bill()

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting order item: {e}")
        return jsonify({'success': False, 'error': str(e)})
    

def recalculate_tot_bill():
    try:
        order_items = OrderItem.query.all()
        total_bill = 0
        for item in order_items:
            food = Food.query.filter_by(id=item.food_id).first()
            if food:
                total_bill += item.quantity * food.price

        order = Order.query.first()  # Ajuste isso se precisar direcionar um pedido específico
        if order:
            order.tot_bill = total_bill
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error recalculating total bill: {e}")


if __name__ == '__main__':
    views.run(debug=True)










#<td>{{ foods[0].name }}</td>
#<td>{{ foods[0].content }}</td>