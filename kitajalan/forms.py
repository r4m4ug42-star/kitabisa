# kitajalan/forms.py
from django import forms
from .models import BankSoal

class JawabanKuisForm(forms.Form):
    """Form untuk menjawab satu soal"""
    jawaban = forms.ChoiceField(
        choices=[('', 'Pilih jawaban...'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        widget=forms.RadioSelect,
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        self.soal = kwargs.pop('soal', None)
        super().__init__(*args, **kwargs)
        
        if self.soal:
            self.fields['jawaban'].label = self.soal.pertanyaan
            self.fields['jawaban'].choices = [
                ('', 'Pilih jawaban...'),
                ('A', f"A. {self.soal.pilihan_a}"),
                ('B', f"B. {self.soal.pilihan_b}"),
                ('C', f"C. {self.soal.pilihan_c}"),
                ('D', f"D. {self.soal.pilihan_d}"),
            ]