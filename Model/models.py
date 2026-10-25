# Auto-generated code signature. Do not modify directly.
from typing import Any
from orm.eloquent_base import Model, relation

@relation
class User(Model):
    table: str = "users"
    primary_key: str = "id"
    fillable: list = ['username', 'password_hash', 'full_name', 'status']
    timestamps: bool = True
    soft_deletes: bool = False

    def roles(self) -> Any:
        return self.belongs_to_many(
            "Role",
            table="role_user",
            foreign_pivot_key="user_id",
            related_pivot_key="role_id"
        )

@relation
class Role(Model):
    table: str = "roles"
    primary_key: str = "id"
    fillable: list = ['name', 'description']
    timestamps: bool = True
    soft_deletes: bool = False

    def users(self) -> Any:
        return self.belongs_to_many(
            "User",
            table="role_user",
            foreign_pivot_key="role_id",
            related_pivot_key="user_id"
        )

@relation
class Customer(Model):
    table: str = "customers"
    primary_key: str = "id"
    fillable: list = ['full_name', 'company_name', 'phone_number', 'address', 'status']
    timestamps: bool = True
    soft_deletes: bool = False

@relation
class Supplier(Model):
    table: str = "suppliers"
    primary_key: str = "id"
    fillable: list = ['name', 'contact_person', 'phone_number', 'address']
    timestamps: bool = True
    soft_deletes: bool = False

@relation
class Item(Model):
    table: str = "items"
    primary_key: str = "id"
    fillable: list = ['sku', 'name', 'category', 'unit', 'buy_price', 'sell_price', 'stock']
    timestamps: bool = True
    soft_deletes: bool = False

@relation
class Sale(Model):
    table: str = "sales"
    primary_key: str = "id"
    fillable: list = ['invoice_no', 'customer_id', 'user_id', 'subtotal_amount', 'discount_amount', 'total_amount', 'payment_method', 'payment_status']
    timestamps: bool = True
    soft_deletes: bool = False

@relation
class SaleDetail(Model):
    table: str = "sale_details"
    primary_key: str = "id"
    fillable: list = ['sale_id', 'item_id', 'quantity', 'unit_price', 'subtotal']
    timestamps: bool = True
    soft_deletes: bool = False

@relation
class Purchase(Model):
    table: str = "purchases"
    primary_key: str = "id"
    fillable: list = ['purchase_no', 'supplier_id', 'user_id', 'total_amount', 'status']
    timestamps: bool = True
    soft_deletes: bool = False

@relation
class PurchaseDetail(Model):
    table: str = "purchase_details"
    primary_key: str = "id"
    fillable: list = ['purchase_id', 'item_id', 'quantity', 'unit_price', 'subtotal']
    timestamps: bool = True
    soft_deletes: bool = False
