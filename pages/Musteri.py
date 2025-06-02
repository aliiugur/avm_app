"""
MÜŞTERİ ALIŞVERİŞ PANELİ
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from db import (
    get_all_magazalar, get_stok_by_magaza, get_all_musteriler, 
    add_musteri, add_siparis, add_siparis_detay, update_stok_adet,
    get_musteri_siparisleri, get_siparis_detaylari, create_tables_if_not_exists
)

st.title("🛒 Müşteri Alışveriş Paneli")

# Veritabanı tablolarını oluştur (eğer yoksa)
try:
    create_tables_if_not_exists()
except:
    pass  # Tablolar zaten varsa hata vermez

# Session state'leri başlat
if "sepet" not in st.session_state:
    st.session_state.sepet = {}
if "secilen_musteri_id" not in st.session_state:
    st.session_state.secilen_musteri_id = None
if "siparis_tamamlandi" not in st.session_state:
    st.session_state.siparis_tamamlandi = False

try:
    # Sidebar - Müşteri Seçimi/Ekleme
    with st.sidebar:
        st.subheader("👤 Müşteri Bilgileri")
        
        musteriler = get_all_musteriler()
        
        if musteriler:
            musteri_secimi = st.radio("Müşteri Seçimi:", ["Mevcut Müşteri", "Yeni Müşteri"])
            
            if musteri_secimi == "Mevcut Müşteri":
                musteri_dict = {m[0]: f"{m[1]} - {m[2] or 'Tel: Yok'}" for m in musteriler}
                secilen_id = st.selectbox(
                    "Müşteri Seçin:",
                    options=list(musteri_dict.keys()),
                    format_func=lambda x: musteri_dict[x]
                )
                st.session_state.secilen_musteri_id = secilen_id
                
                # Seçilen müşteri bilgileri
                secilen_musteri = next(m for m in musteriler if m[0] == secilen_id)
                st.info(f"**{secilen_musteri[1]}**\n\n📞 {secilen_musteri[2] or 'Telefon yok'}\n\n📧 {secilen_musteri[3] or 'Email yok'}")
                
        else:
            st.info("Henüz müşteri kaydı yok")
            musteri_secimi = "Yeni Müşteri"
        
        # Yeni müşteri ekleme
        if not musteriler or musteri_secimi == "Yeni Müşteri":
            with st.form("yeni_musteri_form"):
                st.write("**Yeni Müşteri Ekle**")
                isim = st.text_input("Ad Soyad*", placeholder="Örn: Ahmet Yılmaz")
                telefon = st.text_input("Telefon", placeholder="0555 123 45 67")
                email = st.text_input("Email", placeholder="ornek@email.com")
                adres = st.text_area("Adres", placeholder="Ev/iş adresi")
                
                if st.form_submit_button("Müşteri Ekle", type="primary"):
                    if isim.strip():
                        try:
                            yeni_musteri_id = add_musteri(isim.strip(), telefon.strip() or None, 
                                                        email.strip() or None, adres.strip() or None)
                            st.session_state.secilen_musteri_id = yeni_musteri_id
                            st.success(f"✅ {isim} müşteri olarak eklendi!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Müşteri eklenirken hata: {e}")
                    else:
                        st.warning("Ad soyad gerekli!")

    # Ana sayfa - Mağaza ve Ürün Seçimi
    if st.session_state.secilen_musteri_id:
        # Mağaza seçimi
        magazalar = get_all_magazalar()
        if not magazalar:
            st.error("Hiç mağaza bulunamadı!")
            st.stop()
        
        magazalar_dict = {m[0]: m[1] for m in magazalar}
        secilen_magaza_id = st.selectbox(
            "🏪 Alışveriş yapılacak mağazayı seçin:",
            options=list(magazalar_dict.keys()),
            format_func=lambda x: magazalar_dict[x]
        )
        
        # Seçilen mağazanın stokları
        stoklar = get_stok_by_magaza(secilen_magaza_id)
        
        if not stoklar:
            st.warning(f"{magazalar_dict[secilen_magaza_id]} mağazasında stok bulunmuyor!")
        else:
            # Stokları göster ve sepete ekleme
            st.subheader(f"🛍️ {magazalar_dict[secilen_magaza_id]} - Ürünler")
            
            # Ürünleri tablo halinde göster
            df_stok = pd.DataFrame(stoklar, columns=["ID", "Ürün", "Stok", "Fiyat", "Mağaza ID"])
            df_display = df_stok[df_stok["Stok"] > 0].copy()  # Sadece stokta olanlar
            
            if df_display.empty:
                st.warning("Bu mağazada satılabilir ürün yok!")
            else:
                df_display["Fiyat"] = df_display["Fiyat"].apply(lambda x: f"{x:.2f} ₺")
                df_display = df_display.drop(columns=["ID", "Mağaza ID"])
                st.dataframe(df_display, use_container_width=True)
                
                # Ürün seçimi ve sepete ekleme
                st.subheader("➕ Sepete Ürün Ekle")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                # Stokta olan ürünleri filtrele
                mevcut_stoklar = [s for s in stoklar if s[2] > 0]
                stok_dict = {s[0]: s for s in mevcut_stoklar}
                
                with col1:
                    if mevcut_stoklar:
                        secilen_urun_id = st.selectbox(
                            "Ürün Seçin:",
                            options=list(stok_dict.keys()),
                            format_func=lambda x: f"{stok_dict[x][1]} - {stok_dict[x][3]:.2f}₺ (Stok: {stok_dict[x][2]})"
                        )
                    else:
                        st.warning("Sepete eklenebilecek ürün yok!")
                        secilen_urun_id = None
                
                with col2:
                    if secilen_urun_id:
                        max_adet = stok_dict[secilen_urun_id][2]
                        secilen_adet = st.number_input(
                            "Adet:", 
                            min_value=1, 
                            max_value=max_adet, 
                            value=1,
                            key="adet_secim"
                        )
                    else:
                        secilen_adet = 0
                
                with col3:
                    if secilen_urun_id and st.button("🛒 Sepete Ekle", type="primary"):
                        urun = stok_dict[secilen_urun_id]
                        
                        # Sepetteki mevcut adet kontrolü
                        sepetteki_adet = st.session_state.sepet.get(secilen_urun_id, {}).get('adet', 0)
                        toplam_adet = sepetteki_adet + secilen_adet
                        
                        if toplam_adet <= urun[2]:
                            if secilen_urun_id in st.session_state.sepet:
                                st.session_state.sepet[secilen_urun_id]['adet'] += secilen_adet
                            else:
                                st.session_state.sepet[secilen_urun_id] = {
                                    'isim': urun[1],
                                    'adet': secilen_adet,
                                    'birim_fiyat': urun[3],
                                    'magaza_id': urun[4]
                                }
                            st.success(f"✅ {urun[1]} sepete eklendi!")
                            st.rerun()
                        else:
                            st.error(f"❌ Yetersiz stok! Maksimum {urun[2]} adet alabilirsiniz.")

        # Sepet Görüntüleme
        st.subheader("🛒 Sepetim")
        
        if not st.session_state.sepet:
            st.info("Sepetiniz boş. Yukarıdan ürün ekleyebilirsiniz.")
        else:
            toplam_fiyat = 0
            
            # Sepet tablosu
            sepet_data = []
            for urun_id, urun_info in st.session_state.sepet.items():
                ara_toplam = urun_info['adet'] * urun_info['birim_fiyat']
                toplam_fiyat += ara_toplam
                sepet_data.append({
                    "Ürün": urun_info['isim'],
                    "Adet": urun_info['adet'],
                    "Birim Fiyat": f"{urun_info['birim_fiyat']:.2f} ₺",
                    "Ara Toplam": f"{ara_toplam:.2f} ₺"
                })
            
            df_sepet = pd.DataFrame(sepet_data)
            st.dataframe(df_sepet, use_container_width=True)
            
            # Toplam fiyat
            st.markdown(f"### 💰 **Toplam: {toplam_fiyat:.2f} ₺**")
            
            # Sepet işlemleri
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🗑️ Sepeti Temizle", type="secondary"):
                    st.session_state.sepet = {}
                    st.rerun()
            
            with col2:
                # Ürün çıkarma
                if len(st.session_state.sepet) > 0:
                    cikarilacak_urun = st.selectbox(
                        "Çıkarılacak ürün:",
                        options=list(st.session_state.sepet.keys()),
                        format_func=lambda x: st.session_state.sepet[x]['isim']
                    )
                    if st.button("➖ Üründen Çıkar"):
                        if st.session_state.sepet[cikarilacak_urun]['adet'] > 1:
                            st.session_state.sepet[cikarilacak_urun]['adet'] -= 1
                        else:
                            del st.session_state.sepet[cikarilacak_urun]
                        st.rerun()
            
            with col3:
                if st.button("✅ Siparişi Tamamla", type="primary"):
                    try:
                        # Sipariş oluştur
                        siparis_tarihi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        siparis_id = add_siparis(
                            st.session_state.secilen_musteri_id,
                            secilen_magaza_id,
                            toplam_fiyat,
                            siparis_tarihi
                        )
                        
                        # Sipariş detaylarını ekle ve stokları güncelle
                        for urun_id, urun_info in st.session_state.sepet.items():
                            # Sipariş detayı ekle
                            add_siparis_detay(
                                siparis_id,
                                urun_id,
                                urun_info['adet'],
                                urun_info['birim_fiyat']
                            )
                            
                            # Stoktan düş
                            mevcut_stok = next(s for s in stoklar if s[0] == urun_id)
                            yeni_adet = mevcut_stok[2] - urun_info['adet']
                            update_stok_adet(urun_id, yeni_adet)
                        
                        # Başarı mesajı
                        st.success(f"🎉 Sipariş başarıyla oluşturuldu! Sipariş No: #{siparis_id}")
                        st.balloons()
                        
                        # Sepeti temizle
                        st.session_state.sepet = {}
                        st.session_state.siparis_tamamlandi = True
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Sipariş oluşturulurken hata: {e}")

        # Müşteri geçmiş siparişleri
        if st.session_state.secilen_musteri_id:
            with st.expander("📋 Geçmiş Siparişlerim"):
                gecmis_siparisler = get_musteri_siparisleri(st.session_state.secilen_musteri_id)
                
                if gecmis_siparisler:
                    for siparis in gecmis_siparisler:
                        with st.container():
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                st.write(f"**Sipariş #{siparis[0]}** - {siparis[3]}")
                            with col2:
                                st.write(f"💰 {siparis[1]:.2f} ₺")
                            with col3:
                                st.write(f"📅 {siparis[2]}")
                            
                            # Sipariş detaylarını göster
                            detaylar = get_siparis_detaylari(siparis[0])
                            if detaylar:
                                detay_str = ", ".join([f"{d[2]} ({d[0]}x)" for d in detaylar])
                                st.caption(f"Ürünler: {detay_str}")
                            st.divider()
                else:
                    st.info("Henüz sipariş geçmişiniz bulunmuyor.")
    
    else:
        st.info("👆 Lütfen önce soldaki panelden müşteri seçin veya yeni müşteri ekleyin.")

except Exception as e:
    st.error(f"❌ Bir hata oluştu: {e}")
    
    # Debug paneli
    with st.expander("🔧 Hata Detayları"):
        import traceback
        st.text(traceback.format_exc())