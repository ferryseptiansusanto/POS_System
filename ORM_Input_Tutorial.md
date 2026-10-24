# 📖 Dokumentasi Lengkap CRUD ORM

Gunakan *snippet* kode di bawah ini sebagai referensi cara melakukan **Create, Update, dan Delete** ke masing-masing tabel menggunakan arsitektur `eloquent_base.py`.

## Tabel `customers` (Model: `Customer`)
### 1. Create (Insert Data)
```python
new_customer = Customer.create(
    full_name='full_name_value',
    company_name='company_name_value',
    phone_number='08123456789',
    address='address_value',
    status='active',
)
print(f'Customer berhasil dibuat dengan ID: {new_customer.id}')
```

### 2. Update Data
```python
record = Customer.query().first()
if record:
    record.full_name = 'full_name_updated'
    record.save()
    print('Data berhasil di-update!')
```

### 3. Delete Data
```python
record = Customer.query().first()
if record:
    record.delete()
    print('Data berhasil dihapus dari database!')
```

---

## Tabel `items` (Model: `Item`)
### 1. Create (Insert Data)
```python
new_item = Item.create(
    sku='sku_value',
    name='name_value',
    category='category_value',
    unit='unit_value',
    buy_price=150000,
    sell_price=150000,
    stock=10,
)
print(f'Item berhasil dibuat dengan ID: {new_item.id}')
```

### 2. Update Data
```python
record = Item.query().first()
if record:
    record.sku = 'sku_updated'
    record.save()
    print('Data berhasil di-update!')
```

### 3. Delete Data
```python
record = Item.query().first()
if record:
    record.delete()
    print('Data berhasil dihapus dari database!')
```

---

## Tabel `purchases` (Model: `Purchase`)
### 1. Create (Insert Data)
```python
from eloquent_base import DatabaseManager

# Menggunakan Transaction untuk Master-Detail
with DatabaseManager.transaction():
    # 1. Simpan Master (Purchase)
    new_master = Purchase.create(
        purchase_no='purchase_no_value',
        supplier_id=1,
        user_id=1,
        total_amount=150000,
        status='active',
    )

    # 2. Simpan Detail (PurchaseDetail) menggunakan ID Master
    new_detail = PurchaseDetail.create(
        purchase_id=new_master.id,
        item_id=1,
        quantity=10,
        unit_price=150000,
        subtotal=150000,
    )
    print('Master dan Detail berhasil disimpan secara transaksional!')
```

### 2. Update Data
```python
record = Purchase.query().first()
if record:
    from eloquent_base import DatabaseManager
    
    # Menggunakan Transaction untuk Update Master sekaligus Menambah/Mengubah Detail
    with DatabaseManager.transaction():
        # 1. Update Field di Tabel Master
        record.purchase_no = 'purchase_no_updated'
        record.save()
        
        # 2. Tambahkan Data Detail Baru (contoh)
        PurchaseDetail.create(
            purchase_id=record.id,
            # ... isi field detail lainnya ...
        )
        print('Update Master dan penambahan Detail berhasil secara transaksional!')
```

### 3. Delete Data
```python
record = Purchase.query().first()
if record:
    record.delete()
    print('Data berhasil dihapus dari database!')
```

---

## Tabel `purchase_details` (Model: `PurchaseDetail`)
> ⚠️ **Catatan:** Tabel ini adalah tabel Detail. Untuk integritas data, sangat disarankan melakukan proses Create/Update bersamaan dengan tabel Master-nya menggunakan `DatabaseManager.transaction()`.

### 1. Create (Insert Data)
```python
# Ambil data parent (Foreign Key) yang dibutuhkan
purchase = Purchase.query().first()
item = Item.query().first()

new_purchasedetail = PurchaseDetail.create(
    purchase_id=purchase.id if purchase else 1,
    item_id=item.id if item else 1,
    quantity=10,
    unit_price=150000,
    subtotal=150000,
)
print(f'PurchaseDetail berhasil dibuat dengan ID: {new_purchasedetail.id}')
```

### 2. Update Data
```python
record = PurchaseDetail.query().first()
if record:
    record.quantity = 50
    record.save()
    print('Data berhasil di-update!')
```

### 3. Delete Data
```python
record = PurchaseDetail.query().first()
if record:
    record.delete()
    print('Data berhasil dihapus dari database!')
```

---

## Tabel `roles` (Model: `Role`)
### 1. Create (Insert Data)
```python
new_role = Role.create(
    name='name_value',
    description='description_value',
)
print(f'Role berhasil dibuat dengan ID: {new_role.id}')

# Hubungkan Relasi Many-to-Many
target = User.query().first()
if target:
    new_role._resolve_relation_object('users').attach(target.id)
    print('Relasi ke User berhasil di-attach!')
```

### 2. Update Data
```python
record = Role.query().first()
if record:
    record.name = 'name_updated'
    record.save()
    print('Data berhasil di-update!')
```

### 3. Delete Data
```python
record = Role.query().first()
if record:
    # Bersihkan relasi Many-to-Many di tabel pivot terlebih dahulu
    record._resolve_relation_object('users').detach()  # Menghapus semua relasi pivot
    record.delete()
    print('Data berhasil dihapus dari database!')
```

---

## Tabel `sales` (Model: `Sale`)
### 1. Create (Insert Data)
```python
from eloquent_base import DatabaseManager

# Menggunakan Transaction untuk Master-Detail
with DatabaseManager.transaction():
    # 1. Simpan Master (Sale)
    new_master = Sale.create(
        invoice_no='invoice_no_value',
        customer_id=1,
        user_id=1,
        subtotal_amount=150000,
        discount_amount=150000,
        total_amount=150000,
        payment_method='payment_method_value',
        payment_status='active',
    )

    # 2. Simpan Detail (SaleDetail) menggunakan ID Master
    new_detail = SaleDetail.create(
        sale_id=new_master.id,
        item_id=1,
        quantity=10,
        unit_price=150000,
        subtotal=150000,
    )
    print('Master dan Detail berhasil disimpan secara transaksional!')
```

### 2. Update Data
```python
record = Sale.query().first()
if record:
    from eloquent_base import DatabaseManager
    
    # Menggunakan Transaction untuk Update Master sekaligus Menambah/Mengubah Detail
    with DatabaseManager.transaction():
        # 1. Update Field di Tabel Master
        record.invoice_no = 'invoice_no_updated'
        record.save()
        
        # 2. Tambahkan Data Detail Baru (contoh)
        SaleDetail.create(
            sale_id=record.id,
            # ... isi field detail lainnya ...
        )
        print('Update Master dan penambahan Detail berhasil secara transaksional!')
```

### 3. Delete Data
```python
record = Sale.query().first()
if record:
    record.delete()
    print('Data berhasil dihapus dari database!')
```

---

## Tabel `sale_details` (Model: `SaleDetail`)
> ⚠️ **Catatan:** Tabel ini adalah tabel Detail. Untuk integritas data, sangat disarankan melakukan proses Create/Update bersamaan dengan tabel Master-nya menggunakan `DatabaseManager.transaction()`.

### 1. Create (Insert Data)
```python
# Ambil data parent (Foreign Key) yang dibutuhkan
sale = Sale.query().first()
item = Item.query().first()

new_saledetail = SaleDetail.create(
    sale_id=sale.id if sale else 1,
    item_id=item.id if item else 1,
    quantity=10,
    unit_price=150000,
    subtotal=150000,
)
print(f'SaleDetail berhasil dibuat dengan ID: {new_saledetail.id}')
```

### 2. Update Data
```python
record = SaleDetail.query().first()
if record:
    record.quantity = 50
    record.save()
    print('Data berhasil di-update!')
```

### 3. Delete Data
```python
record = SaleDetail.query().first()
if record:
    record.delete()
    print('Data berhasil dihapus dari database!')
```

---

## Tabel `suppliers` (Model: `Supplier`)
### 1. Create (Insert Data)
```python
new_supplier = Supplier.create(
    name='name_value',
    contact_person='contact_person_value',
    phone_number='08123456789',
    address='address_value',
)
print(f'Supplier berhasil dibuat dengan ID: {new_supplier.id}')
```

### 2. Update Data
```python
record = Supplier.query().first()
if record:
    record.name = 'name_updated'
    record.save()
    print('Data berhasil di-update!')
```

### 3. Delete Data
```python
record = Supplier.query().first()
if record:
    record.delete()
    print('Data berhasil dihapus dari database!')
```

---

## Tabel `users` (Model: `User`)
### 1. Create (Insert Data)
```python
new_user = User.create(
    username='username_value',
    password_hash='secret',
    full_name='full_name_value',
    status='active',
)
print(f'User berhasil dibuat dengan ID: {new_user.id}')

# Hubungkan Relasi Many-to-Many
target = Role.query().first()
if target:
    new_user._resolve_relation_object('roles').attach(target.id)
    print('Relasi ke Role berhasil di-attach!')
```

### 2. Update Data
```python
record = User.query().first()
if record:
    record.username = 'username_updated'
    record.save()
    print('Data berhasil di-update!')
```

### 3. Delete Data
```python
record = User.query().first()
if record:
    # Bersihkan relasi Many-to-Many di tabel pivot terlebih dahulu
    record._resolve_relation_object('roles').detach()  # Menghapus semua relasi pivot
    record.delete()
    print('Data berhasil dihapus dari database!')
```

---
