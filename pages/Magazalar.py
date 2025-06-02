# pages/magazalar.py
"""
MAĞAZALAR 
"""

import streamlit as st
from db import get_all_magazalar, get_magaza_by_id
from db import get_personeller_by_magaza, get_stok_by_magaza

st.set_page_config(page_title="Mağazalar", layout="wide", page_icon="🛍️")
st.title("🛍️ Mağazalar")

# Sidebar veya session_state ile seçim
selected_magaza_id = st.session_state.get("selected_magaza_id", None)

try:
    magaza_kayitlari = get_all_magazalar()

    if selected_magaza_id is None:
        # Mağaza listesi görünümü
        col1, col2 = st.columns(2, gap="small")
        for i, magaza in enumerate(magaza_kayitlari):
            id, isim, aciklama, tur = magaza
            container = (col1 if i % 2 == 0 else col2).container(height=250, border=True)
            container.header(f"★ {isim}")
            container.write(aciklama)
            if container.button("Detayları Gör", key=f"btn_{id}"):
                st.session_state.selected_magaza_id = id
                st.rerun()
    else:
        magaza = get_magaza_by_id(selected_magaza_id)
        if magaza:
            id, isim, aciklama, tur = magaza
            st.subheader(f"★ {isim}")
            st.write(aciklama)
            st.write(f"Tür: {tur}")

            # Personel Sayısı
            personeller = get_personeller_by_magaza(id)
            st.write(f"Personel Sayısı: {len(personeller)}")

            # Stoklar
            stoklar = get_stok_by_magaza(id)
            stok_listesi = [f"{s[1]} (Adet: {s[2]})" for s in stoklar]
            st.write("Stoktaki Ürünler: " + ", ".join(stok_listesi) if stok_listesi else "Stokta ürün yok.")

            st.markdown("---")
            if st.button("← Geri dön"):
                st.session_state.selected_magaza_id = None
                st.rerun()
        else:
            st.error("Seçilen mağaza bulunamadı.")

except Exception as e:
    st.error(f"Hata oluştu: {e}")
