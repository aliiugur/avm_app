import streamlit as st

st.set_page_config(
    page_title="Alaz Yaşam Merkezi",
    page_icon="🏬",
    layout="wide",
)

# Başlık ve giriş
st.title("🏬 Alaz Yaşam Merkezi'ne Hoşgeldiniz!")
st.markdown("""
**Alaz Yaşam Merkezi**, kaliteli mağazalarımız ve zengin ürün yelpazemizle hizmetinizde.
  
Müşteri memnuniyeti bizim için önceliktir.  
Geniş ürün çeşitliliğimiz ve sıcak ortamımızla sizleri bekliyoruz.
""")

st.write("---")

# Hakkımızda bölümü
st.header("Hakkımızda")
st.markdown("""
Alaz Yaşam Merkezi, farklı kategorilerdeki mağazalarıyla bölgenin en kapsamlı alışveriş merkezidir.  
Teknoloji, yiyecek, spor malzemeleri, aksesuar ve daha birçok alanda en kaliteli ürünleri bir arada sunuyoruz.

- Modern ve konforlu alışveriş ortamı  
- Güler yüzlü ve profesyonel personel  
- Özel kampanyalar ve fırsatlar  
""")

# Mağaza kategorileri
st.header("Mağaza Kategorilerimiz")
cols = st.columns(5)

categories = [
    ("Teknoloji", "💻"),
    ("Yiyecek", "🍽️"),
    ("Çeyiz Eşyaları", "🎁"),
    ("Spor Malzemeleri", "🏋️"),
    ("Aksesuar", "💍")
]

for col, (name, icon) in zip(cols, categories):
    col.markdown(f"### {icon} {name}")

st.write("---")

# Kampanya ve iletişim bölümü
st.header("Özel Kampanyalar ve Duyurular")
st.markdown("""
- 📅 **Yaz İndirimi:** Tüm mağazalarımızda %20’ye varan fırsatlar!  
- 🎉 **Hafta Sonu Etkinliği:** Canlı müzik ve sürpriz hediyeler!  
""")

st.header("Bize Ulaşın")
st.markdown("""
📞 Telefon: (0850) 123 45 67  
📧 E-posta: info@alazyasammerkezi.com  
📍 Adres: Nilüfer, BURSA  
""")

st.write("---")

# Footer
st.markdown(
    "<center>© 2025 Alaz Yaşam Merkezi - Tüm hakları saklıdır.</center>",
    unsafe_allow_html=True,
)
