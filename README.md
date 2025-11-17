# Retail Management System

Welcome to the **Retail Management System**, a comprehensive desktop application designed to streamline your retail operations. Built with Python and PyQt5, this system integrates stock management, point-of-sale (POS) functionalities, sales history tracking, and insightful analytics to empower your business with efficient and data-driven decision-making.

<br>
<div align="center">
  <img src="logo.png" width="100">
</div>


## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Stock Management](#stock-management)
  - [Cash Desk (POS)](#cash-desk-pos)
  - [Sales History](#sales-history)
  - [Analytics Dashboard](#analytics-dashboard)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Stock Management:**
  - Add, edit, and delete articles/items with details such as name, price, stock quantity, and photo.
    
  - Upload and manage product images for visual reference.
    
  - Export articles data to CSV for external use or backup.

- **Cash Desk (POS):**
  - Intuitive Point-of-Sale interface for processing sales.
  - Search and add articles to the cart with real-time stock updates.
  - Select payment types (Cash or Card) and apply discounts.
  - Generate detailed receipts with company branding, including logo and contact information.
  - Print or save receipts for record-keeping.

- **Sales History:**
  - Comprehensive view of all sales transactions with details like sale ID, date, total amount, discount, final total, and payment type.
  - Export sales history to CSV for analysis or auditing purposes.

- **Analytics Dashboard:**
  - Visual representations of sales data including:
    - **Total Sales Over Time:** Track revenue trends.
    - **Top Selling Items:** Identify best-performing products.
    - **Discount Distribution:** Analyze the impact of discounts on sales.
  - Export analytics graphs to PDF for reporting.

- **User-Friendly Interface:**
  - Modern and responsive design using PyQt5's Fusion style.
  - Tooltips and intuitive controls for enhanced user experience.
  - Confirmation dialogs to prevent accidental actions.

- **Robust Database Management:**
  - Utilizes SQLite for efficient and reliable data storage.
  - Backup and restore functionalities to safeguard data integrity.

## Screenshots

### Stock Management

![Stock Management](screenshots/stock_management.png)

### Cash Desk (POS)

![Cash Desk](screenshots/cash_desk.png)

### Sales History

![Sales History](screenshots/sales_history.png)

### Analytics Dashboard

![Analytics Dashboard](screenshots/analytics_dashboard.png)

### Receipt Window

![Receipt Window](screenshots/receipt_window.png)

## Getting Started

Follow these instructions to set up and run the Retail Management System on your local machine.

### Prerequisites

- **Python 3.6 or higher**: Ensure Python is installed on your system. You can download it from [here](https://www.python.org/downloads/).

- **pip**: Python package installer. It typically comes bundled with Python.

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/swissmarley/cashier.git
   cd cashier
   ```

2.	**Create a Virtual Environment** (Optional but Recommended)
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.	**Install Required Packages**
    ```bash
    pip install -r requirements.txt
    ````

4.	**Add Company Logo**

	•	Place your logo.png image inside the images/ directory.

	•	Ensure the image is appropriately sized (e.g., 200x200 pixels) for optimal display in receipts.

5.	**Initialize the Database**

    The application automatically initializes the SQLite database (stock_management.db) with necessary tables and sample data upon the first run.


## Usage

Launch the application by running the app.py script:
```bash
python app.py
```

The application window features two main tabs:
	1.	Stock Management
	2.	Cash Desk

### Stock Management

Manage your inventory seamlessly.

	Add Article:
		•	Fill in the article’s name, price, and stock quantity.
		•	Upload a photo for visual reference.
		•	Click “Add Article” to save.
	
	Edit Article:
		•	Select an article from the table.
		•	Modify the desired fields.
		•	Click “Edit Article” to update.
	
	Delete Article:
		•	Select an article from the table.
		•	Click “Delete Article” and confirm the action.
	
	Export Articles:
		•	Click “Export Articles as CSV” to save the current inventory data.

### Cash Desk (POS)

Process sales efficiently with the integrated POS system.

	Search Articles:
		•	Use the search bar to find specific articles by name.
	
	Add to Cart:
		•	Select an article from the list.
		•	Specify the quantity and click “Add to Cart”.
	
	Manage Cart:
		•	View added items in the cart.
		•	Adjust quantities if necessary.
	
	Apply Discounts:
		•	Enter a discount percentage to apply to the total sale.
		
	Select Payment Type:
		•	Choose between “Cash” or “Card” as the payment method.
		
	Process Payment:
		•	Click “Process Payment” to finalize the sale.
		•	A receipt window will appear displaying all sale details.
		•	Choose to print or save the receipt.

### Sales History

Review all past sales transactions.

	View Sales:
		•	Browse through the sales history table with detailed information.
	
	Export History:
		•	Click “Export History as CSV” to download the sales data.

### Analytics Dashboard

Gain insights into your sales performance.

	Total Sales Over Time:
		•	Visualize revenue trends across different dates.
	
	Top Selling Items:
		•	Identify your best-performing products.
	
	Discount Distribution:
		•	Analyze how discounts affect your sales.
	
	Export Analytics:
		•	Click “Export Analytics as PDF” to save the graphical reports.


## Technologies Used
	•	Python 3.6+
	
	•	PyQt5: For building the graphical user interface.
	
	•	SQLite: Lightweight database for data storage.
	
	•	Pandas: Data manipulation and analysis.
	
	•	Matplotlib: Creating visual analytics and charts.

## Contributing

Contributions are welcome! Follow these steps to contribute:

	1.	Fork the Repository
	
	2.	Create a New Branch
	    ```bash
	    git checkout -b feature/YourFeatureName
	    ```
	3.	Make Changes
	4.	Commit Your Changes
	    ```bash
	    git commit -m "Add your message here"
	    ``` 
	
	5.	Push to the Branch
	    ```bash
	    git push origin feature/YourFeatureName
	    ```
	
	6.	Open a Pull Request


## License

This project is licensed under the MIT License.
