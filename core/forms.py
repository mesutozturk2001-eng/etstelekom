from django import forms
from django.contrib.auth.models import User
from .models import AvansTalebi, Personel, AvansHareketi, IzinTalebi, MasrafTalebi, Zimmet, Egitim, PROFIL_CHOICES

class AvansTalepForm(forms.ModelForm):
    class Meta:
        model = AvansTalebi
        fields = ['miktar', 'tarih', 'aciklama']
        widgets = {
            'tarih': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'miktar': forms.NumberInput(attrs={'class': 'form-control'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PersonelForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, label="Ad", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=True, label="Soyad", widget=forms.TextInput(attrs={'class': 'form-control'}))
    tc_no = forms.CharField(max_length=11, required=True, label="TC Kimlik No", 
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '11 haneli TC No', 'maxlength': '11', 'pattern': '[0-9]{11}', 'title': 'TC No 11 rakamdan oluşmalıdır'}))

    class Meta:
        model = Personel
        # izin_hakki otomatik hesaplanır, elle girilemez
        fields = ['tc_no', 'telefon', 'pozisyon', 'profil_tipi', 'adres', 'dogum_tarihi', 'ise_giris_tarihi', 'izin_hakki', 'kalan_izin', 'guncel_avans_borcu', 'first_name', 'last_name', 'yonetici']
        widgets = {
            'tc_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'TC Kimlik No'}),
            'telefon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefon'}),
            'pozisyon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pozisyon'}),
            'profil_tipi': forms.Select(attrs={'class': 'form-select'}, choices=PROFIL_CHOICES),
            'adres': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Adres', 'rows': 2}),
            'dogum_tarihi': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'ise_giris_tarihi': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'izin_hakki': forms.NumberInput(attrs={'class': 'form-control', 'value': '14'}),
            'kalan_izin': forms.NumberInput(attrs={'class': 'form-control', 'value': '0'}),
            'guncel_avans_borcu': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'yonetici': forms.Select(attrs={'class': 'form-select', 'placeholder': 'Yönetici Seç'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Kalan izin zorunlu değil, boşsa 0 olacak
        self.fields['kalan_izin'].required = False
        # Telefon zorunlu değil
        self.fields['telefon'].required = False
        # İzin hakkı zorunlu değil
        self.fields['izin_hakki'].required = False
        # Yönetici alanı için sorgu: Aktif personelleri listele
        if self.instance and self.instance.pk:
            self.fields['yonetici'].queryset = Personel.objects.filter(aktif=True).exclude(pk=self.instance.pk)
        else:
            self.fields['yonetici'].queryset = Personel.objects.filter(aktif=True)
        self.fields['yonetici'].required = False
        self.fields['yonetici'].empty_label = 'Yönetici Seç (Opsiyonel)'
    
    def clean_dogum_tarihi(self):
        dogum_tarihi = self.cleaned_data.get('dogum_tarihi')
        if not dogum_tarihi:
            raise forms.ValidationError("Doğum tarihi zorunludur!")
        return dogum_tarihi
        
    def clean_tc_no(self):
        tc_no = self.cleaned_data.get('tc_no')
        if tc_no:
            # Sadece rakam kontrolü
            if not tc_no.isdigit():
                raise forms.ValidationError("TC Kimlik No yalnızca rakamlardan oluşmalıdır.")
            # 11 hane kontrolü
            if len(tc_no) != 11:
                raise forms.ValidationError("TC Kimlik No 11 haneli olmalıdır.")
        return tc_no

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label="Excel Dosyası Seç (.xlsx)", widget=forms.FileInput(attrs={'class': 'form-control'}))


class AvansIslemForm(forms.Form):
    ISLEM_CHOICES = [
        ('EKLE', 'Avans Borcu Ekle'),
        ('AZALT', 'Avans Borcu Azalt'),
    ]
    islem_turu = forms.ChoiceField(choices=ISLEM_CHOICES, label="İşlem Türü", widget=forms.Select(attrs={'class': 'form-select'}))
    miktar = forms.DecimalField(max_digits=10, decimal_places=2, label="Miktar (TL)", widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}))
    aciklama = forms.CharField(required=False, label="Açıklama", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))


# Kullanıcının kendi bilgilerini güncellemesi için form (sınırlı alanlar)
class PersonelKendiForm(forms.ModelForm):
    class Meta:
        model = Personel
        fields = ['telefon', 'adres']
        widgets = {
            'telefon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefon'}),
            'adres': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Adres', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['telefon'].required = False


# İzin Talep Formu (Personel için)
class IzinTalebiForm(forms.ModelForm):
    class Meta:
        model = IzinTalebi
        fields = ['baslangic_tarihi', 'bitis_tarihi', 'aciklama']
        widgets = {
            'baslangic_tarihi': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'bitis_tarihi': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'İzin sebebini belirtiniz'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['aciklama'].required = False

    def clean(self):
        cleaned_data = super().clean()
        baslangic = cleaned_data.get('baslangic_tarihi')
        bitis = cleaned_data.get('bitis_tarihi')
        
        if baslangic and bitis:
            if bitis < baslangic:
                raise forms.ValidationError("Bitiş tarihi, başlangıç tarihinden önce olamaz.")
        return cleaned_data


# İzin Onay/Red Formu (Admin için)
class IzinOnayForm(forms.ModelForm):
    class Meta:
        model = IzinTalebi
        fields = ['durum', 'admin_notu']
        widgets = {
            'durum': forms.Select(attrs={'class': 'form-select'}),
            'admin_notu': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Varsa notunuz'}),
        }


# Masraf Talep Formu (Personel için)
class MasrafTalepForm(forms.ModelForm):
    class Meta:
        model = MasrafTalebi
        fields = ['miktar', 'aciklama', 'fis_fatura', 'tarih']
        widgets = {
            'miktar': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Masrafın açıklamasını giriniz'}),
            'fis_fatura': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'tarih': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fiş/fatura zorunlu
        self.fields['fis_fatura'].required = True
        self.fields['fis_fatura'].label = "Fiş/Fatura Resmi *"


# Masraf Onay/Red Formu (Admin için)
class MasrafOnayForm(forms.ModelForm):
    class Meta:
        model = MasrafTalebi
        fields = ['durum', 'admin_notu']
        widgets = {
            'durum': forms.Select(attrs={'class': 'form-select'}),
            'admin_notu': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Varsa notunuz'}),
        }


# Zimmet Formu (Admin için)
class ZimmetForm(forms.ModelForm):
    class Meta:
        model = Zimmet
        fields = ['malzeme', 'tarih', 'durum', 'aciklama']
        widgets = {
            'malzeme': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Malzeme Adı'}),
            'tarih': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'durum': forms.Select(attrs={'class': 'form-select'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Açıklama'}),
        }


# Egitim Formu (Admin için)
class EgitimForm(forms.ModelForm):
    class Meta:
        model = Egitim
        fields = ['egitim_adi', 'tarih', 'sure', 'durum', 'aciklama']
        widgets = {
            'egitim_adi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Eğitim Adı'}),
            'tarih': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'sure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Süre (örn: 2 saat)'}),
            'durum': forms.Select(attrs={'class': 'form-select'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Açıklama'}),
        }
