import sys
import requests
import uuid
import locale
import datetime
from dateutil import parser
from PyQt6.QtWidgets import QApplication, QHeaderView, QDateEdit, QStyle, QComboBox, QWidget, QVBoxLayout, QPushButton, QTableWidget, QFrame, QTableWidgetItem, QMessageBox, QLineEdit, QLabel, QFormLayout, QHBoxLayout
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor, QBrush, QFont, QIcon

API_URL = "http://127.0.0.1:1323/transaksi"

class TransactionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Transaksi Manager Kummiku")
        self.setGeometry(100, 100, 800, 550)  # Tambah tinggi agar tidak terlalu padat
        self.setWindowIcon(QIcon("icon.ico"))

        layout = QVBoxLayout()

        # 🔥 Tabel Transaksi
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Jenis Transaksi", "Nilai", "Tanggal", "Keterangan", "Pembeli", "Nomor HP", "Alamat"])

        # 🔥 Pengaturan ukuran kolom
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.loat_data = QPushButton("Loat Data")
        self.loat_data.clicked.connect(self.load_transactions)
        self.loat_data.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))

        layout.addWidget(self.loat_data)
        layout.addWidget(self.table)

        # 🔥 Filter Bulan & Tahun
        filter_layout = QHBoxLayout()

        self.month_selector = QComboBox()
        self.month_selector.addItems(["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        self.month_selector.setCurrentIndex(datetime.datetime.now().month - 1)

        self.year_selector = QComboBox()
        current_year = datetime.datetime.now().year
        self.year_selector.addItems([str(year) for year in range(current_year - 5, current_year + 1)])
        self.year_selector.setCurrentText(str(current_year))

        self.load_report_button = QPushButton("Lihat Laporan")
        self.load_report_button.clicked.connect(self.load_transactions)

        filter_layout.addWidget(QLabel("Bulan:"))
        filter_layout.addWidget(self.month_selector)
        filter_layout.addWidget(QLabel("Tahun:"))
        filter_layout.addWidget(self.year_selector)
        filter_layout.addWidget(self.load_report_button)

        layout.addLayout(filter_layout)

        # 🔥 Label Total Income & Outcome
        summary_layout = QHBoxLayout()

        self.income_label = QLabel("Total Pemasukan: Rp. 0")
        self.outcome_label = QLabel("Total Pengeluaran: Rp. 0")
        # Atur warna dan tebal
        self.income_label.setStyleSheet("color: green; font-weight: bold;")
        self.outcome_label.setStyleSheet("color: red; font-weight: bold;")

        # Bisa juga pakai setFont()
        font = QFont()
        font.setBold(True)
        self.income_label.setFont(font)
        self.outcome_label.setFont(font)

        summary_layout.addWidget(self.income_label)
        summary_layout.addWidget(self.outcome_label)

        layout.addLayout(summary_layout)

        # form transaksi
        self.form_title = QLabel("Form Transaksi")
        self.form_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.form_title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")

        # 🔥 Tambahkan Garis Horizontal
        self.top_separator = QFrame()
        self.top_separator.setFrameShape(QFrame.Shape.HLine)
        self.top_separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.bottom_separator = QFrame()
        self.bottom_separator.setFrameShape(QFrame.Shape.HLine)
        self.bottom_separator.setFrameShadow(QFrame.Shadow.Sunken)

        layout.addWidget(self.top_separator)  # Tambahkan Garis Horizontal
        layout.addWidget(self.form_title)      # Tambahkan Judul ke Layout
        layout.addWidget(self.bottom_separator)  # Tambahkan Garis Horizontal
        # 🔥 Form Input
        form_layout = QFormLayout()
        self.type_input = QComboBox()
        self.type_input.addItems(["Pilih","Pemasukan", "Pengeluaran"])
        self.type_input.currentIndexChanged.connect(self.toggle_buyer_fields) # Event untuk hide/show
        self.amount_input = QLineEdit()
        self.amount_input.textChanged.connect(self.validate_amount_input)
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.desc_input = QLineEdit()
        self.buyer_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        
        # 🔥 Buat widget label agar bisa di-hide juga
        self.buyer_label = QLabel("Pembeli:")
        self.phone_label = QLabel("No.HP:")
        self.address_label = QLabel("Alamat:")

        form_layout.addRow("Jenis Transaksi:", self.type_input)
        form_layout.addRow("Nilai:", self.amount_input)
        form_layout.addRow("Tanggal:", self.date_input)
        form_layout.addRow("Keterangan:", self.desc_input)
        form_layout.addRow(self.buyer_label, self.buyer_input)
        form_layout.addRow(self.phone_label, self.phone_input)
        form_layout.addRow(self.address_label, self.address_input)
        layout.addLayout(form_layout)
        
        self.toggle_buyer_fields()

        # 🔥 Tombol CRUD
        button_layout = QHBoxLayout()
        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_transaction)
        self.create_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        button_layout.addWidget(self.create_button)

        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.update_transaction)
        self.update_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DriveFDIcon))
        button_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_transaction)
        self.delete_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogDiscardButton))
        button_layout.addWidget(self.delete_button)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.clear_form)
        self.reset_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton))
        button_layout.addWidget(self.reset_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # 🔥 Load data saat aplikasi pertama kali dijalankan
        self.load_transactions()

        # 🔥 Klik tabel untuk isi form
        self.table.cellClicked.connect(self.fill_form)
    
    # Set locale untuk menampilkan nama hari & bulan dalam bahasa Indonesia
    try:
        locale.setlocale(locale.LC_TIME, "id_ID.UTF-8")  # Linux/Mac
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, "English_Indonesia.1252")  # Windows
        except locale.Error:
            locale.setlocale(locale.LC_TIME, "")  # Gunakan default OS
    def toggle_buyer_fields(self):
        is_income = self.type_input.currentText() == "Pemasukan"
        self.buyer_label.setVisible(is_income)
        self.buyer_input.setVisible(is_income)
        self.phone_label.setVisible(is_income)
        self.phone_input.setVisible(is_income)
        self.address_label.setVisible(is_income)
        self.address_input.setVisible(is_income)
    
    
    def fill_form(self, row, column):
        self.selected_id = self.table.item(row, 0).text()

        # 🔥 Set pilihan yang sesuai di ComboBox
        type_text = self.table.item(row, 1).text()
        index = self.type_input.findText(type_text)  # Cari index sesuai text
        if index != -1:
            self.type_input.setCurrentIndex(index)

        self.amount_input.setText(self.table.item(row, 2).text())

        # 🔥 Ubah format date agar sesuai dengan QDate
        date_text = self.table.item(row, 3).text()
        date_obj = QDate.fromString(date_text, "dddd, dd MMMM yyyy")  # Format yang sudah digunakan di tabel
        self.date_input.setDate(date_obj)

        self.desc_input.setText(self.table.item(row, 4).text())
        self.buyer_input.setText(self.table.item(row, 5).text())
        self.phone_input.setText(self.table.item(row, 6).text())
        self.address_input.setText(self.table.item(row, 7).text())

    def clear_form(self):
        self.type_input.setCurrentIndex(0)
        self.amount_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.desc_input.clear()
        self.buyer_input.clear()
        self.phone_input.clear()
        self.address_input.clear()
        self.selected_id = None  # Reset selected_id saat form dihapus
        
    def validate_amount_input(self):
        text = self.amount_input.text()

        # 🔥 Hanya izinkan angka dan titik
        new_text = "".join([char for char in text if char.isdigit() or char == "."])

        # Jika terjadi perubahan, update input
        if text != new_text:
            self.amount_input.setText(new_text)
    
    def load_transactions(self):
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                data = response.json().get("data", [])
                
                sorted_data = sorted(data, key=lambda x: x.get("updated_at", ""), reverse=True)

                # Ambil bulan & tahun yang dipilih
                selected_month = self.month_selector.currentIndex() + 1
                selected_year = int(self.year_selector.currentText())

                # Filter transaksi berdasarkan bulan & tahun
                filtered_data = []
                total_income = 0
                total_outcome = 0

                for transaction in sorted_data:
                    transaction_date = parser.parse(transaction['date'])
                    if transaction_date.month == selected_month and transaction_date.year == selected_year:
                        filtered_data.append(transaction)
                        amount = float(transaction['amount'])
                        if transaction['type'].lower() == "pemasukan":
                            total_income += amount
                        else:
                            total_outcome += amount

                self.table.setRowCount(len(filtered_data))

                for row, transaction in enumerate(filtered_data):
                    formatted_amount = f"Rp. {transaction['amount']:,.0f}".replace(",", ".")
                    formatted_date = transaction_date.strftime("%A, %d %B %Y")

                    if transaction['type'].lower() == "pemasukan":
                        text_color = QColor("green")
                        bg_color = QColor(220, 255, 220)
                    else:
                        text_color = QColor("red")
                        bg_color = QColor(255, 220, 220)  # Merah muda
                        
                    for col, value in enumerate([
                        transaction['id'], transaction['type'], formatted_amount,
                        formatted_date, transaction['description'],
                        transaction['buyer'], transaction['phone'], transaction['address']
                    ]):
                        item = QTableWidgetItem(value if value else "-")
                        item.setForeground(QBrush(text_color))
                        item.setBackground(QBrush(bg_color))
                        self.table.setItem(row, col, item)
                    
                    # self.table.setItem(row, 0, QTableWidgetItem(transaction['id']))  # ID (disembunyikan)
                    # self.table.setItem(row, 1, QTableWidgetItem(transaction['type']))
                    # self.table.setItem(row, 2, QTableWidgetItem(formatted_amount))
                    # self.table.setItem(row, 3, QTableWidgetItem(transaction['date']))
                    # self.table.setItem(row, 4, QTableWidgetItem(transaction['description']))
                    # self.table.setItem(row, 5, QTableWidgetItem(transaction['buyer']))
                    # self.table.setItem(row, 6, QTableWidgetItem(transaction['phone']))
                    # self.table.setItem(row, 7, QTableWidgetItem(transaction['address']))

                # Sembunyikan kolom ID
                self.table.hideColumn(0)

                # Update Label Income & Outcome
                self.income_label.setText(f"Total Pemasukkan: Rp. {total_income:,.0f}".replace(",", "."))
                self.outcome_label.setText(f"Total Pengeluaran: Rp. {total_outcome:,.0f}".replace(",", "."))

            else:
                QMessageBox.warning(self, "Error", "Gagal memuat transaksi.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Gagal menghubungi server: {e}")
    
    def create_transaction(self):
        amount_text = self.amount_input.text().replace("Rp. ", "").replace(".", "").strip()
    
        # 🔥 Cek apakah amount kosong atau bukan angka
        if not amount_text or not amount_text.replace(",", "").isdigit():
            QMessageBox.warning(self, "Error", "Amount harus berupa angka!")
            return
        
        data = {
            "id": str(uuid.uuid4()),
            "type": self.type_input.currentText(),
            "amount": float(self.amount_input.text()),
            "date": self.date_input.date().toString("yyyy-MM-dd") + "T00:00:00Z",
            "description": self.desc_input.text(),
            "buyer": self.buyer_input.text(),
            "phone": self.phone_input.text(),
            "address": self.address_input.text()
        }
        
        response = requests.post(API_URL, json=data)
        
        if response.status_code == 200:
            QMessageBox.information(self, "Success", "Transaksi berhasil dibuat.")
            self.load_transactions()
            self.clear_form()
        else:
            QMessageBox.warning(self, "Error", "Gagal membuat transaksi.")
    
    def update_transaction(self):
        if not hasattr(self, 'selected_id') or not self.selected_id:
            QMessageBox.warning(self, "Error", "Pilih transaksi yang akan diubah.")
            return

        try:
            # 🔥 Bersihkan format amount sebelum dikonversi
            amount_text = self.amount_input.text().replace("Rp. ", "").replace(".", "")
            amount_value = float(amount_text)  # Konversi ke float setelah dibersihkan
            
            data = {
                "type": self.type_input.currentText(),
                "amount": amount_value,
                "date": self.date_input.date().toString("yyyy-MM-dd") + "T00:00:00Z",
                "description": self.desc_input.text(),
                "buyer": self.buyer_input.text(),
                "phone": self.phone_input.text(),
                "address": self.address_input.text()
            }

            response = requests.put(f"{API_URL}/{self.selected_id}", json=data)

            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Transaksi berhasil diubah.")
                self.load_transactions()  # Refresh data setelah update
                self.clear_form()  # Hapus isian form saat update selesai  # Reset selected_id saat form dihapus  # Reset form sembunyikan kolom ID saat update selesai  # Tampilkan label Income & Outcome kembali saat update selesai  # Refresh data setelah update selesai  # Reset form sembunyikan kolom ID saat update selesai  #
            else:
                QMessageBox.warning(self, "Error", "Gagal mengubah transaksi.")
        
        except ValueError:
            QMessageBox.critical(self, "Error", "Format jumlah salah. Harus berupa angka valid.")
    
    def delete_transaction(self):
        if not hasattr(self, 'selected_id') or not self.selected_id:
            QMessageBox.warning(self, "Error", "Pilih transaksi yang akan dihapus.")
            return
        
        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus transaksi ID {self.selected_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            response = requests.delete(f"{API_URL}/{self.selected_id}")
            
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Transaksi berhasil dihapus.")
                self.load_transactions()
            else:
                QMessageBox.warning(self, "Error", "Gagal menghapus transaksi.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransactionApp()
    window.show()
    sys.exit(app.exec())
