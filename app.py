import sys
import os
import sqlite3
import datetime
import base64
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QMessageBox, QSpinBox, QListWidgetItem, QDialog,
    QTextEdit, QTabWidget, QTableWidget, QTableWidgetItem, QFileDialog,
    QRadioButton, QButtonGroup, QFormLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtGui
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import PdfPages

# Ensure images and receipts directories exist
if not os.path.exists('images'):
    os.makedirs('images')

if not os.path.exists('receipts'):
    os.makedirs('receipts')

def initialize_database():
    conn = sqlite3.connect('stock_management.db')
    cursor = conn.cursor()
    
    # Create articles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            photo TEXT
        )
    ''')
    
    # Create sales table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            total REAL NOT NULL,
            discount REAL NOT NULL,
            final_total REAL NOT NULL,
            payment_type TEXT NOT NULL  -- New Column Added
        )
    ''')
    
    # Create sales_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_items (
            sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            article_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
            FOREIGN KEY (article_id) REFERENCES articles(id)
        )
    ''')
    
    # Insert sample data if articles table is empty
    cursor.execute('SELECT COUNT(*) FROM articles')
    if cursor.fetchone()[0] == 0:
        sample_articles = [
            ('Apple', 0.50, 100, None),
            ('Banana', 0.30, 150, None),
            ('Orange', 0.80, 80, None),
            ('Milk', 1.20, 50, None),
            ('Bread', 1.00, 60, None),
        ]
        cursor.executemany('INSERT INTO articles (name, price, stock, photo) VALUES (?, ?, ?, ?)', sample_articles)
    
    conn.commit()
    conn.close()

def encode_image_to_base64(image_path):
    if not os.path.exists(image_path):
        return ''
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

class ReceiptWindow(QDialog):
    def __init__(self, receipt_content):
        super().__init__()
        self.setWindowTitle('Receipt')
        self.setGeometry(150, 150, 500, 700)
        self.receipt_content = receipt_content
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Receipt Display using QTextEdit
        self.receipt_text = QTextEdit()
        self.receipt_text.setReadOnly(True)
        self.receipt_text.setHtml(self.receipt_content)  # Use setHtml instead of setText
        self.receipt_text.setFont(QtGui.QFont("Courier", 10))
        layout.addWidget(self.receipt_text)
        
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

class AnalyticsCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
    
    def plot_sales_over_time(self, data):
        self.axes.clear()
        if data.empty:
            self.axes.text(0.5, 0.5, 'No sales data available.', horizontalalignment='center', verticalalignment='center', transform=self.axes.transAxes)
        else:
            data_sorted = data.sort_values('date')
            self.axes.plot(data_sorted['date'], data_sorted['final_total'], marker='o', linestyle='-')
            self.axes.set_title('Total Sales Over Time')
            self.axes.set_xlabel('Date')
            self.axes.set_ylabel('Final Total ($)')
            self.axes.tick_params(axis='x', rotation=45)
        self.fig.tight_layout()
        self.draw()
    
    def plot_top_selling_items(self, data):
        self.axes.clear()
        if data.empty:
            self.axes.text(0.5, 0.5, 'No top selling items data available.', horizontalalignment='center', verticalalignment='center', transform=self.axes.transAxes)
        else:
            top_items = data.set_index('name')['quantity']
            top_items.plot(kind='bar', ax=self.axes, color='skyblue')
            self.axes.set_title('Top Selling Items')
            self.axes.set_xlabel('Item')
            self.axes.set_ylabel('Quantity Sold')
            self.axes.tick_params(axis='x', rotation=45)
        self.fig.tight_layout()
        self.draw()
    
    def plot_discount_distribution(self, data):
        self.axes.clear()
        if data.empty:
            self.axes.text(0.5, 0.5, 'No discount data available.', horizontalalignment='center', verticalalignment='center', transform=self.axes.transAxes)
        else:
            data['discount'].plot(kind='hist', bins=20, ax=self.axes, color='salmon')
            self.axes.set_title('Discount Distribution')
            self.axes.set_xlabel('Discount (%)')
            self.axes.set_ylabel('Number of Sales')
        self.fig.tight_layout()
        self.draw()

class HistoryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Table to display sales history
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Sale ID', 'Date', 'Total ($)', 'Discount (%)', 'Final Total ($)', 'Payment Type'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        # QLabel to display the total of all sellings
        self.total_label = QLabel('Total of All Sellings: $0.00')
        self.total_label.setAlignment(Qt.AlignRight)
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.total_label)
        
        # Export Button
        export_btn = QPushButton('Export History as CSV')
        export_btn.setFixedHeight(40)
        export_btn.setStyleSheet("background-color: #3F51B5; color: white; font-size: 14px;")
        export_btn.clicked.connect(self.export_history_csv)
        layout.addWidget(export_btn)
        
        self.setLayout(layout)
        self.load_history()
    
    def load_history(self):
        conn = sqlite3.connect('stock_management.db')
        cursor = conn.cursor()
        cursor.execute('SELECT sale_id, date, total, discount, final_total, payment_type FROM sales ORDER BY date DESC')
        sales = cursor.fetchall()
        conn.close()
        
        self.table.setRowCount(len(sales))
        total_sellings = 0  # Initialize total
        
        for row_idx, sale in enumerate(sales):
            for col_idx, item in enumerate(sale):
                table_item = QTableWidgetItem(str(item))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, table_item)
            # Accumulate the final_total for each sale
            try:
                final_total = float(sale[4])  # sale[4] corresponds to 'final_total'
                total_sellings += final_total
            except (ValueError, TypeError):
                # Handle cases where conversion to float fails
                pass
        
        # Update the total_label with the calculated total
        self.total_label.setText(f'Total of All Sellings: ${total_sellings:.2f}')
    
    def export_history_csv(self):
        try:
            conn = sqlite3.connect('stock_management.db')
            query = '''
                SELECT sales.sale_id, sales.date, sales.total, sales.discount, sales.final_total, sales.payment_type,
                       articles.name, sales_items.quantity, sales_items.price
                FROM sales
                JOIN sales_items ON sales.sale_id = sales_items.sale_id
                JOIN articles ON sales_items.article_id = articles.id
                ORDER BY sales.date DESC
            '''
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Save to CSV
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save History as CSV", "", "CSV Files (*.csv)", options=options)
            if file_path:
                df.to_csv(file_path, index=False)
                QMessageBox.information(self, 'Export Successful', f"History exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, 'Export Error', f"An error occurred while exporting history:\n{str(e)}")

class AnalyticsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Analytics Canvas
        self.canvas = AnalyticsCanvas(self, width=8, height=6, dpi=100)
        layout.addWidget(self.canvas)
        
        # Buttons Layout
        buttons_layout = QHBoxLayout()
        
        # Export Button
        export_btn = QPushButton('Export Analytics as PDF')
        export_btn.setFixedHeight(40)
        export_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px;")
        export_btn.clicked.connect(self.export_analytics_pdf)
        buttons_layout.addWidget(export_btn)
        
        # Refresh Button
        refresh_btn = QPushButton('Refresh Analytics')
        refresh_btn.setFixedHeight(40)
        refresh_btn.setStyleSheet("background-color: #FF9800; color: white; font-size: 14px;")
        refresh_btn.clicked.connect(self.load_analytics)
        buttons_layout.addWidget(refresh_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        self.load_analytics()
    
    def load_analytics(self):
        conn = sqlite3.connect('stock_management.db')
        cursor = conn.cursor()
        
        # Total Sales Over Time
        cursor.execute('SELECT date, final_total FROM sales')
        sales_over_time = cursor.fetchall()
        df_sales_time = pd.DataFrame(sales_over_time, columns=['date', 'final_total'])
        df_sales_time['date'] = pd.to_datetime(df_sales_time['date'])
        df_sales_time['final_total'] = pd.to_numeric(df_sales_time['final_total'], errors='coerce')
        print("Sales Over Time DataFrame:")
        print(df_sales_time.head())
        print(df_sales_time.dtypes)
        
        # Top Selling Items
        cursor.execute('''
            SELECT articles.name, SUM(sales_items.quantity) as quantity
            FROM sales_items
            JOIN articles ON sales_items.article_id = articles.id
            GROUP BY articles.name
            ORDER BY quantity DESC
            LIMIT 10
        ''')
        top_selling = cursor.fetchall()
        df_top_selling = pd.DataFrame(top_selling, columns=['name', 'quantity'])
        df_top_selling['quantity'] = pd.to_numeric(df_top_selling['quantity'], errors='coerce')
        print("Top Selling Items DataFrame:")
        print(df_top_selling.head())
        print(df_top_selling.dtypes)
        
        # Discount Distribution
        cursor.execute('SELECT discount FROM sales')
        discounts = cursor.fetchall()
        df_discounts = pd.DataFrame(discounts, columns=['discount'])
        df_discounts['discount'] = pd.to_numeric(df_discounts['discount'], errors='coerce')
        print("Discount Distribution DataFrame:")
        print(df_discounts.head())
        print(df_discounts.dtypes)
        
        conn.close()
        
        # Plotting
        self.canvas.plot_sales_over_time(df_sales_time)
        self.canvas.plot_top_selling_items(df_top_selling)
        self.canvas.plot_discount_distribution(df_discounts)
    
    def export_analytics_pdf(self):
        try:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Analytics as PDF", "", "PDF Files (*.pdf)", options=options)
            if file_path:
                with PdfPages(file_path) as pdf:
                    # Plot Sales Over Time
                    fig1 = Figure(figsize=(8,6))
                    ax1 = fig1.add_subplot(111)
                    conn = sqlite3.connect('stock_management.db')
                    query = 'SELECT date, final_total FROM sales'
                    df = pd.read_sql_query(query, conn)
                    conn.close()
                    df['date'] = pd.to_datetime(df['date'])
                    df_sorted = df.sort_values('date')
                    df_sorted['final_total'] = pd.to_numeric(df_sorted['final_total'], errors='coerce')
                    ax1.plot(df_sorted['date'], df_sorted['final_total'], marker='o', linestyle='-')
                    ax1.set_title('Total Sales Over Time')
                    ax1.set_xlabel('Date')
                    ax1.set_ylabel('Final Total ($)')
                    ax1.tick_params(axis='x', rotation=45)
                    fig1.tight_layout()
                    pdf.savefig(fig1)
                    plt.close(fig1)
                    
                    # Plot Top Selling Items
                    fig2 = Figure(figsize=(8,6))
                    ax2 = fig2.add_subplot(111)
                    conn = sqlite3.connect('stock_management.db')
                    query = '''
                        SELECT articles.name, SUM(sales_items.quantity) as quantity
                        FROM sales_items
                        JOIN articles ON sales_items.article_id = articles.id
                        GROUP BY articles.name
                        ORDER BY quantity DESC
                        LIMIT 10
                    '''
                    df_top = pd.read_sql_query(query, conn)
                    conn.close()
                    df_top['quantity'] = pd.to_numeric(df_top['quantity'], errors='coerce')
                    if df_top.empty:
                        ax2.text(0.5, 0.5, 'No top selling items data available.', horizontalalignment='center', verticalalignment='center', transform=ax2.transAxes)
                    else:
                        top_items = df_top.set_index('name')['quantity']
                        top_items.plot(kind='bar', ax=ax2, color='skyblue')
                        ax2.set_title('Top Selling Items')
                        ax2.set_xlabel('Item')
                        ax2.set_ylabel('Quantity Sold')
                        ax2.tick_params(axis='x', rotation=45)
                    fig2.tight_layout()
                    pdf.savefig(fig2)
                    plt.close(fig2)
                    
                    # Plot Discount Distribution
                    fig3 = Figure(figsize=(8,6))
                    ax3 = fig3.add_subplot(111)
                    conn = sqlite3.connect('stock_management.db')
                    query = 'SELECT discount FROM sales'
                    df_discount = pd.read_sql_query(query, conn)
                    conn.close()
                    df_discount['discount'] = pd.to_numeric(df_discount['discount'], errors='coerce')
                    if df_discount.empty:
                        ax3.text(0.5, 0.5, 'No discount data available.', horizontalalignment='center', verticalalignment='center', transform=ax3.transAxes)
                    else:
                        df_discount['discount'].plot(kind='hist', bins=20, ax=ax3, color='salmon')
                        ax3.set_title('Discount Distribution')
                        ax3.set_xlabel('Discount (%)')
                        ax3.set_ylabel('Number of Sales')
                    fig3.tight_layout()
                    pdf.savefig(fig3)
                    plt.close(fig3)
                
                QMessageBox.information(self, 'Export Successful', f"Analytics exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, 'Export Error', f"An error occurred while exporting analytics:\n{str(e)}")

class ArticleManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Form to Add/Modify Articles
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        form_layout.addRow('Name:', self.name_input)
        
        self.price_input = QLineEdit()
        self.price_input.setValidator(QtGui.QDoubleValidator(0.0, 10000.0, 2))
        form_layout.addRow('Price ($):', self.price_input)
        
        self.stock_input = QSpinBox()
        self.stock_input.setMinimum(0)
        self.stock_input.setMaximum(1000000)
        form_layout.addRow('Stock:', self.stock_input)
        
        self.photo_path = ''
        self.photo_label = QLabel('No Photo Selected')
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setStyleSheet("border: 1px solid gray;")
        form_layout.addRow('Photo:', self.photo_label)
        
        self.upload_btn = QPushButton('Upload Photo')
        self.upload_btn.clicked.connect(self.upload_photo)
        form_layout.addRow('', self.upload_btn)
        
        layout.addLayout(form_layout)
        
        # Buttons for Add, Edit, Delete
        buttons_layout = QHBoxLayout()
        
        self.add_btn = QPushButton('Add Article')
        self.add_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.add_btn.clicked.connect(self.add_article)
        buttons_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton('Edit Article')
        self.edit_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.edit_btn.clicked.connect(self.edit_article)
        buttons_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton('Delete Article')
        self.delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.delete_btn.clicked.connect(self.delete_article)
        buttons_layout.addWidget(self.delete_btn)
        
        layout.addLayout(buttons_layout)
        
        # Table to Display Articles
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Price ($)', 'Stock', 'Photo'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellClicked.connect(self.load_article_details)
        layout.addWidget(self.table)
        
        # Export Button
        export_btn = QPushButton('Export Articles as CSV')
        export_btn.setFixedHeight(40)
        export_btn.setStyleSheet("background-color: #3F51B5; color: white; font-size: 14px;")
        export_btn.clicked.connect(self.export_articles_csv)
        layout.addWidget(export_btn)
        
        self.setLayout(layout)
        self.load_articles()
    
    def upload_photo(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Article Photo", "", "Image Files (*.png *.jpg *.jpeg)", options=options)
        if file_path:
            self.photo_path = file_path
            # Display the photo in the label
            pixmap = QtGui.QPixmap(file_path)
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_label.setPixmap(pixmap)
    
    def add_article(self):
        name = self.name_input.text().strip()
        price = self.price_input.text().strip()
        stock = self.stock_input.value()
        photo = self.photo_path
        
        if not name or not price:
            QMessageBox.warning(self, 'Input Error', 'Please provide both name and price for the article.')
            return
        
        try:
            price = float(price)
        except ValueError:
            QMessageBox.warning(self, 'Input Error', 'Please enter a valid price.')
            return
        
        # Handle photo
        if photo:
            # Copy the photo to the images directory
            photo_filename = os.path.basename(photo)
            destination = os.path.join('images', photo_filename)
            try:
                if not os.path.exists(destination):
                    os.rename(photo, destination)
            except Exception as e:
                QMessageBox.critical(self, 'Photo Error', f"Failed to upload photo:\n{str(e)}")
                return
        else:
            destination = None
        
        # Insert into database
        try:
            conn = sqlite3.connect('stock_management.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO articles (name, price, stock, photo)
                VALUES (?, ?, ?, ?)
            ''', (name, price, stock, destination))
            conn.commit()
            conn.close()
            QMessageBox.information(self, 'Success', 'Article added successfully.')
            self.clear_form()
            self.load_articles()
        except Exception as e:
            QMessageBox.critical(self, 'Database Error', f"An error occurred while adding the article:\n{str(e)}")
    
    def load_articles(self):
        conn = sqlite3.connect('stock_management.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, price, stock, photo FROM articles')
        articles = cursor.fetchall()
        conn.close()
        
        self.table.setRowCount(len(articles))
        for row_idx, article in enumerate(articles):
            for col_idx, item in enumerate(article):
                if col_idx == 4 and item:
                    # Display photo as text (file path)
                    table_item = QTableWidgetItem(os.path.basename(item))
                else:
                    table_item = QTableWidgetItem(str(item))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, table_item)
    
    def load_article_details(self, row, column):
        conn = sqlite3.connect('stock_management.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, price, stock, photo FROM articles WHERE id = ?', (self.table.item(row, 0).text(),))
        article = cursor.fetchone()
        conn.close()
        
        if article:
            self.name_input.setText(article[1])
            self.price_input.setText(str(article[2]))
            self.stock_input.setValue(article[3])
            photo = article[4]
            if photo and os.path.exists(photo):
                pixmap = QtGui.QPixmap(photo)
                pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.photo_label.setPixmap(pixmap)
                self.photo_path = photo
            else:
                self.photo_label.setText('No Photo Selected')
                self.photo_path = ''
    
    def edit_article(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Selection Error', 'Please select an article to edit.')
            return
        
        article_id = selected_items[0].text()
        name = self.name_input.text().strip()
        price = self.price_input.text().strip()
        stock = self.stock_input.value()
        photo = self.photo_path
        
        if not name or not price:
            QMessageBox.warning(self, 'Input Error', 'Please provide both name and price for the article.')
            return
        
        try:
            price = float(price)
        except ValueError:
            QMessageBox.warning(self, 'Input Error', 'Please enter a valid price.')
            return
        
        # Handle photo
        if photo:
            # Copy the photo to the images directory if it's a new photo
            if not photo.startswith(os.path.abspath('images')):
                photo_filename = os.path.basename(photo)
                destination = os.path.join('images', photo_filename)
                try:
                    if not os.path.exists(destination):
                        os.rename(photo, destination)
                except Exception as e:
                    QMessageBox.critical(self, 'Photo Error', f"Failed to upload photo:\n{str(e)}")
                    return
            else:
                destination = photo
        else:
            destination = None
        
        # Update database
        try:
            conn = sqlite3.connect('stock_management.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE articles
                SET name = ?, price = ?, stock = ?, photo = ?
                WHERE id = ?
            ''', (name, price, stock, destination, article_id))
            conn.commit()
            conn.close()
            QMessageBox.information(self, 'Success', 'Article updated successfully.')
            self.clear_form()
            self.load_articles()
        except Exception as e:
            QMessageBox.critical(self, 'Database Error', f"An error occurred while updating the article:\n{str(e)}")
    
    def delete_article(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Selection Error', 'Please select an article to delete.')
            return
        
        article_id = selected_items[0].text()
        reply = QMessageBox.question(
            self,
            'Confirm Deletion',
            f"Are you sure you want to delete the article with ID {article_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Get photo path to delete the image file
                conn = sqlite3.connect('stock_management.db')
                cursor = conn.cursor()
                cursor.execute('SELECT photo FROM articles WHERE id = ?', (article_id,))
                result = cursor.fetchone()
                photo = result[0] if result else None
                cursor.execute('DELETE FROM articles WHERE id = ?', (article_id,))
                conn.commit()
                conn.close()
                
                # Delete the photo file if it exists
                if photo and os.path.exists(photo):
                    os.remove(photo)
                
                QMessageBox.information(self, 'Success', 'Article deleted successfully.')
                self.clear_form()
                self.load_articles()
            except Exception as e:
                QMessageBox.critical(self, 'Database Error', f"An error occurred while deleting the article:\n{str(e)}")
    
    def clear_form(self):
        self.name_input.clear()
        self.price_input.clear()
        self.stock_input.setValue(0)
        self.photo_label.setText('No Photo Selected')
        self.photo_path = ''
    
    def export_articles_csv(self):
        try:
            conn = sqlite3.connect('stock_management.db')
            query = 'SELECT id, name, price, stock, photo FROM articles'
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Save to CSV
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Articles as CSV", "", "CSV Files (*.csv)", options=options)
            if file_path:
                df.to_csv(file_path, index=False)
                QMessageBox.information(self, 'Export Successful', f"Articles exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, 'Export Error', f"An error occurred while exporting articles:\n{str(e)}")

class AnalyticsCanvasEnhanced(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
    
    def plot_sales_over_time(self, data):
        self.axes.clear()
        if data.empty:
            self.axes.text(0.5, 0.5, 'No sales data available.', horizontalalignment='center', verticalalignment='center', transform=self.axes.transAxes)
        else:
            data_sorted = data.sort_values('date')
            self.axes.plot(data_sorted['date'], data_sorted['final_total'], marker='o', linestyle='-')
            self.axes.set_title('Total Sales Over Time')
            self.axes.set_xlabel('Date')
            self.axes.set_ylabel('Final Total ($)')
            self.axes.tick_params(axis='x', rotation=45)
        self.fig.tight_layout()
        self.draw()
    
    def plot_top_selling_items(self, data):
        self.axes.clear()
        if data.empty:
            self.axes.text(0.5, 0.5, 'No top selling items data available.', horizontalalignment='center', verticalalignment='center', transform=self.axes.transAxes)
        else:
            top_items = data.set_index('name')['quantity']
            top_items.plot(kind='bar', ax=self.axes, color='skyblue')
            self.axes.set_title('Top Selling Items')
            self.axes.set_xlabel('Item')
            self.axes.set_ylabel('Quantity Sold')
            self.axes.tick_params(axis='x', rotation=45)
        self.fig.tight_layout()
        self.draw()
    
    def plot_discount_distribution(self, data):
        self.axes.clear()
        if data.empty:
            self.axes.text(0.5, 0.5, 'No discount data available.', horizontalalignment='center', verticalalignment='center', transform=self.axes.transAxes)
        else:
            data['discount'].plot(kind='hist', bins=20, ax=self.axes, color='salmon')
            self.axes.set_title('Discount Distribution')
            self.axes.set_xlabel('Discount (%)')
            self.axes.set_ylabel('Number of Sales')
        self.fig.tight_layout()
        self.draw()

class AnalyticsTabEnhanced(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Enhanced Analytics Canvas
        self.canvas = AnalyticsCanvasEnhanced(self, width=8, height=6, dpi=100)
        layout.addWidget(self.canvas)
        
        # Buttons Layout
        buttons_layout = QHBoxLayout()
        
        # Export Button
        export_btn = QPushButton('Export Analytics as PDF')
        export_btn.setFixedHeight(40)
        export_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px;")
        export_btn.clicked.connect(self.export_analytics_pdf)
        buttons_layout.addWidget(export_btn)
        
        # Refresh Button
        refresh_btn = QPushButton('Refresh Analytics')
        refresh_btn.setFixedHeight(40)
        refresh_btn.setStyleSheet("background-color: #FF9800; color: white; font-size: 14px;")
        refresh_btn.clicked.connect(self.load_analytics)
        buttons_layout.addWidget(refresh_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        self.load_analytics()
    
    def load_analytics(self):
        conn = sqlite3.connect('stock_management.db')
        cursor = conn.cursor()
        
        # Total Sales Over Time
        cursor.execute('SELECT date, final_total FROM sales')
        sales_over_time = cursor.fetchall()
        df_sales_time = pd.DataFrame(sales_over_time, columns=['date', 'final_total'])
        df_sales_time['date'] = pd.to_datetime(df_sales_time['date'])
        df_sales_time['final_total'] = pd.to_numeric(df_sales_time['final_total'], errors='coerce')
        print("Sales Over Time DataFrame:")
        print(df_sales_time.head())
        print(df_sales_time.dtypes)
        
        # Top Selling Items
        cursor.execute('''
            SELECT articles.name, SUM(sales_items.quantity) as quantity
            FROM sales_items
            JOIN articles ON sales_items.article_id = articles.id
            GROUP BY articles.name
            ORDER BY quantity DESC
            LIMIT 10
        ''')
        top_selling = cursor.fetchall()
        df_top_selling = pd.DataFrame(top_selling, columns=['name', 'quantity'])
        df_top_selling['quantity'] = pd.to_numeric(df_top_selling['quantity'], errors='coerce')
        print("Top Selling Items DataFrame:")
        print(df_top_selling.head())
        print(df_top_selling.dtypes)
        
        # Discount Distribution
        cursor.execute('SELECT discount FROM sales')
        discounts = cursor.fetchall()
        df_discounts = pd.DataFrame(discounts, columns=['discount'])
        df_discounts['discount'] = pd.to_numeric(df_discounts['discount'], errors='coerce')
        print("Discount Distribution DataFrame:")
        print(df_discounts.head())
        print(df_discounts.dtypes)
        
        conn.close()
        
        # Plotting
        self.canvas.plot_sales_over_time(df_sales_time)
        self.canvas.plot_top_selling_items(df_top_selling)
        self.canvas.plot_discount_distribution(df_discounts)
    
    def export_analytics_pdf(self):
        try:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Analytics as PDF", "", "PDF Files (*.pdf)", options=options)
            if file_path:
                with PdfPages(file_path) as pdf:
                    # Plot Sales Over Time
                    fig1 = Figure(figsize=(8,6))
                    ax1 = fig1.add_subplot(111)
                    conn = sqlite3.connect('stock_management.db')
                    query = 'SELECT date, final_total FROM sales'
                    df = pd.read_sql_query(query, conn)
                    conn.close()
                    df['date'] = pd.to_datetime(df['date'])
                    df_sorted = df.sort_values('date')
                    df_sorted['final_total'] = pd.to_numeric(df_sorted['final_total'], errors='coerce')
                    ax1.plot(df_sorted['date'], df_sorted['final_total'], marker='o', linestyle='-')
                    ax1.set_title('Total Sales Over Time')
                    ax1.set_xlabel('Date')
                    ax1.set_ylabel('Final Total ($)')
                    ax1.tick_params(axis='x', rotation=45)
                    fig1.tight_layout()
                    pdf.savefig(fig1)
                    plt.close(fig1)
                    
                    # Plot Top Selling Items
                    fig2 = Figure(figsize=(8,6))
                    ax2 = fig2.add_subplot(111)
                    conn = sqlite3.connect('stock_management.db')
                    query = '''
                        SELECT articles.name, SUM(sales_items.quantity) as quantity
                        FROM sales_items
                        JOIN articles ON sales_items.article_id = articles.id
                        GROUP BY articles.name
                        ORDER BY quantity DESC
                        LIMIT 10
                    '''
                    df_top = pd.read_sql_query(query, conn)
                    conn.close()
                    df_top['quantity'] = pd.to_numeric(df_top['quantity'], errors='coerce')
                    if df_top.empty:
                        ax2.text(0.5, 0.5, 'No top selling items data available.', horizontalalignment='center', verticalalignment='center', transform=ax2.transAxes)
                    else:
                        top_items = df_top.set_index('name')['quantity']
                        top_items.plot(kind='bar', ax=ax2, color='skyblue')
                        ax2.set_title('Top Selling Items')
                        ax2.set_xlabel('Item')
                        ax2.set_ylabel('Quantity Sold')
                        ax2.tick_params(axis='x', rotation=45)
                    fig2.tight_layout()
                    pdf.savefig(fig2)
                    plt.close(fig2)
                    
                    # Plot Discount Distribution
                    fig3 = Figure(figsize=(8,6))
                    ax3 = fig3.add_subplot(111)
                    conn = sqlite3.connect('stock_management.db')
                    query = 'SELECT discount FROM sales'
                    df_discount = pd.read_sql_query(query, conn)
                    conn.close()
                    df_discount['discount'] = pd.to_numeric(df_discount['discount'], errors='coerce')
                    if df_discount.empty:
                        ax3.text(0.5, 0.5, 'No discount data available.', horizontalalignment='center', verticalalignment='center', transform=ax3.transAxes)
                    else:
                        df_discount['discount'].plot(kind='hist', bins=20, ax=ax3, color='salmon')
                        ax3.set_title('Discount Distribution')
                        ax3.set_xlabel('Discount (%)')
                        ax3.set_ylabel('Number of Sales')
                    fig3.tight_layout()
                    pdf.savefig(fig3)
                    plt.close(fig3)
                
                QMessageBox.information(self, 'Export Successful', f"Analytics exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, 'Export Error', f"An error occurred while exporting analytics:\n{str(e)}")

class StockManagementApp(QWidget):
    sale_processed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Stock Management System')
        self.setGeometry(100, 100, 1300, 800)
        self.init_ui()
        self.load_articles()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tabs
        self.tabs = QTabWidget()
        self.tab_article_management = ArticleManagementTab()
        self.tab_sales_history = HistoryTab()
        self.tab_analytics = AnalyticsTabEnhanced()
        
        self.tabs.addTab(self.tab_article_management, "Article Management")
        self.tabs.addTab(self.tab_sales_history, "Sales History")
        self.tabs.addTab(self.tab_analytics, "Analytics Dashboard")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
    
    def load_articles(self):
        self.tab_article_management.load_articles()

class CashDeskApp(QWidget):
    sale_processed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cash Desk App')
        self.setGeometry(100, 100, 1200, 700)
        self.cart = []
        self.discount = 0
        self.init_ui()
        self.load_articles()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tabs
        self.tabs = QTabWidget()
        self.tab_main = QWidget()
        self.tab_history = HistoryTab()
        self.tab_analytics = AnalyticsTabEnhanced()
        
        self.tabs.addTab(self.tab_main, "POS")
        self.tabs.addTab(self.tab_history, "History")
        self.tabs.addTab(self.tab_analytics, "Analytics")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        # Initialize Main POS UI
        self.init_main_tab()
    
    def init_main_tab(self):
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
    
        # Payment Type Selection
        payment_type_layout = QHBoxLayout()
        payment_label = QLabel('Payment Type:')
        payment_label.setFixedWidth(100)
        self.cash_radio = QRadioButton('Cash')
        self.card_radio = QRadioButton('Card')
        self.cash_radio.setChecked(True)  # Default selection
        self.payment_group = QButtonGroup()
        self.payment_group.addButton(self.cash_radio)
        self.payment_group.addButton(self.card_radio)
        payment_type_layout.addWidget(payment_label)
        payment_type_layout.addWidget(self.cash_radio)
        payment_type_layout.addWidget(self.card_radio)
        payment_type_layout.addStretch()
        right_layout.addLayout(payment_type_layout)
    
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
    
        self.tab_main.setLayout(main_layout)
    
    def load_articles(self):
        conn = sqlite3.connect('stock_management.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, price, stock, photo FROM articles')
        articles = cursor.fetchall()
        conn.close()
        
        self.articles = articles  # Update the current articles
        self.display_articles(articles)
    
    def display_articles(self, articles):
        self.articles_list.clear()
        for article in articles:
            item_text = f"{article[1]} - ${article[2]:.2f} (Stock: {article[3]})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, article)  # Store the entire article tuple
            self.articles_list.addItem(item)
    
    def search_articles(self):
        query = self.search_input.text().strip()
        conn = sqlite3.connect('stock_management.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, stock, photo FROM articles WHERE name LIKE ?", ('%' + query + '%',))
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
        conn = sqlite3.connect('stock_management.db')
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
    
        # Get selected payment type
        if self.cash_radio.isChecked():
            payment_type = 'Cash'
        else:
            payment_type = 'Card'
    
        # Simulate payment process
        reply = QMessageBox.question(
            self,
            'Confirm Payment',
            f"Total: ${total:.2f}\nDiscount: ${discount_amount:.2f}\nFinal Total: ${final_total:.2f}\nPayment Type: {payment_type}\n\nProceed with payment?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
    
        if reply == QMessageBox.Yes:
            # Record the sale in the database
            try:
                conn = sqlite3.connect('stock_management.db')
                cursor = conn.cursor()
                sale_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('''
                    INSERT INTO sales (date, total, discount, final_total, payment_type)
                    VALUES (?, ?, ?, ?, ?)
                ''', (sale_date, total, self.discount, final_total, payment_type))
                sale_id = cursor.lastrowid
                
                # Insert sale items
                for item in self.cart:
                    cursor.execute('''
                        INSERT INTO sales_items (sale_id, article_id, quantity, price)
                        VALUES (?, ?, ?, ?)
                    ''', (sale_id, item['id'], item['quantity'], item['price']))
                
                conn.commit()
                conn.close()
            except Exception as e:
                QMessageBox.critical(self, 'Database Error', f"An error occurred while recording the sale:\n{str(e)}")
                return
    
            # Simulate payment confirmation
            QMessageBox.information(
                self,
                'Payment Successful',
                f"Payment of ${final_total:.2f} was successful!"
            )
            receipt_content = self.generate_receipt(sale_id, total, discount_amount, final_total, payment_type)
            self.print_receipt(receipt_content)
            self.show_receipt(receipt_content)
            self.cart.clear()
            self.cart_list.clear()
            self.update_totals()
    
            # Refresh the History Tab
            self.tabs.widget(1).load_history()  # Assuming HistoryTab is at index 1
    
    def generate_receipt(self, sale_id, total, discount, final_total, payment_type):
        sale_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Path to the logo image
        logo_path = os.path.join('images', 'logo.png')  # Ensure this path is correct
        
        # Encode the logo image to Base64
        logo_base64 = encode_image_to_base64(logo_path)
        
        # Start building the HTML receipt
        html_receipt = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Courier, monospace;
                    width: 400px;
                }}
                .header {{
                    text-align: center;
                }}
                .header img {{
                    max-width: 150px;
                    height: auto;
                }}
                .company-details {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .items {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                .items th, .items td {{
                    border: 1px solid #000;
                    padding: 5px;
                    text-align: left;
                }}
                .totals {{
                    margin-top: 20px;
                    width: 100%;
                }}
                .totals td {{
                    padding: 5px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                {"<img src='data:image/png;base64," + logo_base64 + "' />" if logo_base64 else ""}
            </div>
            <div class="company-details">
                <h2>My Retail Company</h2>
                <p>1234 Market Street<br>
                City, State ZIP<br>
                Phone: (123) 456-7890<br>
                Email: info@myretailcompany.com</p>
            </div>
            <hr>
            <p><strong>Sale ID:</strong> {sale_id}<br>
            <strong>Date:</strong> {sale_time}<br>
            <strong>Payment Type:</strong> {payment_type}</p>
            <table class="items">
                <tr>
                    <th>Item</th>
                    <th>Qty</th>
                    <th>Price ($)</th>
                    <th>Total ($)</th>
                </tr>
        """
        
        # Add each cart item to the HTML table
        for item in self.cart:
            item_total = item['price'] * item['quantity']
            html_receipt += f"""
                <tr>
                    <td>{item['name']}</td>
                    <td>{item['quantity']}</td>
                    <td>{item['price']:.2f}</td>
                    <td>{item_total:.2f}</td>
                </tr>
            """
        
        # Add totals and discount
        html_receipt += f"""
            </table>
            <table class="totals">
                <tr>
                    <td><strong>Total:</strong></td>
                    <td>${total:.2f}</td>
                </tr>
                <tr>
                    <td><strong>Discount ({self.discount}%):</strong></td>
                    <td>-${discount:.2f}</td>
                </tr>
                <tr>
                    <td><strong>Final Total:</strong></td>
                    <td>${final_total:.2f}</td>
                </tr>
            </table>
            <div class="footer">
                <p>Thank you for shopping with us!</p>
                <p>Visit again.</p>
            </div>
        </body>
        </html>
        """
        
        return html_receipt
    
    def print_receipt(self, receipt_content):
        try:
            if not os.path.exists('receipts'):
                os.makedirs('receipts')
            receipt_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            receipt_path = f"receipts/receipt_{receipt_time}.html"
            with open(receipt_path, 'w') as f:
                f.write(receipt_content)
            # Optionally, implement actual printing here
            # QMessageBox.information(self, 'Receipt Saved', f"Receipt saved to {receipt_path}")
        except Exception as e:
            QMessageBox.critical(self, 'Error', f"Failed to save receipt:\n{str(e)}")
    
    def show_receipt(self, receipt_content):
        receipt_window = ReceiptWindow(receipt_content)
        receipt_window.exec_()

def main():
    initialize_database()
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Set a modern style
    
    # Create a Tab Widget and add both Stock Management and Cash Desk apps
    main_window = QTabWidget()
    stock_management_app = StockManagementApp()
    cash_desk_app = CashDeskApp()
    
    main_window.addTab(stock_management_app, "Stock Management")
    main_window.addTab(cash_desk_app, "Cash Desk")
    
    main_window.setWindowTitle('Retail Management System')
    main_window.setGeometry(50, 50, 1400, 800)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()