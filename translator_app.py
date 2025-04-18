import sys
import os
import re
import json
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QTextEdit, QComboBox, 
                           QLabel, QFileDialog, QTabWidget, QLineEdit, 
                           QMessageBox, QProgressDialog, QDialog, QScrollArea,
                           QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette, QColor
import google.generativeai as genai
from dotenv import load_dotenv
import PyPDF2
from docx import Document
import base64

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - BA Enterprise Tools")
        self.setFixedSize(300, 200)  # Reduced window width
        
        # Initialize input fields first
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Set dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                min-width: 120px;
                max-width: 120px;
            }
            QPushButton {
                background-color: #ff7700;
                color: #ffffff;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #ff8c00;
            }
            QPushButton:pressed {
                background-color: #ff6600;
            }
            QLabel {
                color: #ffffff;
                min-width: 50px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)  # Reduced spacing between elements
        
        # Title
        title_label = QLabel("BA Enterprise Tools")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Create a container widget for centering
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setSpacing(10)  # Reduced spacing
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Username
        username_layout = QHBoxLayout()
        username_layout.setSpacing(5)  # Reduced spacing between label and input
        username_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        username_label = QLabel("Usuário:")
        # Load saved username
        self.load_credentials()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        container_layout.addLayout(username_layout)
        
        # Password
        password_layout = QHBoxLayout()
        password_layout.setSpacing(5)  # Reduced spacing between label and input
        password_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        password_label = QLabel("Senha:")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        container_layout.addLayout(password_layout)
        
        # Login button
        login_btn = QPushButton("Entrar")
        login_btn.clicked.connect(self.try_login)
        container_layout.addWidget(login_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        container.setLayout(container_layout)
        layout.addWidget(container)
        
        self.setLayout(layout)
    
    def load_credentials(self):
        """Load saved credentials from file."""
        try:
            if os.path.exists('credentials.json'):
                with open('credentials.json', 'r', encoding='utf-8') as f:
                    credentials = json.load(f)
                    self.username_input.setText(credentials.get('username', ''))
                    self.password_input.setText(credentials.get('password', ''))
        except Exception as e:
            print(f"Error loading credentials: {str(e)}")
    
    def save_credentials(self, username, password):
        """Save credentials to file."""
        try:
            with open('credentials.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'username': username,
                    'password': password
                }, f)
        except Exception as e:
            print(f"Error saving credentials: {str(e)}")
    
    def try_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if username == "admin" and password == "7782":
            # Save credentials on successful login
            self.save_credentials(username, password)
            self.accept()
        else:
            QMessageBox.warning(self, "Erro", "Usuário ou senha incorretos!")
            self.username_input.clear()
            self.password_input.clear()
            self.username_input.setFocus()

class HistoryEntry(QFrame):
    def __init__(self, title, content, timestamp, parent=None):
        super().__init__(parent)
        self.content = content
        self.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }
            QFrame:hover {
                background-color: #3d3d3d;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Title and timestamp
        info_layout = QHBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.title_label.setFixedWidth(200)  # Fixed width for title
        self.timestamp_label = QLabel(timestamp)
        self.timestamp_label.setStyleSheet("color: #888888; font-size: 12px;")
        self.timestamp_label.setFixedWidth(120)  # Fixed width for timestamp
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.timestamp_label)
        layout.addLayout(info_layout)
        
        # Download button
        self.download_btn = QPushButton("Download")
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff7700;
                color: #ffffff;
                border: none;
                padding: 3px 8px;
                border-radius: 3px;
                min-width: 80px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #ff8c00;
            }
        """)
        layout.addWidget(self.download_btn)
        
        self.setLayout(layout)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(60)  # Increased height by 50% (from 40 to 60)

class TranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Show login dialog first
        login = LoginWindow()
        if login.exec() != QDialog.DialogCode.Accepted:
            # If login fails, close the application
            sys.exit()
        
        self.setWindowTitle("BA Enterprise Tools")
        self.setGeometry(100, 100, 1000, 600)  # Increased window size
        
        # Initialize history
        self.history = []
        self.history_layout = None  # Initialize history_layout as None
        self.load_history()
        
        # Initialize file storage
        self.current_file = None
        self.current_file_path = None
        
        # Set up cleanup timer (every hour)
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.cleanup_old_entries)
        self.cleanup_timer.start(3600000)  # 1 hour in milliseconds
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #ff7700;
                color: #ffffff;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff8c00;
            }
            QPushButton:pressed {
                background-color: #ff6600;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px;
                border: none;
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #ff7700;
            }
            QTabBar::tab:hover {
                background-color: #ff8c00;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
        # Load environment variables
        load_dotenv()
        
        # Initialize AI client
        self.gemini_client = None
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create translation tab
        self.create_translation_tab()
        
        # Create voiceover tab
        self.create_voiceover_tab()
        
        # Create settings tab
        self.create_settings_tab()
        
        # Initialize AI client if API key is available
        self.initialize_ai_client()
    
    def create_translation_tab(self):
        translation_tab = QWidget()
        layout = QHBoxLayout(translation_tab)
        
        # Left side - Input and output
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Input section
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Digite o texto da história para adaptação cultural...")
        self.input_text.textChanged.connect(self.update_counts)
        left_layout.addWidget(self.input_text)
        
        # Add word and character count labels
        counts_layout = QHBoxLayout()
        self.word_count_label = QLabel("Palavras: 0")
        self.char_count_label = QLabel("Caracteres: 0")
        counts_layout.addWidget(self.word_count_label)
        counts_layout.addWidget(self.char_count_label)
        left_layout.addLayout(counts_layout)
        
        # Language selection and translate button
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("País de Destino:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            "Estados Unidos",
            "Brasil",
            "México",
            "França",
            "Polônia",
            "Alemanha",
            "Romênia",
            "Itália",
            "Suécia",
            "Hungria",
            "Noruega"
        ])
        lang_layout.addWidget(self.lang_combo)
        
        # Create a container for the translate button
        self.translate_btn_container = QWidget()
        translate_btn_layout = QHBoxLayout(self.translate_btn_container)
        translate_btn_layout.setContentsMargins(0, 0, 0, 0)
        
        # Translate button
        self.translate_btn = QPushButton("Adaptar História")
        self.translate_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff7700;
                color: #ffffff;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #ff8c00;
            }
        """)
        self.translate_btn.clicked.connect(self.translate_text)
        translate_btn_layout.addWidget(self.translate_btn)
        
        # Loading spinner (initially hidden)
        self.loading_spinner = QLabel("⏳")
        self.loading_spinner.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: #ff7700;
                min-width: 120px;
                text-align: center;
            }
        """)
        self.loading_spinner.hide()
        translate_btn_layout.addWidget(self.loading_spinner)
        
        lang_layout.addWidget(self.translate_btn_container)
        left_layout.addLayout(lang_layout)
        
        # Output section
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("A história adaptada culturalmente aparecerá aqui...")
        left_layout.addWidget(self.output_text)
        
        # Save button and clock icon
        save_layout = QHBoxLayout()
        save_btn = QPushButton("Salvar")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff7700;
                color: #ffffff;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #ff8c00;
            }
        """)
        save_btn.clicked.connect(self.save_translation)
        
        # Clock icon button
        self.clock_btn = QPushButton("🕒")
        self.clock_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-size: 16px;
                min-width: 40px;
                max-width: 40px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
        """)
        self.clock_btn.clicked.connect(self.toggle_history)
        
        save_layout.addWidget(save_btn)
        save_layout.addWidget(self.clock_btn)
        left_layout.addLayout(save_layout)
        
        layout.addWidget(left_panel)
        
        # Right side - History (initially hidden)
        self.right_panel = QWidget()
        right_layout = QVBoxLayout(self.right_panel)
        
        # History title
        history_title = QLabel("Histórico (últimas 24h)")
        history_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(history_title)
        
        # History scroll area
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                background-color: #1e1e1e;
            }
        """)
        
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)  # Align content to bottom
        self.history_scroll.setWidget(self.history_container)
        right_layout.addWidget(self.history_scroll)
        
        layout.addWidget(self.right_panel)
        self.right_panel.hide()  # Initially hide the history panel
        
        self.tabs.addTab(translation_tab, "Adaptação Cultural")
        
        # Update history display
        self.update_history_display()
    
    def create_voiceover_tab(self):
        voiceover_tab = QWidget()
        layout = QVBoxLayout(voiceover_tab)
        
        # Add construction message
        construction_label = QLabel("Em construção")
        construction_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #ff7700;
        """)
        construction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(construction_label)
        
        self.tabs.addTab(voiceover_tab, "VoiceOver")
    
    def create_settings_tab(self):
        settings_tab = QWidget()
        layout = QVBoxLayout(settings_tab)
        
        # Gemini API Key
        gemini_layout = QHBoxLayout()
        gemini_layout.addWidget(QLabel("Chave da API Gemini:"))
        self.gemini_key = QLineEdit()
        self.gemini_key.setEchoMode(QLineEdit.EchoMode.Password)
        if os.getenv("GEMINI_API_KEY"):
            self.gemini_key.setText(os.getenv("GEMINI_API_KEY"))
        gemini_layout.addWidget(self.gemini_key)
        layout.addLayout(gemini_layout)
        
        # Save settings button
        save_settings_btn = QPushButton("Salvar Chave da API")
        save_settings_btn.clicked.connect(self.save_api_key)
        layout.addWidget(save_settings_btn)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #3d3d3d;")
        layout.addWidget(separator)
        
        # Prompt Configuration
        prompt_label = QLabel("Prompt de Adaptação Cultural:")
        prompt_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        layout.addWidget(prompt_label)
        
        self.prompt_text = QTextEdit()
        self.prompt_text.setPlaceholderText("Digite o prompt de adaptação cultural...")
        self.prompt_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
                min-height: 200px;
            }
        """)
        
        # Load default prompt
        default_prompt = """You are an expert in the cultural adaptation of narratives. Your task is to take a given story and adapt it so that it feels natural within the context of a specific target country, translating the text into the language of that country and adjusting elements that reflect the local culture to make it more authentic.

Read this history {text} 

Make a natural and subtle cultural adaptation to this target country: {country}

Based on the story and the target country, make the following adaptations:

Language: Translate the text into the language of {country}.
Cultural elements: Adapt any elements that reflect the local culture of {country}. This may include, but is not limited to:
People's names: Replace all the characters' original names with less common ones that are still recognizable as belonging to {country}. Make sure the new names match the age and social status of the original characters.
Place names (cities, states, locations, beaches and any other regional location)
Company names
Sports
Slang and idiomatic expressions
Other relevant cultural aspects

ALWAYS maintain the original text: Do not add any new information or alter the essence of the original text, only do the culture adaptation

Provide only the adapted text, without any additional explanations or notes.

No numbering: Present the adapted story as a continuous narrative.

NEVER erase call to actions and other types of communications."""
        
        self.prompt_text.setText(default_prompt)
        layout.addWidget(self.prompt_text)
        
        # Save prompt button
        save_prompt_btn = QPushButton("Salvar Prompt")
        save_prompt_btn.clicked.connect(self.save_prompt)
        layout.addWidget(save_prompt_btn)
        
        self.tabs.addTab(settings_tab, "Configurações")
    
    def initialize_ai_client(self):
        # Initialize Gemini client
        if os.getenv("GEMINI_API_KEY"):
            try:
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                # Use the fastest model available
                self.gemini_client = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                QMessageBox.warning(self, "Aviso", f"Falha ao inicializar Gemini: {str(e)}")
    
    def update_counts(self):
        """Update word and character count labels."""
        text = self.input_text.toPlainText()
        
        # Count words (split by whitespace)
        words = len(text.split()) if text.strip() else 0
        
        # Count characters (including spaces)
        chars = len(text)
        
        # Update labels
        self.word_count_label.setText(f"Palavras: {words}")
        self.char_count_label.setText(f"Caracteres: {chars}")

    def translate_text(self):
        if not self.gemini_client:
            QMessageBox.critical(self, "Erro", "Por favor, configure sua chave da API Gemini na aba Configurações")
            return
        
        target_country = self.lang_combo.currentText()
        
        try:
            # Hide translate button and show spinner
            self.translate_btn.hide()
            self.loading_spinner.show()
            
            # Get text from input
            text = self.input_text.toPlainText()
            if not text:
                QMessageBox.warning(self, "Aviso", "Por favor, digite um texto para adaptar")
                self.translate_btn.show()
                self.loading_spinner.hide()
                return
            
            # Get translation
            translation = self.translate_with_gemini(text, target_country)
            if translation:
                self.output_text.setText(translation)
                # Add to history with target country
                self.add_to_history(target_country, translation)
            else:
                QMessageBox.critical(self, "Erro", "Falha na adaptação cultural. Por favor, tente novamente.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha na adaptação cultural: {str(e)}")
        finally:
            # Show translate button and hide spinner
            self.translate_btn.show()
            self.loading_spinner.hide()
    
    def translate_with_gemini(self, text, target_country, progress=None):
        try:
            # Use the current prompt from the settings
            prompt_template = self.prompt_text.toPlainText()
            
            # Split text into chunks if it's too long
            if len(text) > 29000:
                chunks = self.split_text_into_chunks(text)
                total_chunks = len(chunks)
                translated_chunks = []
                
                for i, chunk in enumerate(chunks, 1):
                    # Update progress
                    if progress:
                        progress.setValue(int((i - 1) / total_chunks * 90))
                        progress.setLabelText(f"Adaptando parte {i} de {total_chunks}...")
                    
                    # Create the prompt for this chunk
                    chunk_prompt = prompt_template.replace("{text}", chunk).replace("{country}", target_country)
                    
                    # Translate and adapt chunk
                    response = self.gemini_client.generate_content(chunk_prompt)
                    
                    # Process the translated chunk
                    if response.text:
                        # Clean up the chunk and ensure it ends with proper spacing
                        cleaned_chunk = response.text.strip()
                        # Ensure chunk ends with exactly one newline
                        cleaned_chunk = cleaned_chunk.replace("\n\n\n", "\n\n")
                        translated_chunks.append(cleaned_chunk)
                    
                    # Small delay between requests to avoid rate limiting
                    if i < total_chunks:
                        import time
                        time.sleep(1)
                
                # Combine all chunks with proper spacing
                final_text = "\n\n".join(translated_chunks)
                # Clean up any excessive newlines that might have been created
                final_text = re.sub(r'\n{3,}', '\n\n', final_text)
                return final_text.strip()
            else:
                # For short texts, translate directly
                prompt = prompt_template.replace("{text}", text).replace("{country}", target_country)
                response = self.gemini_client.generate_content(prompt)
                return response.text.strip()
                
        except Exception as e:
            if "quota" in str(e).lower():
                raise Exception("Limite da API excedido. Por favor, tente novamente mais tarde ou verifique seus limites de uso da API.")
            elif "model" in str(e).lower():
                raise Exception("Modelo não encontrado. Por favor, verifique sua chave de API e tente novamente.")
            else:
                raise Exception(f"Erro na adaptação cultural: {str(e)}")
    
    def save_translation(self):
        translation = self.output_text.toPlainText()
        if not translation:
            QMessageBox.warning(self, "Aviso", "Nenhuma adaptação para salvar")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Adaptação", "", "Arquivos de Texto (*.txt);;Todos os Arquivos (*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(translation)
                QMessageBox.information(self, "Sucesso", "Adaptação salva com sucesso")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao salvar arquivo: {str(e)}")
    
    def save_api_key(self):
        # Save API key to .env file
        with open('.env', 'w') as f:
            if self.gemini_key.text():
                f.write(f"GEMINI_API_KEY={self.gemini_key.text()}\n")
        
        # Reinitialize AI client
        self.initialize_ai_client()
        QMessageBox.information(self, "Sucesso", "Chave da API salva com sucesso")

    def save_prompt(self):
        """Save the current prompt to a file."""
        try:
            with open('prompt.txt', 'w', encoding='utf-8') as f:
                f.write(self.prompt_text.toPlainText())
            QMessageBox.information(self, "Sucesso", "Prompt salvo com sucesso")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar prompt: {str(e)}")

    def add_to_history(self, target_country, content):
        """Add a new entry to the history."""
        entry = {
            'title': f"Adaptação para {target_country}",
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self.history.append(entry)
        self.save_history()
        self.update_history_display()

    def update_history_display(self):
        """Update the history display with current entries."""
        if self.history_layout is None:
            return  # Skip if history_layout is not initialized yet
            
        # Clear existing entries
        for i in reversed(range(self.history_layout.count())): 
            self.history_layout.itemAt(i).widget().setParent(None)
        
        # Add entries in chronological order (oldest first)
        for entry in self.history:
            frame = HistoryEntry(
                entry['title'],
                entry['content'],
                datetime.fromisoformat(entry['timestamp']).strftime('%H:%M - %d/%m/%Y')
            )
            frame.mousePressEvent = lambda e, content=entry['content']: self.show_history_entry(content)
            frame.download_btn.clicked.connect(lambda checked, content=entry['content']: self.download_history_entry(content))
            self.history_layout.addWidget(frame)
            self.history_layout.setSpacing(1)  # Minimal spacing between entries
            self.history_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)  # Align entries to bottom

    def show_history_entry(self, content):
        """Show the full content of a history entry."""
        self.output_text.setText(content)

    def download_history_entry(self, content):
        """Download a history entry."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar História",
            "",
            "Arquivos de Texto (*.txt);;Todos os Arquivos (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                QMessageBox.information(self, "Sucesso", "História salva com sucesso")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao salvar arquivo: {str(e)}")

    def save_history(self):
        """Save history to a file."""
        try:
            with open('history.json', 'w', encoding='utf-8') as f:
                json.dump(self.history, f)
        except Exception as e:
            print(f"Error saving history: {str(e)}")

    def load_history(self):
        """Load history from file."""
        try:
            if os.path.exists('history.json'):
                with open('history.json', 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                self.cleanup_old_entries()  # Clean up old entries on load
        except Exception as e:
            print(f"Error loading history: {str(e)}")
            self.history = []

    def cleanup_old_entries(self):
        """Remove entries older than 24 hours."""
        now = datetime.now()
        self.history = [
            entry for entry in self.history
            if now - datetime.fromisoformat(entry['timestamp']) < timedelta(hours=24)
        ]
        self.save_history()
        self.update_history_display()

    def toggle_history(self):
        """Toggle the visibility of the history panel."""
        if self.right_panel.isVisible():
            self.right_panel.hide()
        else:
            self.right_panel.show()

    def split_text_into_chunks(self, text, max_chunk_size=29000):
        """Split text into chunks of approximately equal size, trying to break at paragraph boundaries."""
        chunks = []
        current_chunk = ""
        
        # Split text into paragraphs
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed the chunk size, save current chunk and start new one
            if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TranslatorApp()
    window.show()
    sys.exit(app.exec()) 