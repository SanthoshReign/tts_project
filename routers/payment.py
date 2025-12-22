from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import getDb
from models.payment import PaymentItem, PaymentOrder
from schemas.payment import PaymentResponse, PaymentCreate, PaymentUpdate, PaymentItemUpdate

router = APIRouter(prefix="/payments", tags=["Payments"])

def calculate_order(items, tax_percent, other_charges, paid_amount):
    subtotal = sum(item.quantity * item.unit_price for item in items)

    tax_amount = subtotal * (tax_percent / 100)
    total_amount = subtotal + tax_amount + other_charges
    balance_amount = total_amount - paid_amount

    return {
        "subtotal": round(subtotal, 2),
        "tax_amount": round(tax_amount, 2),
        "total_amount": round(total_amount, 2),
        "balance_amount": round(balance_amount, 2)
    }

@router.post("/create", response_model=PaymentResponse)
def create_payment(
    data: PaymentCreate,
    db: Session = Depends(getDb)
):
    calc = calculate_order(
        items=data.items,
        tax_percent=data.tax_percent,
        other_charges=data.other_charges,
        paid_amount=data.paid_amount
    )

    if data.paid_amount > calc["total_amount"]:
        raise HTTPException(
            status_code=400,
            detail="Paid amount cannot exceed total amount"
        )

    payment = PaymentOrder(
        vendor_name=data.vendor_name,
        branch=data.branch,
        purchase_order_no = data.purchase_order_no,
        purchase_order_date = data.purchase_order_date,
        tax_percent=data.tax_percent,
        other_charges=data.other_charges,
        subtotal=calc["subtotal"],
        tax_amount=calc["tax_amount"],
        total_amount=calc["total_amount"],
        paid_amount=data.paid_amount,
        balance_amount=calc["balance_amount"],
        payment_method = data.payment_method,
        payment_date = data.payment_date
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    for item in data.items:
        db.add(
            PaymentItem(
                payment_id=payment.id,
                item_name=item.item_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_total=item.quantity * item.unit_price
            )
        )

    db.commit()

    return payment

# ------------------------------------------- GET ORDER ----------------------------------
@router.get('/get-items/{order_id}', response_model = PaymentResponse)
def get_order_details(order_id: int, db: Session = Depends(getDb)):
    order = db.query(PaymentOrder).filter(PaymentOrder.id == order_id).first()

    if not order:
        raise HTTPException(status_code = 404, detail = "Order not found")

    return order

# ------------------------------------------- UPDATE ITEMS -----------------------------------

def recalculate_order(order):
    subtotal = sum(item.quantity * item.unit_price for item in order.items)
    tax_amount = subtotal * (order.tax_percent / 100)
    total_amount = subtotal + tax_amount + order.other_charges
    balance_amount = total_amount - order.paid_amount

    order.subtotal = round(subtotal, 2)
    order.tax_amount = round(tax_amount, 2)
    order.total_amount = round(total_amount, 2)
    order.balance_amount = round(balance_amount, 2)


@router.patch("/update/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: int,
    data: PaymentUpdate,
    db: Session = Depends(getDb)
):
    payment = db.query(PaymentOrder).filter(PaymentOrder.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment order not found")

    # Update order-level fields
    for field, value in data.model_dump(exclude_unset=True).items():
        if field != "items":
            setattr(payment, field, value)

    # Update items if provided
    if data.items is not None:
        existing_items = {item.id: item for item in payment.items}

        for item_data in data.items:
            if item_data.id and item_data.id in existing_items:
                item = existing_items[item_data.id]
                if item_data.item_name:
                    item.item_name = item_data.item_name
                if item_data.quantity:
                    item.quantity = item_data.quantity
                if item_data.unit_price:
                    item.unit_price = item_data.unit_price
                item.line_total = item.quantity * item.unit_price
            else:
                # New item
                new_item = PaymentItem(
                    payment_id=payment.id,
                    item_name=item_data.item_name,
                    quantity=item_data.quantity,
                    unit_price=item_data.unit_price,
                    line_total=item_data.quantity * item_data.unit_price
                )
                db.add(new_item)

    # Recalculate totals
    recalculate_order(payment)

    db.commit()
    db.refresh(payment)

    return payment

# ---------------------------------------------- DELETE ITEM ---------------------------------
@router.delete("/delete-item/{item_id}")
def delete_payment_item(
    item_id: int,
    db: Session = Depends(getDb)
):
    item = db.query(PaymentItem).filter(PaymentItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Payment item not found")

    payment = db.query(PaymentOrder).filter(
        PaymentOrder.id == item.payment_id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Parent payment order not found")

    # Delete item
    db.delete(item)
    db.commit()

    # Recalculate totals
    subtotal = sum(i.quantity * i.unit_price for i in payment.items)
    tax_amount = subtotal * (payment.tax_percent / 100)
    total_amount = subtotal + tax_amount + payment.other_charges
    balance_amount = total_amount - payment.paid_amount

    payment.subtotal = round(subtotal, 2)
    payment.tax_amount = round(tax_amount, 2)
    payment.total_amount = round(total_amount, 2)
    payment.balance_amount = round(balance_amount, 2)

    db.commit()

    return {
        "message": "Payment item deleted successfully",
        "payment_id": payment.id,
        "updated_totals": {
            "subtotal": payment.subtotal,
            "tax_amount": payment.tax_amount,
            "total_amount": payment.total_amount,
            "balance_amount": payment.balance_amount
        }
    }

# ------------------------------------------ UPDATING A PARTICULAR ITEM -------------------------------------------------

@router.patch("/{order_id}/items/{item_id}")
def update_payment_item(
    order_id: int,
    item_id: int,
    data: PaymentItemUpdate,
    db: Session = Depends(getDb)
):
    # 🔹 Check order exists
    order = db.query(PaymentOrder).filter(PaymentOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Payment order not found")

    # 🔹 Check item belongs to order
    item = (
        db.query(PaymentItem)
        .filter(
            PaymentItem.id == item_id,
            PaymentItem.payment_id == order_id
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in this order")

    # Partial update
    if data.item_name is not None:
        item.item_name = data.item_name
    if data.quantity is not None:
        item.quantity = data.quantity
    if data.unit_price is not None:
        item.unit_price = data.unit_price

    # Recalculate item total
    item.line_total = item.quantity * item.unit_price

    # Recalculate order totals
    recalculate_order(order)

    db.commit()
    db.refresh(order)

    return {
        "message": "Item updated successfully",
        "order_id": order.id,
        "item_id": item.id,
        "updated_item": {
            "item_name": item.item_name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "line_total": item.line_total
        },
        "updated_totals": {
            "subtotal": order.subtotal,
            "tax_amount": order.tax_amount,
            "total_amount": order.total_amount,
            "balance_amount": order.balance_amount
        }
    }
