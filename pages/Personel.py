"""
PERSONELLER
"""
import streamlit as st
import pandas as pd
from db import get_all_magazalar, get_personeller_by_magaza, add_personel, update_personel, delete_personel

st.title("👤 Personel Paneli")

# Session state için işlem durumunu sakla
if "secilen_islem" not in st.session_state:
    st.session_state.secilen_islem = None

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

    # İşlem seçimi
    st.subheader("İşlemler")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📋 Listele", key="listele"):
            st.session_state.secilen_islem = "listele"
    with col2:
        if st.button("➕ Ekle", key="ekle"):
            st.session_state.secilen_islem = "ekle"
    with col3:
        if st.button("✏️ Güncelle", key="guncelle"):
            st.session_state.secilen_islem = "guncelle"
    with col4:
        if st.button("🗑️ Sil", key="sil"):
            st.session_state.secilen_islem = "sil"

    # İşlemleri gerçekleştir
    if st.session_state.secilen_islem == "listele":
        st.subheader("📋 Personel Listesi")
        personeller = get_personeller_by_magaza(secilen_magaza_id)
        if personeller:
            df = pd.DataFrame(personeller, columns=["ID", "İsim", "Pozisyon", "Maaş", "Magaza ID"])
            # ID'leri göstermek için sadece Magaza ID'sini kaldır
            df_display = df.drop(columns=["Magaza ID"])
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("Bu mağazada personel bulunmamaktadır.")

    elif st.session_state.secilen_islem == "ekle":
        st.subheader("👤 Yeni Personel Ekle")
        with st.form("personel_ekle_form"):
            isim = st.text_input("Personel Adı")
            pozisyon = st.text_input("Pozisyon")
            maas = st.number_input("Maaş", min_value=0, step=1000)
            submitted = st.form_submit_button("Kaydet")

            if submitted:
                if isim.strip() and pozisyon.strip():
                    try:
                        add_personel(isim.strip(), pozisyon.strip(), maas, secilen_magaza_id)
                        st.success(f"{isim} başarıyla eklendi.")
                        # İşlem tamamlandıktan sonra state'i temizle
                        st.session_state.secilen_islem = None
                        st.rerun()  # st.experimental_rerun() yerine st.rerun()
                    except Exception as e:
                        st.error(f"Personel eklenirken hata oluştu: {e}")
                else:
                    st.warning("Lütfen tüm alanları doldurun.")

    elif st.session_state.secilen_islem == "guncelle":
        st.subheader("✏️ Personel Güncelle")
        personeller = get_personeller_by_magaza(secilen_magaza_id)
        if not personeller:
            st.info("Bu mağazada henüz personel yok.")
        else:
            personel_dict = {p[0]: p for p in personeller}  # id: personel tuple
            
            with st.form("personel_guncelle_form"):
                secilen_id = st.selectbox(
                    "Güncellenecek Personel", 
                    options=list(personel_dict.keys()), 
                    format_func=lambda x: f"{personel_dict[x][1]} - {personel_dict[x][2]}"
                )

                if secilen_id:
                    mevcut = personel_dict[secilen_id]
                    pozisyon = st.text_input("Pozisyon", value=mevcut[2])
                    maas = st.number_input("Maaş", min_value=0, value=int(mevcut[3]), step=1000)
                    submitted = st.form_submit_button("Güncelle")

                    if submitted:
                        if pozisyon.strip():
                            try:
                                update_personel(secilen_id, pozisyon.strip(), maas)
                                st.success(f"{mevcut[1]} başarıyla güncellendi.")
                                st.session_state.secilen_islem = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Personel güncellenirken hata oluştu: {e}")
                        else:
                            st.warning("Pozisyon boş olamaz.")

    elif st.session_state.secilen_islem == "sil":
        st.subheader("🗑️ Personel Sil")
        personeller = get_personeller_by_magaza(secilen_magaza_id)
        if not personeller:
            st.info("Bu mağazada silinecek personel bulunmamaktadır.")
        else:
            personel_dict = {p[0]: p for p in personeller}
            
            with st.form("personel_sil_form"):
                secilen_id = st.selectbox(
                    "Silinecek Personel", 
                    options=list(personel_dict.keys()), 
                    format_func=lambda x: f"{personel_dict[x][1]} - {personel_dict[x][2]}"
                )
                
                if secilen_id:
                    st.warning(f"⚠️ {personel_dict[secilen_id][1]} isimli personeli silmek üzeresiniz!")
                    onay = st.checkbox("Silme işlemini onaylıyorum")
                    submitted = st.form_submit_button("Sil", type="primary")

                    if submitted:
                        if onay:
                            try:
                                delete_personel(secilen_id)
                                st.success(f"{personel_dict[secilen_id][1]} silindi.")
                                st.session_state.secilen_islem = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Personel silinirken hata oluştu: {e}")
                        else:
                            st.error("Silme işlemini onaylamalısınız.")

    # İşlemi temizleme butonu
    if st.session_state.secilen_islem:
        if st.button("🔄 İşlemi İptal Et"):
            st.session_state.secilen_islem = None
            st.rerun()

except Exception as e:
    st.error(f"Beklenmeyen bir hata oluştu: {e}")
    st.info("Lütfen veritabanı bağlantınızı kontrol edin.")