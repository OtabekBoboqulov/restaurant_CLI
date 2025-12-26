import os
import mysql.connector

from dotenv import load_dotenv
from colorama import init, Fore, Style
from datetime import datetime

init(autoreset=True)

load_dotenv()
DATABASE_NAME = os.getenv('DB_NAME')
DATABASE_HOST = os.getenv('DB_HOST')
DATABASE_USER = os.getenv('DB_USER')
PASSWORD = os.getenv('PASSWORD')


def show_table(cursor, table_name, to_print=True):
    cursor.execute(f'SELECT * FROM {DATABASE_NAME}.{table_name}')
    result = cursor.fetchall()
    column_names = cursor.column_names
    result.insert(0, column_names)
    if to_print:
        headers = result[0]
        col_widths = []
        num_cols = len(result[0])
        for col in range(num_cols):
            max_width = max(len(str(row[col])) for row in result)
            col_widths.append(max_width)
        if headers:
            header_row = " | ".join(str(headers[i]).ljust(col_widths[i]) for i in range(num_cols))
            print(header_row)
            print("-" * len(header_row))
        for row in result[1:]:
            print(" | ".join(str(row[i]).ljust(col_widths[i]) for i in range(num_cols)))
    return result


def update(cursor, db, table_name, column_name, new_value, *where_clauses):
    sql = f'UPDATE {DATABASE_NAME}.{table_name} SET {column_name} = "{new_value}" WHERE {where_clauses[0]}'
    for where_clause in where_clauses[1:]:
        sql += f' AND {where_clause}'
    cursor.execute(sql)
    db.commit()


def id_generate(cursor, table_name):
    data = show_table(cursor, table_name, to_print=False)
    if len(data) == 1:
        return '1'
    id_column = data[1][0]
    if not isinstance(id_column, int):
        id_column = id_column[0]
        id = id_column + str(len(data))
    else:
        id = str(len(data))
    return id


def insert(cursor, db, table_name, *values):
    id = id_generate(cursor, table_name)
    sql = f'INSERT INTO {DATABASE_NAME}.{table_name} VALUES ("{id}", {",".join(["%s"] * (len(values)))})'
    cursor.execute(sql, values)
    db.commit()
    return id


def delete(cursor, db, table_name, id, id_field_name='id'):
    cursor.execute(f'DELETE FROM {DATABASE_NAME}.{table_name} WHERE {id_field_name} = {id}')
    db.commit()


def print_columns(cursor, table_name):
    cursor.execute(f'DESCRIBE {DATABASE_NAME}.{table_name}')
    columns = cursor.fetchall()
    for column in columns[1:]:
        print(column[0], end='\t|\t')
    print()


def print_as_table(data, headers=None):
    if not data:
        print("No data to display")
        return
    all_rows = [headers] + data if headers else data
    col_widths = []
    num_cols = len(all_rows[0])
    for col in range(num_cols):
        max_width = max(len(str(row[col])) for row in all_rows)
        col_widths.append(max_width)
    if headers:
        header_row = " | ".join(str(headers[i]).ljust(col_widths[i]) for i in range(num_cols))
        print(header_row)
        print("-" * len(header_row))
    for row in data:
        print(" | ".join(str(row[i]).ljust(col_widths[i]) for i in range(num_cols)))


def show_orders(cursor, waiter_id):
    orders = show_table(cursor, 'orders', to_print=False)
    waiter_orders = []
    for order in orders[1:]:
        if order[2] == int(waiter_id):
            id = order[0]
            waiter_orders.append(id)
            cursor.execute(
                f'SELECT phone_number FROM {DATABASE_NAME}.customer WHERE id = {order[1]}')
            customer_phone_number = cursor.fetchall()[0][0]
            print(
                f'{id}. Order by customer with phone number {customer_phone_number} on {order[3].strftime("%Y/%m/%d %H:%M:%S")}')
    return waiter_orders


def show_bill(data):
    print(Fore.CYAN + "=" * 50)
    print(Fore.CYAN + "                    RECEIPT                    ")
    print(Fore.CYAN + "=" * 50)
    print()
    print(Fore.YELLOW + f"{'Item':<20} {'Price':>8} {'Qty':>5} {'Total':>10}")
    print(Fore.CYAN + "-" * 50)
    total_sum = 0
    for row in data:
        item_name = row[0]
        price = row[1]
        quantity = row[2]
        subtotal = price * quantity
        print(f"{Fore.WHITE}{item_name:<20} "
              f"{Fore.GREEN}${price:>7.2f} "
              f"{Fore.YELLOW}x{quantity:>4} "
              f"{Fore.GREEN}${subtotal:>9.2f}")
        total_sum += subtotal
    print(Fore.CYAN + "-" * 50)
    print(f"{Fore.WHITE}{'TOTAL:':<20} {Fore.GREEN + Style.BRIGHT}${total_sum:>28.2f}")
    print()
    print(Fore.MAGENTA + "-" * 50)
    print(f"{Fore.CYAN}Served by: {Fore.WHITE}{row[3]} {row[4]}")
    print(f"{Fore.CYAN}Date: {Fore.WHITE}{row[5].strftime('%Y/%m/%d %H:%M:%S')}")
    print(Fore.MAGENTA + "=" * 50)
    print(Fore.GREEN + Style.BRIGHT + "             Thank you for your visit!")
    print(Fore.MAGENTA + "=" * 50)


def main():
    my_cursor = None
    while not my_cursor:
        try:
            username = input("Enter your username: ")
            password = input("Enter your password or your waiter ID: ")
            if password == PASSWORD:
                status = 'admin'
            mydb = mysql.connector.connect(
                host=DATABASE_HOST,
                user=DATABASE_USER,
                passwd=PASSWORD,
                database=DATABASE_NAME
            )
            my_cursor = mydb.cursor()
            if password != PASSWORD:
                my_cursor.execute(f"SELECT id, first_name FROM {DATABASE_NAME}.staff")
                staff_ids = my_cursor.fetchall()
                for staff_id in staff_ids:
                    if password == str(staff_id[0]):
                        username = staff_id[1]
                        status = 'waiter'
                        break
                else:
                    my_cursor = None
                    raise mysql.connector.Error('Password or waiter id is invalid.')
        except mysql.connector.Error as err:
            print(Fore.RED + f"Failed to connect to MySQL: {err}")
    print(f'{Fore.GREEN}{Style.BRIGHT}Hello, {username}')
    while True:
        if status == 'waiter':
            message = '''Actions:
        1. Make order
        2. Edit order
        3. Get bill
        4. Exit'''
            print(Fore.BLUE + message)
            action = int(input('Choose action: '))
            try:
                match action:
                    case 1:
                        show_table(my_cursor, 'meal')
                        my_cursor.execute(f'SELECT id FROM meal')
                        meal_ids = list(zip(*my_cursor.fetchall()))[0]
                        order_id = insert(my_cursor, mydb, 'orders', 2, password, datetime.now())
                        meals = []
                        while True:
                            meal = input(
                                "Enter meal id and quantity (meal quantity)\n'c' for removing all meals\n'q' for quiting\n'a' for finishing order: ").lower()
                            if meal == 'q':
                                delete(my_cursor, mydb, 'orders', order_id)
                                print(Fore.GREEN + 'Order canceled successfully.')
                                meals = []
                                break
                            elif meal == 'c':
                                meals = []
                                print(Fore.GREEN + 'Order is now empty.')
                            elif meal == 'a':
                                break
                            else:
                                if not meal.isdigit():
                                    meal_id, quantity = map(int, meal.split())
                                else:
                                    meal_id, quantity = int(meal), 1
                                if meal_id not in meal_ids:
                                    print(Fore.RED + 'Meal id is not found')
                                else:
                                    meals.append((meal_id, quantity))
                        if meals:
                            for meal in meals:
                                insert(my_cursor, mydb, 'ordermeal', order_id, *meal)
                            print(Fore.GREEN + f'Order is accepted. Order id is {order_id}.')
                    case 2:
                        waiter_orders = show_orders(my_cursor, password)
                        order_id = input('Enter order you want to edit: ')
                        if int(order_id) not in waiter_orders:
                            raise Exception('Order id is invalid.')
                        my_cursor.execute(
                            f'SELECT ordermeal.id, name, quantity FROM {DATABASE_NAME}.ordermeal JOIN {DATABASE_NAME}.meal '
                            f'ON meal.id = meal_id WHERE order_id = {order_id}')
                        ordered_meals = my_cursor.fetchall()
                        if ordered_meals:
                            available_ids = list(zip(*ordered_meals))[0]
                        else:
                            available_ids = [-1]
                        print_as_table(ordered_meals, headers=('id', 'meal', 'quantity'))
                        order_meal_id = input(
                            'Enter id you want to edit\n"a" to append meal\n"c" to cancel order: ').lower()
                        if order_meal_id == "c":
                            delete(my_cursor, mydb, 'orders', order_id)
                            print(Fore.GREEN + 'Order canceled')
                        elif order_meal_id == "a":
                            show_table(my_cursor, 'meal')
                            meal = input('Enter meal id and quantity: ')
                            if meal.isdigit():
                                id, quantity = int(meal), 1
                            else:
                                id, quantity = map(int, meal.split())
                            insert(my_cursor, mydb, 'ordermeal', order_id, id, quantity)
                            print(Fore.GREEN + 'Meal added to order.')
                        else:
                            order_meal_id = int(order_meal_id)
                            if order_meal_id not in available_ids:
                                raise Exception('Meal id is invalid')
                            action = input('Enter "r" to remove meal from order\n"e" to edit its quantity: ')
                            match action:
                                case "r":
                                    delete(my_cursor, mydb, 'ordermeal', order_meal_id)
                                    print(Fore.GREEN + 'Meal removed from order.')
                                case "e":
                                    new_quantity = int(input("Enter new quantity: "))
                                    update(my_cursor, mydb, 'ordermeal', 'quantity', new_quantity,
                                           f'id = {order_meal_id}')
                                    print(Fore.GREEN + 'Quantity updated successfully.')
                    case 3:
                        waiter_orders = show_orders(my_cursor, password)
                        order_id = int(input('Choose order to get bills: '))
                        if order_id not in waiter_orders:
                            raise Exception('Order id is invalid')
                        my_cursor.execute(
                            f'SELECT name, price, quantity, first_name, last_name, ordered_date FROM {DATABASE_NAME}.orders '
                            f'JOIN {DATABASE_NAME}.ordermeal ON orders.id = order_id JOIN {DATABASE_NAME}.meal ON meal.id = meal_id '
                            f'JOIN {DATABASE_NAME}.staff ON staff.id = staff_id '
                            f'WHERE orders.id = {order_id}')
                        data = my_cursor.fetchall()
                        show_bill(data)
                    case 4:
                        break
            except Exception as e:
                print(Fore.RED + str(e))
        elif status == 'admin':
            message = '''Actions:
        1. Add meal
        2. Change meal info
        3. Delete meal
        4. Waiter sales info
        5. Sales by meals
        6. Exit'''
            print(Fore.BLUE + message)
            action = int(input('Choose action: '))
            try:
                match action:
                    case 1:
                        categories_data = show_table(my_cursor, 'category')
                        category_ids = list(zip(*categories_data[1:]))[0]
                        category_id = int(input('To which category you want to add meal? '))
                        if category_id not in category_ids:
                            raise Exception('Category id is invalid.')
                        my_cursor.execute(
                            f'SELECT id, `name`, price FROM {DATABASE_NAME}.meal WHERE category_id = {category_id}')
                        category_meals = my_cursor.fetchall()
                        print_as_table(category_meals, ('id', 'name', 'price'))
                        option = input(
                            'If you see meal you want to add in table above it means it already exists on database.\n'
                            'Enter "c" to cancel adding meal or "k" to keep going to add meal: ')
                        match option:
                            case 'c':
                                continue
                            case "k":
                                name = input("Enter a name of meal you want to add: ")
                                price = eval(input("Enter a price of meal you want to add: "))
                                insert(my_cursor, mydb, 'meal', category_id, name, price)
                        print(f'{Fore.GREEN}Meal added successfully.')
                    case 2:
                        meals_data = show_table(my_cursor, 'meal')
                        meal_ids = list(zip(*meals_data[1:]))[0]
                        meal_id = input('Choose meal to edit or "c" to cancel: ')
                        if meal_id == 'c':
                            continue
                        else:
                            meal_id = int(meal_id)
                        if meal_id not in meal_ids:
                            raise Exception('Meal id is invalid.')
                        new_price = eval(input('Enter new price for this meal: '))
                        update(my_cursor, mydb, 'meal', 'price', new_price, f'id = {meal_id}')
                        print(f'{Fore.GREEN}Meal price changed successfully.')
                    case 3:
                        meals_data = show_table(my_cursor, 'meal')
                        meal_ids = list(zip(*meals_data[1:]))[0]
                        meal_id = input('Choose meal to delete or "c" to cancel: ')
                        if meal_id == 'c':
                            continue
                        else:
                            meal_id = int(meal_id)
                        if meal_id not in meal_ids:
                            raise Exception('Meal id is invalid.')
                        confirmation = input(
                            f'{Fore.YELLOW}Are you sure you want to delete this meal(No/Yes)? ').lower()
                        if confirmation in ['y', 'yes', 'yeap', 'yeah']:
                            delete(my_cursor, mydb, 'meal', meal_id)
                            print(f'{Fore.GREEN}Meal deleted successfully.')
                    case 4:
                        my_cursor.execute(
                            f'SELECT staff.id, first_name, last_name, sum(price * quantity), count(distinct customer_id) FROM {DATABASE_NAME}.staff '
                            f'JOIN {DATABASE_NAME}.orders ON staff_id = staff.id '
                            f'JOIN {DATABASE_NAME}.ordermeal ON order_id = orders.id '
                            f'JOIN {DATABASE_NAME}.meal ON meal_id = meal.id '
                            'GROUP BY staff.id')
                        staff_data = my_cursor.fetchall()
                        headers = ('id', 'First Name', 'Last Name', 'Total served price', 'Customers served')
                        print_as_table(staff_data, headers)
                        message = '''You can use one of these filters:
        1. Ascending order by total served price
        2. Descending order by total served price
        3. Ascending order by customers served
        4. Descending order by customers served
        5. Main menu'''
                        print(Fore.BLUE + message)
                        fltr = int(input('Choose filter: '))
                        if fltr == 5:
                            continue
                        else:
                            limit = input('Enter number of staff you want to see (press <Enter> to see every staff): ')
                        filtered_data = []
                        match fltr:
                            case 1:
                                filtered_data = sorted(staff_data, key=lambda x: x[3])
                            case 2:
                                filtered_data = sorted(staff_data, key=lambda x: x[3], reverse=True)
                            case 3:
                                filtered_data = sorted(staff_data, key=lambda x: x[4])
                            case 4:
                                filtered_data = sorted(staff_data, key=lambda x: x[4], reverse=True)
                        if not limit:
                            print_as_table(filtered_data, headers)
                        else:
                            limit = int(limit)
                            print_as_table(filtered_data[:limit], headers)
                    case 5:
                        my_cursor.execute(f'SELECT meal.id, `name`, sum(price * quantity), sum(quantity) FROM {DATABASE_NAME}.meal '
                                          f'JOIN {DATABASE_NAME}.ordermeal ON meal_id = meal.id '
                                          'GROUP BY meal.id')
                        meal_data = my_cursor.fetchall()
                        headers = ('id', 'Name', 'Total sold price', 'Total sold number')
                        print_as_table(meal_data, headers)
                        message = '''You can use one of these filters:
        1. Ascending order by total sold price
        2. Descending order by total sold price
        3. Ascending order by total sold number
        4. Descending order by total sold number
        5. Main menu'''
                        print(Fore.BLUE + message)
                        fltr = int(input('Choose filter: '))
                        if fltr == 5:
                            continue
                        else:
                            limit = input('Enter number of staff you want to see (press <Enter> to see every staff): ')
                        filtered_data = []
                        match fltr:
                            case 1:
                                filtered_data = sorted(meal_data, key=lambda x: x[2])
                            case 2:
                                filtered_data = sorted(meal_data, key=lambda x: x[2], reverse=True)
                            case 3:
                                filtered_data = sorted(meal_data, key=lambda x: x[3])
                            case 4:
                                filtered_data = sorted(meal_data, key=lambda x: x[3], reverse=True)
                        if not limit:
                            print_as_table(filtered_data, headers)
                        else:
                            limit = int(limit)
                            print_as_table(filtered_data[:limit], headers)
                    case 6:
                        break
            except Exception as e:
                print(Fore.RED + str(e))


if __name__ == "__main__":
    main()
