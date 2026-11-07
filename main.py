from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title='CRUD')

user_list = []
users_id_list = []
users_unique = []
next_id = 0

@app.get('/users')
async def get_users():
    return user_list

@app.post('/register')
async def get_users(username:str , password:str , password1:str):
    global next_id
    if password != password1:
        return {'Passwords do not match'}
    if username in users_unique:
        return {'Username already exists'}
    next_id += 1
    user = {
        'id' : next_id ,
        'username' : username ,
        'password' : password
    }
    user_list.append(user)
    users_id_list.append(user['id'])
    users_unique.append(user['username'])
    return user

user_id = None

@app.post('/login')
async def login(username:str , password:str) :
    global user_id
    for user in user_list:
        if user['username'] == username and user['password'] == password:
            user_id = user['id']
            return {'Login Successfully'}
    return {'Username or password is not correct. User not Found'}


@app.delete('/logout')
async def logout():
    global user_id
    if user_id:
        user_id = None
        return {'Logout Succesfully'}
    return {'Must be logined to logout'}

category_list = []
category_id_list = []
category_id_next = 0

@app.post('/add_category')
async def add_category(name:str):
    global category_id_next
    category_id_next += 1
    category = {
        'id' : category_id_next,
        'name' : name
    }
    category_list.append(category)
    category_id_list.append(category['id'])
    return category

@app.delete('/del_category')
async def delete_category(id:int):
    for cat in category_list:
        if cat['id'] == id:
            category_list.remove(cat)
            return {'Category deleted'}
    return {'Category not found'}


product_list = []
product_id_next = 0

order_list = []
order_id_next = 0

order_items_list = []
order_item_id_next = 0


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1)
    password: str | None = Field(default=None, min_length=1)

class CategoryUpdate(BaseModel):
    name: str = Field(min_length=1)

class ProductCreate(BaseModel):
    title: str = Field(min_length=1)
    price: float = Field(gt=0)
    category_id: int

class ProductUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    price: float | None = Field(default=None, gt=0)
    category_id: int | None = None

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


@app.get('/users/{user_id}')
async def get_user(user_id:int):
    for user in user_list:
        if user['id'] == user_id:
            return {'id' : user['id'], 'username' : user['username']}
    return {'User not found'}

@app.patch('/users/{user_id}')
async def update_user(user_id:int, data:UserUpdate):
    for user in user_list:
        if user['id'] == user_id:
            if data.username is not None and data.username != user['username']:
                if data.username in users_unique:
                    return {'Username already exists'}
                users_unique.remove(user['username'])
                users_unique.append(data.username)
                user['username'] = data.username
            if data.password is not None:
                user['password'] = data.password
            return {'id' : user['id'], 'username' : user['username']}
    return {'User not found'}

@app.delete('/users/{user_id}')
async def delete_user(user_id:int):
    for user in user_list:
        if user['id'] == user_id:
            for order in order_list:
                if order['user_id'] == user_id:
                    return {'User has orders'}
            user_list.remove(user)
            users_id_list.remove(user['id'])
            users_unique.remove(user['username'])
            return {'User deleted'}
    return {'User not found'}


@app.get('/categories/{category_id}')
async def get_category(category_id:int):
    for cat in category_list:
        if cat['id'] == category_id:
            return cat
    return {'Category not found'}

@app.put('/categories/{category_id}')
async def update_category(category_id:int, data:CategoryUpdate):
    if not data.name.strip():
        return {'Name can not be empty'}
    for cat in category_list:
        if cat['id'] == category_id:
            cat['name'] = data.name.strip()
            return cat
    return {'Category not found'}

@app.delete('/categories/{category_id}')
async def delete_category_by_id(category_id:int):
    for cat in category_list:
        if cat['id'] == category_id:
            for product in product_list:
                if product['category_id'] == category_id:
                    return {'Category has products'}
            category_list.remove(cat)
            category_id_list.remove(cat['id'])
            return {'Category deleted'}
    return {'Category not found'}

@app.get('/categories/{category_id}/products')
async def get_category_products(category_id:int):
    if category_id not in category_id_list:
        return {'Category not found'}
    result = []
    for product in product_list:
        if product['category_id'] == category_id:
            result.append(product)
    return result


@app.get('/products')
async def get_products():
    return product_list

@app.post('/products')
async def add_product(data:ProductCreate):
    global product_id_next
    if data.category_id not in category_id_list:
        return {'Category not found'}
    product_id_next += 1
    product = {
        'id' : product_id_next,
        'title' : data.title,
        'price' : data.price,
        'category_id' : data.category_id
    }
    product_list.append(product)
    return product

@app.get('/products/search')
async def search_products(title:str):
    result = []
    for product in product_list:
        if title.lower() in product['title'].lower():
            result.append(product)
    return result

@app.get('/products/filter')
async def filter_products(min_price:float = None, max_price:float = None):
    if min_price is not None and max_price is not None and min_price > max_price:
        return {'min_price can not be greater than max_price'}
    result = []
    for product in product_list:
        if min_price is not None and product['price'] < min_price:
            continue
        if max_price is not None and product['price'] > max_price:
            continue
        result.append(product)
    return result

@app.get('/products/{product_id}')
async def get_product(product_id:int):
    for product in product_list:
        if product['id'] == product_id:
            category_name = None
            for cat in category_list:
                if cat['id'] == product['category_id']:
                    category_name = cat['name']
            return {**product, 'category_name' : category_name}
    return {'Product not found'}

@app.patch('/products/{product_id}')
async def update_product(product_id:int, data:ProductUpdate):
    for product in product_list:
        if product['id'] == product_id:
            if data.category_id is not None and data.category_id not in category_id_list:
                return {'Category not found'}
            if data.title is not None:
                product['title'] = data.title
            if data.price is not None:
                product['price'] = data.price
            if data.category_id is not None:
                product['category_id'] = data.category_id
            return product
    return {'Product not found'}

@app.delete('/products/{product_id}')
async def delete_product(product_id:int):
    for product in product_list:
        if product['id'] == product_id:
            for item in order_items_list:
                if item['product_id'] == product_id:
                    return {'Product is in orders'}
            product_list.remove(product)
            return {'Product deleted'}
    return {'Product not found'}


@app.post('/orders')
async def add_order(user_id:int):
    global order_id_next
    if user_id not in users_id_list:
        return {'User not found'}
    order_id_next += 1
    order = {
        'id' : order_id_next,
        'user_id' : user_id
    }
    order_list.append(order)
    return order

@app.get('/orders/{order_id}')
async def get_order(order_id:int):
    for order in order_list:
        if order['id'] == order_id:
            items = []
            for item in order_items_list:
                if item['order_id'] == order_id:
                    product_info = None
                    for product in product_list:
                        if product['id'] == item['product_id']:
                            product_info = product
                    items.append({**item, 'product' : product_info})
            return {**order, 'items' : items}
    return {'Order not found'}

@app.post('/orders/{order_id}/items')
async def add_order_item(order_id:int, data:OrderItemCreate):
    global order_item_id_next
    order_found = False
    for order in order_list:
        if order['id'] == order_id:
            order_found = True
    if not order_found:
        return {'Order not found'}

    price = None
    for product in product_list:
        if product['id'] == data.product_id:
            price = product['price']
    if price is None:
        return {'Product not found'}

    for item in order_items_list:
        if item['order_id'] == order_id and item['product_id'] == data.product_id:
            item['quantity'] += data.quantity
            return item

    order_item_id_next += 1
    item = {
        'id' : order_item_id_next,
        'order_id' : order_id,
        'product_id' : data.product_id,
        'quantity' : data.quantity,
        'price' : price
    }
    order_items_list.append(item)
    return item

@app.get('/orders/{order_id}/total')
async def get_order_total(order_id:int):
    order_found = False
    for order in order_list:
        if order['id'] == order_id:
            order_found = True
    if not order_found:
        return {'Order not found'}
    total = 0
    for item in order_items_list:
        if item['order_id'] == order_id:
            total += item['price'] * item['quantity']
    return {'order_id' : order_id, 'total' : total}


