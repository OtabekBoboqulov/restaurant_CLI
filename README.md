# Restaurant Management System (Milliy Taomlar)

A Python-based restaurant management system with MySQL database integration, featuring order management, bill generation, and colorful console interface.

## Features

- **User Authentication**: Admin and waiter login system
- **Order Management**: Create, edit, and cancel orders
- **Bill Generation**: Beautiful, colorful receipt printing
- **Database Operations**: Full CRUD operations for orders and meals
- **Role-Based Access**: Different permissions for admin and waiters

## Prerequisites

- Python 3.10+
- MySQL Server
- Required Python packages:
  - `mysql-connector-python`
  - `colorama`
  - `python-dotenv`

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd milliy_taomlar
   ```

2. **Install dependencies**
   
   Option 1 - Using requirements.txt (recommended):
   ```bash
   pip install -r requirements.txt
   ```
   
   Option 2 - Manual installation:
   ```bash
   pip install mysql-connector-python colorama python-dotenv
   ```

3. **Set up MySQL Database**
   
   Create a database named `milliy_taomlar` with the following tables:

   ```sql
   CREATE DATABASE milliy_taomlar;
   USE milliy_taomlar;

   -- Category table
   CREATE TABLE category (
       id INT PRIMARY KEY,
       name VARCHAR(100)
   );

   -- Staff table
   CREATE TABLE staff (
       id INT PRIMARY KEY,
       first_name VARCHAR(50),
       last_name VARCHAR(50)
   );

   -- Customer table
   CREATE TABLE customer (
       id INT PRIMARY KEY AUTO_INCREMENT,
       phone_number VARCHAR(20)
   );

   -- Meal table
   CREATE TABLE meal (
       id INT PRIMARY KEY,
       category_id INT,
       name VARCHAR(100),
       price DECIMAL(10, 2),
       FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE CASCADE
   );

   -- Orders table
   CREATE TABLE orders (
       id INT PRIMARY KEY,
       customer_id INT,
       staff_id INT,
       ordered_date DATETIME,
       FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE CASCADE,
       FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE
   );

   -- OrderMeal junction table
   CREATE TABLE ordermeal (
       id INT PRIMARY KEY,
       order_id INT,
       meal_id INT,
       quantity INT,
       FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
       FOREIGN KEY (meal_id) REFERENCES meal(id) ON DELETE CASCADE
   );
   ```

4. **Configure Environment Variables**
   
   Create a `.env` file in the project root directory:
   ```env
   DB_NAME=milliy_taomlar
   DB_HOST=localhost
   DB_USER=root
   PASSWORD=your_database_password
   ```
   
   **Important**: Add `.env` to your `.gitignore` file to avoid committing sensitive credentials!

## Usage

### Running the Application

```bash
python main.py
```

### Login Credentials

- **Admin Access**: Use the password configured in your `.env` file (PASSWORD variable)
- **Waiter Access**: Use your waiter ID (staff ID from database)

### Waiter Features

1. **Make Order**
   - View available meals
   - Add meals to order with quantities
   - Options:
     - `meal_id quantity` - Add meal (e.g., `1 2` for 2 units of meal ID 1)
     - `meal_id` - Add single meal (quantity defaults to 1)
     - `c` - Clear all meals from current order
     - `q` - Cancel order
     - `a` - Finish and accept order

2. **Edit Order**
   - View your orders
   - Select order to edit
   - Options:
     - Edit meal quantities
     - Remove meals from order
     - Add new meals to order
     - Cancel entire order

3. **Get Bill**
   - View your orders
   - Select order to generate bill
   - Displays formatted receipt with:
     - Item details
     - Prices and quantities
     - Total amount
     - Waiter name
     - Date and time

4. **Exit**
   - Logout from the system

### Admin Features

1. **Add Meal**
   - View existing meal categories
   - Select category for new meal
   - Check if meal already exists in selected category
   - Add new meal with name and price

2. **Change Meal Info**
   - View all meals in database
   - Select meal to edit
   - Update meal price

3. **Delete Meal**
   - View all meals in database
   - Select meal to delete
   - Confirm deletion (cascades to related orders)

4. **Waiter Sales Info**
   - View comprehensive sales statistics per waiter:
     - Total revenue served
     - Number of customers served
   - Filter options:
     - Sort by total served price (ascending/descending)
     - Sort by customers served (ascending/descending)
     - Limit number of results displayed

5. **Sales by Meals**
   - View comprehensive sales statistics per meal:
     - Total revenue generated
     - Total quantity sold
   - Filter options:
     - Sort by total sold price (ascending/descending)
     - Sort by total sold number (ascending/descending)
     - Limit number of results displayed

6. **Exit**
   - Logout from the system

## Project Structure

```
milliy_taomlar/
│
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (DO NOT COMMIT)
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## Key Functions

- `show_table()` - Display database table contents
- `insert()` - Insert new records with auto-generated IDs
- `update()` - Update existing records
- `delete()` - Delete records from tables
- `show_orders()` - Display waiter's orders
- `show_bill()` - Generate formatted receipt
- `id_generate()` - Auto-generate unique IDs

## Color Scheme

The application uses colorama for colored console output:

- **Cyan**: Headers and separators
- **Yellow**: Column headers and quantities
- **Green**: Prices, totals, and success messages
- **Red**: Error messages
- **Blue**: Action menus
- **Magenta**: Footer information
- **White**: General text

## Error Handling

The application includes error handling for:
- Invalid database connections
- Wrong credentials
- Invalid order IDs
- Invalid meal IDs
- General exceptions during operations


## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Contact

For questions or suggestions, please open an issue in the repository.

---

**Security Notes**: 
- Always keep your `.env` file secure and never commit it to version control
- Add `.env` to your `.gitignore` file
- Use strong passwords for database and admin access
- Consider implementing password hashing for production use