def show_store_items(store):
    print("\nItem Id\t\tItem Name\t\tUnit Price\tQuantity")
    for item_id, item_info in store.items():
        print(f"{item_id}\t\t{item_info[0]}\t\t{item_info[1]}\t\t{item_info[2]}")

def show_cart(cart):
    if not cart:
        print("\nThe shopping cart is empty.")
        return

    print("\nOrder Id\tItem Name\t\tItem Price\tQuantity")
    total_amount = 0
    for order_id, order_info in enumerate(cart, 1):
        print(f"{order_id}\t{order_info['name']}\t{order_info['price']}\t{order_info['quantity']}")
        total_amount += order_info['price'] * order_info['quantity']
    print(f"\nTotal amount: {total_amount}")

def add_to_cart(store, cart):
    item_id = input("Enter the Item Id to add to the cart: ")
    if item_id not in store:
        print("Invalid Item Id. Please try again.")
        return

    
    quantity = int(input("Enter the quantity: "))
    if quantity <= 0 or quantity > store[item_id][2]:
        print("Invalid quantity. Please try again.")
        return
    

    cart.append({
        'name': store[item_id][0],
        'price': store[item_id][1],
        'quantity': quantity
    })
    store[item_id][2] -= quantity
    print(f"\n{store[item_id][0]} added to the cart.")

def remove_from_cart(store, cart):
    if not cart:
        print("\nThe shopping cart is empty.")
        return


    order_id = int(input("Enter the Order Id to remove: "))
    if order_id <= 0 or order_id > len(cart):
        print("Invalid Order Id. Please try again.")
        return
    

    removed_item = cart.pop(order_id - 1)
    for item_id, item_info in store.items():
        if item_info[0] == removed_item['name']:
            item_info[2] += removed_item['quantity']
            break

    print(f"\n{removed_item['name']} removed from the cart.")

def save_and_quit(cart):
        print("\nShopping cart saved. Goodbye!")

def main():
    store = {
        "1": ["HP Laptop", 1500, 10],
        "2": ["Epson printer", 500, 5],
        "3": ["Acer Desktop", 1100, 20]
    }
    cart = []

    while True:
        print("""
***************************************************************************************
		Welcome to the Store
***************************************************************************************
1- Show the items in the store
2- Show the items in the shopping cart
3- Add an item to the cart
4- Remove an item from the cart
5- Save and Quit
        """)
        choice = input("Enter your choice: ")

        if choice == "1":
            show_store_items(store)
        elif choice == "2":
            show_cart(cart)
        elif choice == "3":
            add_to_cart(store, cart)
        elif choice == "4":
            remove_from_cart(store, cart)
        elif choice == "5":
            save_and_quit(cart)
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
