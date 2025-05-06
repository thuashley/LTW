from django import forms
from django.forms import inlineformset_factory
from .models import NhapKho, ChiTietNhap, HangHoa

class NhapKhoForm(forms.ModelForm):
    class Meta:
        model = NhapKho
        fields = ['ma_nhap', 'nguon_nhap', 'thoi_gian', 'sdt', 'diachi', 'ly_do', 'url_hop_dong', 'url_so_cu']
        widgets = {
            'ma_nhap': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Để trống để tự động tạo'}),
            'nguon_nhap': forms.TextInput(attrs={'class': 'form-control'}),
            'thoi_gian': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'sdt': forms.TextInput(attrs={'class': 'form-control'}),
            'diachi': forms.TextInput(attrs={'class': 'form-control'}),
            'ly_do': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'url_hop_dong': forms.FileInput(attrs={'class': 'form-control'}),
            'url_so_cu': forms.FileInput(attrs={'class': 'form-control'}),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['ma_nhap'].required = False


class ChiTietNhapForm(forms.ModelForm):
    class Meta:
        model = ChiTietNhap
        fields = ['ma_hang', 'don_gia_nhap', 'so_luong_nhap', 'chiet_khau']
        widgets = {
            'ma_hang': forms.Select(attrs={
                'class': 'form-select hang-hoa-select',
                'data-live-search': 'true'
            }),
            'don_gia_nhap': forms.NumberInput(attrs={
                'class': 'form-control don-gia',
                'min': '0',
                'step': '1000'
            }),
            'so_luong_nhap': forms.NumberInput(attrs={
                'class': 'form-control so-luong',
                'min': '1'
            }),
            'chiet_khau': forms.NumberInput(attrs={
                'class': 'form-control chiet-khau',
                'min': '0',
                'max': '100',
                'step': '0.1'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ma_hang'].queryset = HangHoa.objects.all()
        self.fields['ma_hang'].label_from_instance = lambda obj: f"{obj.ten_hang} ({obj.ma_hang})"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ma_hang'].queryset = HangHoa.objects.all()

ChiTietNhapFormSet = forms.inlineformset_factory(
    NhapKho,
    ChiTietNhap,
    form=ChiTietNhapForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)


from django import forms
from django.forms import inlineformset_factory
from .models import XuatKho, ChiTietXuat, HangHoa


class XuatKhoForm(forms.ModelForm):
    class Meta:
        model = XuatKho
        fields = ['ma_xuat', 'nguon_nhan', 'thoi_gian', 'sdt', 'diachi', 'ly_do', 'url_hop_dong', 'url_so_cu']
        widgets = {
            'ma_xuat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Để trống để tự động tạo'}),
            'nguon_nhan': forms.TextInput(attrs={'class': 'form-control'}),
            'thoi_gian': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'sdt': forms.TextInput(attrs={'class': 'form-control'}),
            'diachi': forms.TextInput(attrs={'class': 'form-control'}),
            'ly_do': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'url_hop_dong': forms.FileInput(attrs={'class': 'form-control'}),
            'url_so_cu': forms.FileInput(attrs={'class': 'form-control'}),
        }



class ChiTietXuatForm(forms.ModelForm):
    hang_hoa_display = forms.CharField(required=False,
                                       widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}))

    class Meta:
        model = ChiTietXuat
        fields = ['ma_hang', 'don_gia_xuat', 'so_luong_xuat', 'chiet_khau']
        widgets = {
            'ma_hang': forms.Select(attrs={'class': 'form-control hang-hoa-select'}),
            'don_gia_xuat': forms.NumberInput(attrs={'class': 'form-control don-gia', 'min': '0', 'step': '1000'}),
            'so_luong_xuat': forms.NumberInput(attrs={'class': 'form-control so-luong', 'min': '1'}),
            'chiet_khau': forms.NumberInput(
                attrs={'class': 'form-control chiet-khau', 'min': '0', 'max': '100', 'step': '0.1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ma_hang'].queryset = HangHoa.objects.all()

        # Nếu đã có instance, hiển thị tên hàng hóa
        if self.instance and self.instance.pk and self.instance.ma_hang:
            self.fields['hang_hoa_display'].initial = self.instance.ma_hang.ten_hang

# Tạo formset cho chi tiết xuất kho
ChiTietXuatFormSet = inlineformset_factory(
    XuatKho,
    ChiTietXuat,
    form=ChiTietXuatForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)

from django import forms
from django.forms import inlineformset_factory
from .models import KiemKe, ChiTietKiemKe

class KiemKeForm(forms.ModelForm):
    thoi_gian = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Thời gian kiểm kê'
    )

    class Meta:
        model = KiemKe
        fields = ['ma_kiemke', 'muc_dich', 'thoi_gian', 'tinh_trang']

class ChiTietKiemKeForm(forms.ModelForm):
    class Meta:
        model = ChiTietKiemKe
        fields = ['hang_hoa', 'so_luong_tai_kho', 'xu_ly']

ChiTietKiemKeFormSet = inlineformset_factory(
    KiemKe,
    ChiTietKiemKe,
    form=ChiTietKiemKeForm,
    extra=1,
    can_delete=True
)

class ChiTietKiemKeFormUpdate(forms.ModelForm):
    class Meta:
        model = ChiTietKiemKe
        fields = ['so_luong_tai_kho', 'xu_ly']

ChiTietKiemKeFormSetUpdate = inlineformset_factory(
    KiemKe,
    ChiTietKiemKe,
    form=ChiTietKiemKeFormUpdate,
    extra=0,
    can_delete=True
)