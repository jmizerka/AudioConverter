import tkinter as tk
from tkinter import filedialog
from TTS.api import TTS
import PyPDF2
import docx
import textract
import torch
import re


class AudioConverter:

    def __init__(self):
        self.root = tk.Tk()  # create tk app
        self.root.title("Konwerter plików tekstowych na audio")
        # you can check available models by tts --list_models in command line
        self.model_name = 'tts_models/en/jenny/jenny'  # Default English model
        self.output_file_name = "output.wav"  # Default output file name
        self.make_layout()

    # set app layout
    def make_layout(self):
        button_add_file = tk.Button(self.root, text="Dodaj plik", command=self.add_text_file)
        button_convert = tk.Button(self.root, text="Konwertuj", command=self.convert)
        button_choose_output = tk.Button(self.root, text="Wybierz plik wyjściowy", command=self.choose_output_file)
        self.label_info = tk.Label(self.root, text="")
        button_add_file.pack(pady=10)
        button_choose_output.pack(pady=10)
        button_convert.pack(pady=10)
        self.label_info.pack(pady=10)

    # run mainloop
    def run(self):
        self.root.mainloop()

    # add file type selection
    def add_text_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Pliki tekstowe", "*.txt"),
                ("Pliki PDF", "*.pdf"),
                ("Dokumenty Word", "*.doc;*.docx"),
                ("Wszystkie pliki", "*.*"),
            ]
        )
        if file_path:
            self.label_info.config(text=f"Wybrano plik: {file_path}")
            self.text_file = file_path

    # choose output file if you want to change the default one
    def choose_output_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Pliki WAV", "*.wav")])
        if file_path:
            self.output_file_name = file_path
            self.label_info.config(text=f"Zapisywanie wyników do pliku: {self.output_file_name}")

    def convert(self):
        # determine if input file was chosen
        if hasattr(self, 'text_file') and self.text_file:
            # use gpu if available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            if self.text_file.lower().endswith('.pdf'):
                # handle pdf file
                with open(self.text_file, "rb") as file:
                    pdf_reader = PyPDF2.PdfReader(file, strict=False)  # read file even if broken structure
                    text = ''
                    for page in pdf_reader.pages:
                        text += page.extract_text()
            elif self.text_file.lower().endswith(('.doc', '.docx')):
                # handle .doc and .docx files
                doc = docx.Document(self.text_file) if self.text_file.lower().endswith('.docx') else textract.process(
                    self.text_file).decode('utf-8')
                text = ' '.join([paragraph.text for paragraph in doc.paragraphs])
            elif self.text_file.lower().endswith('.txt'):
                # handle .txt file
                with open(self.text_file, 'r', encoding='utf-8') as file:
                    text = file.read()

            # remove page numbers
            text = re.sub(r'. \d+', '', text, flags=re.MULTILINE)
            # detect language of text
            language = self.detect_language(text)
            if language == 'pl':
                self.model_name = 'tts_models/pl/mai_female/vits'

            # Text-to-Speech conversion
            tts = TTS(model_name=self.model_name).to(device)
            tts.tts_to_file(text=text, file_path=self.output_file_name)

            self.label_info.config(text=f"Konwersja zakończona. Wyniki zapisane w {self.output_file_name}")
        else:
            self.label_info.config(text="Nie wybrano pliku tekstowego")

    # simple language detection based on polish symbols occurrence
    @staticmethod
    def detect_language(text):
        if any(char in 'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ' for char in text):
            return 'pl'
        else:
            return 'en'


# Create an instance of the AudioConverter class
text_to_audio_conv = AudioConverter()

# Run the application
text_to_audio_conv.run()
