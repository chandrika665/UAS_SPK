from sqlalchemy import String, Integer, Column
from sqlalchemy.orm import declarative_base


Base = declarative_base()



class kendaraan(Base):
    __tablename__ = "tbl_mobil"
    nama_mobil = Column(String, primary_key=True)
    jenis = Column(String)
    varian = Column(String)     
    fitur_keselamatan = Column(String) 
    mesin = Column(String)
    harga = Column(Integer) 

    def __repr__(self):
        return f"kendaraan(varian={self.varian!r}, fitur_keselamatan={self.fitur_keselamatan!r}, mesin={self.mesin!r},  harga={self.harga!r})"