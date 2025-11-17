import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QMessageBox, QSpinBox, QListWidgetItem, QDialog, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
import sqlite3
import datetime
import os

def initialize_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Create articles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    
    # Insert sample data if table is empty
    cursor.execute('SELECT COUNT(*) FROM articles')
    if cursor.fetchone()[0] == 0:
        sample_articles = [
            ('Apple', 0.50, 100),
            ('Banana', 0.30, 150),
            ('Orange', 0.80, 80),
            ('Milk', 1.20, 50),
            ('Bread', 1.00, 60),
        ]
        cursor.executemany('INSERT INTO articles (name, price, stock) VALUES (?, ?, ?)', sample_articles)
    
    conn.commit()
    conn.close()

class ReceiptWindow(QDialog):
    def __init__(self, receipt_content):
        super().__init__()
        self.setWindowTitle('Receipt')
        self.setGeometry(150, 150, 500, 600)
        self.receipt_content = receipt_content
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Receipt Text
        self.receipt_text = QTextEdit()
        self.receipt_text.setReadOnly(True)
        self.receipt_text.setText(self.receipt_content)
        self.receipt_text.setFont(QtGui.QFont("Courier", 10))
        
        # Buttons Layout
        buttons_layout = QHBoxLayout()
        
        # Print Button
        print_btn = QPushButton('Print')
        print_btn.setFixedHeight(40)
        print_btn.setStyleSheet("background-color: #2196F3; color: white; font-size: 14px;")
        print_btn.clicked.connect(self.print_receipt)
        
        # Close Button
        close_btn = QPushButton('Close')
        close_btn.setFixedHeight(40)
        close_btn.setStyleSheet("background-color: #f44336; color: white; font-size: 14px;")
        close_btn.clicked.connect(self.close)
        
        buttons_layout.addWidget(print_btn)
        buttons_layout.addWidget(close_btn)
        
        layout.addWidget(self.receipt_text)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def print_receipt(self):
        try:
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)
            if dialog.exec_() == QPrintDialog.Accepted:
                self.receipt_text.print_(printer)
                QMessageBox.information(self, 'Print Successful', 'Receipt has been sent to the printer.')
        except Exception as e:
            QMessageBox.critical(self, 'Print Error', f"An error occurred while printing:\n{str(e)}")

class CashDeskApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cash Desk App')
        self.setGeometry(100, 100, 1000, 600)
        self.cart = []
        self.discount = 0
        self.init_ui()
        self.load_articles()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Left side: Search and Articles
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search articles...')
        self.search_input.setFixedHeight(30)
        self.search_button = QPushButton('Search')
        self.search_button.setFixedHeight(30)
        self.search_button.clicked.connect(self.search_articles)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        left_layout.addLayout(search_layout)

        # Articles List
        self.articles_list = QListWidget()
        self.articles_list.setStyleSheet("QListWidget { font-size: 16px; }")
        left_layout.addWidget(self.articles_list)

        # Quantity Selection and Add to Cart
        add_layout = QHBoxLayout()
        qty_label = QLabel('Quantity:')
        self.qty_spinbox = QSpinBox()
        self.qty_spinbox.setMinimum(1)
        self.qty_spinbox.setMaximum(100)
        self.qty_spinbox.setValue(1)
        add_to_cart_btn = QPushButton('Add to Cart')
        add_to_cart_btn.setFixedHeight(30)
        add_to_cart_btn.clicked.connect(self.add_to_cart)
        add_layout.addWidget(qty_label)
        add_layout.addWidget(self.qty_spinbox)
        add_layout.addWidget(add_to_cart_btn)
        left_layout.addLayout(add_layout)

        # Refresh Button
        refresh_btn = QPushButton('Refresh Articles')
        refresh_btn.setFixedHeight(30)
        refresh_btn.setStyleSheet("background-color: #FF9800; color: white;")
        refresh_btn.clicked.connect(self.load_articles)
        left_layout.addWidget(refresh_btn)

        # Right side: Cart and Payment
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        # Cart Label
        cart_label = QLabel('Cart')
        cart_label.setAlignment(Qt.AlignCenter)
        cart_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        right_layout.addWidget(cart_label)

        # Cart List
        self.cart_list = QListWidget()
        self.cart_list.setStyleSheet("QListWidget { font-size: 16px; }")
        right_layout.addWidget(self.cart_list)

        # Total Display
        total_layout = QVBoxLayout()
        self.total_label = QLabel('Total: $0.00')
        self.total_label.setStyleSheet("font-size: 16px;")
        self.discount_label = QLabel('Discount (%): 0')
        self.discount_label.setStyleSheet("font-size: 16px;")
        self.final_total_label = QLabel('Final Total: $0.00')
        self.final_total_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        total_layout.addWidget(self.total_label)
        total_layout.addWidget(self.discount_label)
        total_layout.addWidget(self.final_total_label)
        right_layout.addLayout(total_layout)

        # Discount Input
        discount_layout = QHBoxLayout()
        discount_label = QLabel('Apply Discount (%):')
        discount_label.setFixedWidth(150)
        self.discount_input = QLineEdit('0')
        self.discount_input.setFixedHeight(30)
        self.discount_input.setFixedWidth(50)
        self.discount_input.setValidator(QtGui.QDoubleValidator(0.0, 100.0, 2))
        self.discount_input.textChanged.connect(self.update_totals)
        discount_layout.addWidget(discount_label)
        discount_layout.addWidget(self.discount_input)
        discount_layout.addStretch()
        right_layout.addLayout(discount_layout)

        # Payment Button
        payment_btn = QPushButton('Process Payment')
        payment_btn.setFixedHeight(40)
        payment_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px;")
        payment_btn.clicked.connect(self.process_payment)
        right_layout.addWidget(payment_btn)

        # Add layouts to main layout
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)

        self.setLayout(main_layout)

    def load_articles(self):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, price, stock FROM articles')
        articles = cursor.fetchall()
        self.articles = articles  # Update the current articles
        self.display_articles(articles)
        conn.close()

    def display_articles(self, articles):
        self.articles_list.clear()
        for article in articles:
            item_text = f"{article[1]} - ${article[2]:.2f} (Stock: {article[3]})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, article)  # Store the entire article tuple
            self.articles_list.addItem(item)

    def search_articles(self):
        query = self.search_input.text().strip()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, stock FROM articles WHERE name LIKE ?", ('%' + query + '%',))
        results = cursor.fetchall()
        self.display_articles(results)
        conn.close()

    def add_to_cart(self):
        selected_item = self.articles_list.currentItem()
        if selected_item:
            article = selected_item.data(Qt.UserRole)
            quantity = self.qty_spinbox.value()
            if article[3] >= quantity:
                # Check if article is already in cart
                for idx, cart_item in enumerate(self.cart):
                    if cart_item['id'] == article[0]:
                        self.cart[idx]['quantity'] += quantity
                        break
                else:
                    self.cart.append({
                        'id': article[0],
                        'name': article[1],
                        'price': article[2],
                        'quantity': quantity
                    })
                self.refresh_cart()
                # Update stock in real-time
                self.update_stock(article[0], article[3] - quantity)
            else:
                QMessageBox.warning(self, 'Out of Stock', f"Only {article[3]} units of {article[1]} are available.")

    def update_stock(self, article_id, new_stock):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE articles SET stock = ? WHERE id = ?", (new_stock, article_id))
        conn.commit()
        conn.close()
        self.load_articles()

    def refresh_cart(self):
        self.cart_list.clear()
        for item in self.cart:
            self.cart_list.addItem(f"{item['name']} x{item['quantity']} - ${item['price'] * item['quantity']:.2f}")
        self.update_totals()

    def update_totals(self):
        total = sum(item['price'] * item['quantity'] for item in self.cart)
        self.total_label.setText(f"Total: ${total:.2f}")

        try:
            self.discount = float(self.discount_input.text())
            if not (0 <= self.discount <= 100):
                raise ValueError
        except ValueError:
            self.discount = 0
            self.discount_input.setText('0')

        self.discount_label.setText(f"Discount (%): {self.discount}")
        discount_amount = total * (self.discount / 100)
        final_total = total - discount_amount
        self.final_total_label.setText(f"Final Total: ${final_total:.2f}")

    def process_payment(self):
        if not self.cart:
            QMessageBox.warning(self, 'Empty Cart', 'Add items to the cart before payment.')
            return
        total = sum(item['price'] * item['quantity'] for item in self.cart)
        discount_amount = total * (self.discount / 100)
        final_total = total - discount_amount

        # Simulate payment process
        reply = QMessageBox.question(
            self,
            'Confirm Payment',
            f"Total: ${total:.2f}\nDiscount: ${discount_amount:.2f}\nFinal Total: ${final_total:.2f}\n\nProceed with payment?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            # Here you can integrate actual payment processing
            QMessageBox.information(
                self,
                'Payment Successful',
                f"Payment of ${final_total:.2f} was successful!"
            )
            receipt_content = self.generate_receipt(total, discount_amount, final_total)
            self.print_receipt(receipt_content)
            self.show_receipt(receipt_content)
            self.cart.clear()
            self.cart_list.clear()
            self.update_totals()

    def generate_receipt(self, total, discount, final_total):
        receipt_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        receipt_lines = [
            "----- Receipt -----",
            f"Date: {receipt_time}",
            "",
            "Items:",
        ]
        for item in self.cart:
            line = f"{item['name']} x{item['quantity']} @ ${item['price']:.2f} each: ${item['price'] * item['quantity']:.2f}"
            receipt_lines.append(line)
        receipt_lines += [
            "",
            f"Total: ${total:.2f}",
            f"Discount: ${discount:.2f}",
            f"Final Total: ${final_total:.2f}",
            "-------------------"
        ]
        receipt_content = "\n".join(receipt_lines)
        return receipt_content

    def print_receipt(self, receipt_content):
        try:
            if not os.path.exists('receipts'):
                os.makedirs('receipts')
            receipt_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            receipt_path = f"receipts/receipt_{receipt_time}.txt"
            with open(receipt_path, 'w') as f:
                f.write(receipt_content)
            # Optionally, implement actual printing here
            # QMessageBox.information(self, 'Receipt Saved', f"Receipt saved to {receipt_path}")
        except Exception as e:
            QMessageBox.critical(self, 'Error', f"Failed to save receipt:\n{str(e)}")

    def show_receipt(self, receipt_content):
        receipt_window = ReceiptWindow(receipt_content)
        receipt_window.exec_()

if __name__ == '__main__':
    initialize_database()
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Set a modern style
    window = CashDeskApp()
    window.show()
    sys.exit(app.exec_())