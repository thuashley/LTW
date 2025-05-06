from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum, F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name="Chức vụ")

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.username})"

# Choices cho các bảng
TINH_TRANG_NHAPKHO_CHOICES = [
    ('CHO_DUYET', 'Chờ duyệt'),
    ('DA_DUYET', 'Đã duyệt'),
    ('DA_NHAP', 'Đã nhập'),
    ('TU_CHOI', 'Từ chối'),
]

TINH_TRANG_XUATKHO_CHOICES = [
    ('CHO_DUYET', 'Chờ duyệt'),
    ('DA_DUYET', 'Đã duyệt'),
    ('DA_XUAT', 'Đã xuất'),
    ('TU_CHOI', 'Từ chối'),
    ('HOAN_HANG', 'Hoàn hàng'),
]

TINH_TRANG_KIEMKE_CHOICES = [
    ('CHO_DUYET', 'Chờ duyệt'),
    ('DA_DUYET', 'Đã duyệt'),
    ('TU_CHOI', 'Từ chối'),
]

TINH_TRANG_TONKHO_CHOICES = [
    ('CON_HANG', 'Còn hàng'),
    ('GAN_HET_HANG', 'Gần hết hàng'),
    ('HET_HANG', 'Hết hàng'),
]

# 1. HangHoa (gộp với TonKho)
class HangHoa(models.Model):
    ma_hang = models.CharField(max_length=50, primary_key=True, verbose_name="Mã hàng")
    ten_hang = models.CharField(max_length=255, verbose_name="Tên hàng")
    nhom_hang = models.CharField(max_length=100, verbose_name="Nhóm hàng")
    url_image = models.ImageField(upload_to='images/hanghoa/', blank=True, null=True, verbose_name="Ảnh sản phẩm")
    don_vi_tinh = models.CharField(max_length=50, verbose_name="Đơn vị tính")
    han_su_dung = models.DateField(blank=True, null=True, verbose_name="Hạn sử dụng")
    mo_ta = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    so_luong_he_thong = models.PositiveIntegerField(default=0, verbose_name="Số lượng hệ thống")
    tinh_trang = models.CharField(
        max_length=50,
        choices=TINH_TRANG_TONKHO_CHOICES,
        default='CON_HANG',
        verbose_name="Tình trạng tồn cuoiky"
    )

    def __str__(self):
        return f"{self.ma_hang} - {self.ten_hang} (Tồn: {self.so_luong_he_thong})"

    class Meta:
        verbose_name = "Hàng Hóa"
        verbose_name_plural = "Hàng Hóa"
        ordering = ['ten_hang']

# 2. NhapKho
class NhapKho(models.Model):
    ma_nhap = models.CharField(max_length=50, primary_key=True, verbose_name="Mã phiếu nhập")
    nguon_nhap = models.CharField(max_length=255, verbose_name="Nguồn nhập")
    thoi_gian = models.DateTimeField(default=timezone.now, verbose_name="Thời gian nhập")
    tinh_trang = models.CharField(
        max_length=50,
        choices=TINH_TRANG_NHAPKHO_CHOICES,
        default='CHO_DUYET',
        verbose_name="Tình trạng phiếu"
    )
    tong = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Tổng tiền")
    tao_boi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phieu_nhap_kho',
        verbose_name="Người tạo"
    )
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo phiếu")
    sdt = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    diachi = models.CharField(max_length=500, blank=True, null=True, verbose_name="Địa chỉ")
    ly_do = models.TextField(blank=True, null=True, verbose_name="Lý do nhập")
    url_hop_dong = models.FileField(upload_to='files/nhapkho/hopdong/', blank=True, null=True, verbose_name="File hợp đồng")
    url_so_cu = models.FileField(upload_to='files/nhapkho/socu/', blank=True, null=True, verbose_name="File sổ cũ")

    def tinh_lai_tong_tien(self):
        total = self.chi_tiet_nhap.aggregate(Sum('thanh_tien'))['thanh_tien__sum'] or 0.00
        self.tong = total
        self.save(update_fields=['tong'])

    def __str__(self):
        return self.ma_nhap

    class Meta:
        verbose_name = "Phiếu Nhập Kho"
        verbose_name_plural = "Phiếu Nhập Kho"
        ordering = ['-ngay_tao']

# 3. ChiTietNhap
class ChiTietNhap(models.Model):
    ma_nhap = models.ForeignKey(
        NhapKho,
        on_delete=models.CASCADE,
        related_name='chi_tiet_nhap',
        to_field='ma_nhap',
        verbose_name="Mã phiếu nhập"
    )
    ma_hang = models.ForeignKey(
        HangHoa,
        on_delete=models.PROTECT,
        related_name='chi_tiet_nhap',
        to_field='ma_hang',
        verbose_name="Mã hàng"
    )
    don_gia_nhap = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Đơn giá nhập")
    so_luong_nhap = models.PositiveIntegerField(verbose_name="Số lượng nhập")
    chiet_khau = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Chiết khấu")
    thanh_tien = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Thành tiền", editable=False)

    def clean(self):
        super().clean()
        if self.so_luong_nhap is None or self.so_luong_nhap <= 0:
            raise ValidationError({'so_luong_nhap': 'Số lượng nhập phải lớn hơn 0.'})
        if self.don_gia_nhap < 0:
            raise ValidationError({'don_gia_nhap': 'Đơn giá nhập không được âm.'})
        if self.chiet_khau < 0:
            raise ValidationError({'chiet_khau': 'Chiết khấu không được âm.'})
        if self.chiet_khau > (self.don_gia_nhap * self.so_luong_nhap):
            raise ValidationError({'chiet_khau': 'Chiết khấu không được lớn hơn giá trị hàng.'})

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.thanh_tien = (self.don_gia_nhap * self.so_luong_nhap) - self.chiet_khau
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Chi tiết {self.ma_nhap.ma_nhap} - {self.ma_hang.ten_hang}"

    class Meta:
        verbose_name = "Chi Tiết Nhập Kho"
        verbose_name_plural = "Chi Tiết Nhập Kho"
        unique_together = ('ma_nhap', 'ma_hang')
        ordering = ['ma_nhap', 'ma_hang']

# 4. XuatKho
class XuatKho(models.Model):
    ma_xuat = models.CharField(max_length=50, primary_key=True, verbose_name="Mã phiếu xuất")
    nguon_nhan = models.CharField(max_length=255, verbose_name="Nguồn nhận")
    thoi_gian = models.DateTimeField(default=timezone.now, verbose_name="Thời gian xuất")
    tinh_trang = models.CharField(
        max_length=50,
        choices=TINH_TRANG_XUATKHO_CHOICES,
        default='CHO_DUYET',
        verbose_name="Tình trạng phiếu"
    )
    tong = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Tổng tiền")
    tao_boi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phieu_xuat_kho',
        verbose_name="Người tạo"
    )
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo phiếu")
    sdt = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    diachi = models.CharField(max_length=500, blank=True, null=True, verbose_name="Địa chỉ")
    ly_do = models.TextField(blank=True, null=True, verbose_name="Lý do xuất")
    url_hop_dong = models.FileField(upload_to='files/xuatkho/hopdong/', blank=True, null=True, verbose_name="File hợp đồng")
    url_so_cu = models.FileField(upload_to='files/xuatkho/socu/', blank=True, null=True, verbose_name="File sổ cũ")

    def tinh_lai_tong_tien(self):
        total = self.chi_tiet_xuat.aggregate(Sum('thanh_tien'))['thanh_tien__sum'] or 0.00
        self.tong = total
        self.save(update_fields=['tong'])

    def __str__(self):
        return self.ma_xuat

    class Meta:
        verbose_name = "Phiếu Xuất Kho"
        verbose_name_plural = "Phiếu Xuất Kho"
        ordering = ['-ngay_tao']

# 5. ChiTietXuat
class ChiTietXuat(models.Model):
    ma_xuat = models.ForeignKey(
        XuatKho,
        on_delete=models.CASCADE,
        related_name='chi_tiet_xuat',
        to_field='ma_xuat',
        verbose_name="Mã phiếu xuất"
    )
    ma_hang = models.ForeignKey(
        HangHoa,
        on_delete=models.PROTECT,
        related_name='chi_tiet_xuat',
        to_field='ma_hang',
        verbose_name="Mã hàng"
    )
    don_gia_xuat = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Đơn giá xuất")
    so_luong_xuat = models.PositiveIntegerField(verbose_name="Số lượng xuất")
    chiet_khau = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Chiết khấu")
    thanh_tien = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Thành tiền", editable=False)

    def clean(self):
        if self.so_luong_xuat is None or self.so_luong_xuat <= 0:
            raise ValidationError({'so_luong_xuat': 'Số lượng xuất phải lớn hơn 0.'})
        if self.don_gia_xuat < 0:
            raise ValidationError({'don_gia_xuat': 'Đơn giá xuất không được âm.'})
        if self.chiet_khau < 0:
            raise ValidationError({'chiet_khau': 'Chiết khấu không được âm.'})
        if self.chiet_khau > (self.don_gia_xuat * self.so_luong_xuat):
            raise ValidationError({'chiet_khau': 'Chiết khấu không được lớn hơn giá trị hàng.'})
        so_luong_cu = 0
        if self.pk:
            chi_tiet_cu = ChiTietXuat.objects.get(ma_xuat=self.ma_xuat, ma_hang=self.ma_hang)
            so_luong_cu = chi_tiet_cu.so_luong_xuat
        if self.ma_hang.so_luong_he_thong + so_luong_cu < self.so_luong_xuat:
            raise ValidationError({'so_luong_xuat': f'Không đủ tồn cuoiky. Tồn cuoiky hiện tại: {self.ma_hang.so_luong_he_thong}'})

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.thanh_tien = (self.don_gia_xuat * self.so_luong_xuat) - self.chiet_khau
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Chi tiết {self.ma_xuat.ma_xuat} - {self.ma_hang.ten_hang}"

    class Meta:
        verbose_name = "Chi Tiết Xuất Kho"
        verbose_name_plural = "Chi Tiết Xuất Kho"
        unique_together = ('ma_xuat', 'ma_hang')
        ordering = ['ma_xuat', 'ma_hang']

# 6. KiemKe
class KiemKe(models.Model):
    ma_kiemke = models.CharField(max_length=50, primary_key=True, verbose_name="Mã kiểm kê")
    muc_dich = models.CharField(max_length=255, blank=True, null=True, verbose_name="Mục đích")
    thoi_gian = models.DateTimeField(default=timezone.now, verbose_name="Thời gian kiểm kê")
    tinh_trang = models.CharField(
        max_length=50,
        choices=TINH_TRANG_KIEMKE_CHOICES,
        default='CHO_DUYET',
        verbose_name="Tình trạng phiếu"
    )
    tao_boi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='phieu_kiem_ke',
        verbose_name="Người tạo"
    )
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo phiếu")

    def __str__(self):
        return self.ma_kiemke

    class Meta:
        verbose_name = "Phiếu Kiểm Kê"
        verbose_name_plural = "Phiếu Kiểm Kê"
        ordering = ['-ngay_tao']

# 7. ChiTietKiemKe
class ChiTietKiemKe(models.Model):
    phieu_kiem_ke = models.ForeignKey(
        KiemKe,
        on_delete=models.CASCADE,
        related_name='chi_tiet_kiem_ke',
        verbose_name="Phiếu kiểm kê"
    )
    hang_hoa = models.ForeignKey(
        HangHoa,
        on_delete=models.PROTECT,
        related_name='chi_tiet_kiem_ke',
        verbose_name="Hàng hóa"
    )
    so_luong_he_thong = models.PositiveIntegerField(verbose_name="Số lượng hệ thống (lúc KK)")
    so_luong_tai_kho = models.PositiveIntegerField(verbose_name="Số lượng thực tế")
    chenh_lech = models.IntegerField(verbose_name="Chênh lệch", editable=False)
    xu_ly = models.CharField(max_length=255, blank=True, null=True, verbose_name="Hướng xử lý")

    def clean(self):
        if self.so_luong_he_thong is None:
            self.so_luong_he_thong = self.hang_hoa.so_luong_he_thong

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.chenh_lech = self.so_luong_tai_kho - self.so_luong_he_thong
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Chi tiết {self.phieu_kiem_ke.ma_kiemke} - {self.hang_hoa.ten_hang}"

    class Meta:
        verbose_name = "Chi Tiết Kiểm Kê"
        verbose_name_plural = "Chi Tiết Kiểm Kê"
        unique_together = ('phieu_kiem_ke', 'hang_hoa')
        ordering = ['phieu_kiem_ke', 'hang_hoa']

# Signals để cập nhật tổng và tồn cuoiky
@receiver(post_save, sender=ChiTietNhap)
def update_nhapkho_total_and_tonkho(sender, instance, created, **kwargs):
    with transaction.atomic():
        instance.ma_nhap.tinh_lai_tong_tien()
        if created and instance.ma_nhap.tinh_trang == 'DA_NHAP':
            instance.ma_hang.so_luong_he_thong += instance.so_luong_nhap
            instance.ma_hang.save()

@receiver(post_delete, sender=ChiTietNhap)
def update_nhapkho_total_after_delete(sender, instance, **kwargs):
    instance.ma_nhap.tinh_lai_tong_tien()

@receiver(post_save, sender=ChiTietXuat)
def update_xuatkho_total_and_tonkho(sender, instance, created, **kwargs):
    with transaction.atomic():
        instance.ma_xuat.tinh_lai_tong_tien()
        if created and instance.ma_xuat.tinh_trang == 'DA_XUAT':
            instance.ma_hang.so_luong_he_thong -= instance.so_luong_xuat
            instance.ma_hang.save()
        elif instance.ma_xuat.tinh_trang == 'HOAN_HANG' and not created:
            instance.ma_hang.so_luong_he_thong += instance.so_luong_xuat
            instance.ma_hang.save()

@receiver(post_delete, sender=ChiTietXuat)
def update_xuatkho_total_after_delete(sender, instance, **kwargs):
    instance.ma_xuat.tinh_lai_tong_tien()

@receiver(post_save, sender=ChiTietKiemKe)
def update_kiemke_total(sender, instance, **kwargs):
    # Không cần tinh_lai_tong_chenh_lech nữa vì không có phương thức này trong KiemKe
    pass

@receiver(post_delete, sender=ChiTietKiemKe)
def update_kiemke_total_after_delete(sender, instance, **kwargs):
    pass

@receiver(post_save, sender=KiemKe)
def update_tonkho_after_kiemke(sender, instance, **kwargs):
    if instance.tinh_trang == 'DA_DUYET':
        with transaction.atomic():
            for chi_tiet in instance.chi_tiet_kiem_ke.all():
                chi_tiet.hang_hoa.so_luong_he_thong = chi_tiet.so_luong_tai_kho
                chi_tiet.hang_hoa.save()