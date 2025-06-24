CREATE TABLE customers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  email TEXT,
  city TEXT,
  country TEXT
);

CREATE TABLE products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  category TEXT,
  price REAL
);

CREATE TABLE sales (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER,
  product_id INTEGER,
  employee_id INTEGER,
  quantity INTEGER,
  total_amount REAL,
  sale_date DATE,
  city TEXT,
  FOREIGN KEY (customer_id) REFERENCES customers(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
  FOREIGN KEY (employee_id) REFERENCES employees(id)
);

CREATE TABLE employees (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  region TEXT
);
