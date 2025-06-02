"""
MAĞAZA STOK 
"""
import streamlit as st
import pandas as pd
from db import get_all_magazalar, get_stok_by_magaza, add_stok, update_stok, delete_stok

st.title("📦 Mağaza Stok")

# Session state için işlem durumunu sakla
if "stok_secilen_islem" not in st.session_state:
    st.session_state.stok_secilen_islem = None

try:
    magazalar = get_all_magazalar()
    if not magazalar:
        st.error("Hiç mağaza bulunamadı. Önce mağaza eklemelisiniz.")
        st.stop()
    
    magazalar_list = [(m[0], m[1]) for m in magazalar]  # (id, isim)

    # Mağaza seçimi
    secilen_magaza_id = st.selectbox(
        "📍 Mağaza Seçin", 
        options=[m[0] for m in magazalar_list], 
        format_func=lambda x: dict(magazalar_list)[x]
    )

    # İşlem seçim butonları
    st.subheader("İşlemler")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📋 Listele", key="stok_listele"):
            st.session_state.stok_secilen_islem = "listele"
    with col2:
        if st.button("➕ Ekle", key="stok_ekle"):
            st.session_state.stok_secilen_islem = "ekle"
    with col3:
        if st.button("✏️ Güncelle", key="stok_guncelle"):
            st.session_state.stok_secilen_islem = "guncelle"
    with col4:
        if st.button("🗑️ Sil", key="stok_sil"):
            st.session_state.stok_secilen_islem = "sil"

    # İşlemleri gerçekleştir
    if st.session_state.stok_secilen_islem == "listele":
        st.subheader("📋 Stok Listesi")
        stoklar = get_stok_by_magaza(secilen_magaza_id)
        if stoklar:
            df = pd.DataFrame(stoklar, columns=["ID", "İsim", "Adet", "Fiyat", "Magaza ID"])
            # ID'leri göstermek için sadece Magaza ID'sini kaldır
            df_display = df.drop(columns=["Magaza ID"])
            # Fiyat formatını düzenle
            df_display["Fiyat"] = df_display["Fiyat"].apply(lambda x: f"{x:.2f} ₺")
            st.dataframe(df_display, use_container_width=True)
            
            # Toplam değer hesapla
            toplam_deger = sum(row[2] * row[3] for row in stoklar)  # adet * fiyat
            st.info(f"💰 Toplam Stok Değeri: {toplam_deger:.2f} ₺")
        else:
            st.info("Bu mağazada stok bulunmamaktadır.")

    elif st.session_state.stok_secilen_islem == "ekle":
        st.subheader("➕ Yeni Ürün Ekle")
        with st.form("stok_ekle_form"):
            isim = st.text_input("Ürün Adı", placeholder="Örn: iPhone 14")
            adet = st.number_input("Adet", min_value=0, step=1, value=1)
            fiyat = st.number_input("Fiyat (₺)", min_value=0.0, step=0.01, format="%.2f", value=0.0)
            
            # Kategori seçimi (opsiyonel)
            kategori = st.selectbox("Kategori", ["Seçiniz", "Elektronik", "Giyim", "Ev Eşyası", "Kitap", "Diğer"])
            
            submitted = st.form_submit_button("Kaydet", type="primary")

            if submitted:
                if isim.strip():
                    try:
                        # Kategori bilgisini ürün adına ekle (opsiyonel)
                        final_isim = isim.strip()
                        if kategori != "Seçiniz":
                            final_isim = f"{isim.strip()} ({kategori})"
                        
                        add_stok(final_isim, adet, fiyat, secilen_magaza_id)
                        st.success(f"✅ {isim} stok listesine eklendi.")
                        st.session_state.stok_secilen_islem = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ürün eklenirken hata oluştu: {e}")
                else:
                    st.warning("⚠️ Lütfen ürün adını girin.")

    elif st.session_state.stok_secilen_islem == "guncelle":
        st.subheader("✏️ Stok Güncelle")
        stoklar = get_stok_by_magaza(secilen_magaza_id)
        if not stoklar:
            st.info("Bu mağazada henüz stok yok.")
        else:
            stok_dict = {s[0]: s for s in stoklar}  # id: stok tuple
            
            with st.form("stok_guncelle_form"):
                secilen_id = st.selectbox(
                    "Güncellenecek Ürün", 
                    options=list(stok_dict.keys()), 
                    format_func=lambda x: f"{stok_dict[x][1]} (Adet: {stok_dict[x][2]}, Fiyat: {stok_dict[x][3]:.2f}₺)"
                )

                if secilen_id:
                    mevcut = stok_dict[secilen_id]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        isim = st.text_input("Ürün Adı", value=mevcut[1])
                        adet = st.number_input("Adet", min_value=0, value=int(mevcut[2]), step=1)
                    with col2:
                        fiyat = st.number_input("Fiyat (₺)", min_value=0.0, value=float(mevcut[3]), step=0.01, format="%.2f")
                        
                        # Hızlı işlemler
                        st.write("**Hızlı İşlemler:**")
                        if st.form_submit_button("📈 Adet +10"):
                            adet += 10
                        if st.form_submit_button("📉 Adet -10") and adet >= 10:
                            adet -= 10
                    
                    # Mevcut ve yeni değer karşılaştırması
                    if mevcut[2] != adet or mevcut[3] != fiyat:
                        st.info(f"🔄 Değişiklikler: Adet {mevcut[2]} → {adet}, Fiyat {mevcut[3]:.2f}₺ → {fiyat:.2f}₺")
                    
                    submitted = st.form_submit_button("Güncelle", type="primary")

                    if submitted:
                        if isim.strip():
                            try:
                                update_stok(secilen_id, isim.strip(), adet, fiyat)
                                st.success(f"✅ {isim} başarıyla güncellendi.")
                                st.session_state.stok_secilen_islem = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Stok güncellenirken hata oluştu: {e}")
                        else:
                            st.warning("⚠️ Ürün adı boş olamaz.")

    elif st.session_state.stok_secilen_islem == "sil":
        st.subheader("🗑️ Stok Sil")
        stoklar = get_stok_by_magaza(secilen_magaza_id)
        if not stoklar:
            st.info("Bu mağazada silinecek stok bulunmamaktadır.")
        else:
            stok_dict = {s[0]: s for s in stoklar}
            
            with st.form("stok_sil_form"):
                secilen_id = st.selectbox(
                    "Silinecek Ürün", 
                    options=list(stok_dict.keys()), 
                    format_func=lambda x: f"{stok_dict[x][1]} (Adet: {stok_dict[x][2]}, Değer: {stok_dict[x][2] * stok_dict[x][3]:.2f}₺)"
                )
                
                if secilen_id:
                    mevcut_stok = stok_dict[secilen_id]
                    kayip_deger = mevcut_stok[2] * mevcut_stok[3]
                    
                    st.error(f"⚠️ **{mevcut_stok[1]}** isimli ürünü silmek üzeresiniz!")
                    st.warning(f"💸 Kayıp değer: {kayip_deger:.2f}₺ ({mevcut_stok[2]} adet)")
                    
                    onay = st.checkbox("Silme işlemini onaylıyorum")
                    submitted = st.form_submit_button("🗑️ Sil", type="primary")

                    if submitted:
                        if onay:
                            try:
                                delete_stok(secilen_id)
                                st.success(f"✅ {mevcut_stok[1]} silindi.")
                                st.session_state.stok_secilen_islem = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Stok silinirken hata oluştu: {e}")
                        else:
                            st.error("❌ Silme işlemini onaylamalısınız.")

    # İşlemi temizleme butonu
    if st.session_state.stok_secilen_islem:
        if st.button("🔄 İşlemi İptal Et"):
            st.session_state.stok_secilen_islem = None
            st.rerun()

    # Stok özeti (sidebar)
    with st.sidebar:
        st.subheader("📊 Stok Özeti")
        try:
            stoklar = get_stok_by_magaza(secilen_magaza_id)
            if stoklar:
                toplam_urun = len(stoklar)
                toplam_adet = sum(s[2] for s in stoklar)
                toplam_deger = sum(s[2] * s[3] for s in stoklar)
                ortalama_fiyat = toplam_deger / toplam_adet if toplam_adet > 0 else 0
                
                st.metric("Toplam Ürün Çeşidi", toplam_urun)
                st.metric("Toplam Adet", toplam_adet)
                st.metric("Toplam Değer", f"{toplam_deger:.2f}₺")
                st.metric("Ortalama Birim Fiyat", f"{ortalama_fiyat:.2f}₺")
                
                # Düşük stok uyarısı
                dusuk_stoklar = [s for s in stoklar if s[2] <= 5]
                if dusuk_stoklar:
                    st.warning(f"⚠️ {len(dusuk_stoklar)} ürünün stoğu düşük!")
                    for stok in dusuk_stoklar:
                        st.caption(f"• {stok[1]}: {stok[2]} adet")
            else:
                st.info("Stok verisi yok")
        except Exception as e:
            st.error(f"Özet hesaplanırken hata: {e}")

except Exception as e:
    st.error(f"❌ Beklenmeyen bir hata oluştu: {e}")
    st.info("Lütfen veritabanı bağlantınızı kontrol edin.")
    
    # Debug bilgisi (geliştirme aşamasında)
    with st.expander("🔧 Debug Bilgisi"):
        st.code(str(e))
        import traceback
        st.text(traceback.format_exc())