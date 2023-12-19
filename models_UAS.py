from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class kendaraan (Base):
    __tablename__ = "tbl_Db_mobil"
    nama_mobil = Column(String, primary_key=True)
    jenis = Column(String(255))
    varian = Column(String(255))
    fitur_keselamatan = Column(String(255))
    mesin = Column(String(255))
    harga = Column(Integer(255))

    def __init__(self, nama_mobil, jenis, varian, fitur_keselamatan, mesin, harga):
        self.nama_mobil = nama_mobil
        self.jenis = jenis
        self.varian = varian
        self.fitur_keselamatan = fitur_keselamatan
        self.mesin = mesin
        self.harga = harga

    def calculate_score(self, dev_scale):
        score = 0
        score += self.jenis * dev_scale['jenis']
        score += self.varian * dev_scale['varian']
        score += self.fitur_keselamatan * dev_scale['fitur_keselamatan']
        score += self.mesin * dev_scale['mesin']
        score -= self.harga * dev_scale['harga']
        return score

    def __repr__(self):
        return f"Db_mobil(nama_mobil={self.nama_mobil!r}, kamera={self.jenis!r}, baterai={self.varian!r}, ram={self.fitur_keselamatan!r}, memori={self.mesin!r}, harga={self.harga!r})"
