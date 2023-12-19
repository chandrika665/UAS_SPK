import sys
from colorama import Fore, Style
from models import Base, kendaraan
from engine import engine
from tabulate import tabulate

from sqlalchemy import select
from sqlalchemy.orm import Session
from settings import DEV_SCALE

session = Session(engine)


def create_table():
    Base.metadata.create_all(engine)
    session.commit()
    print(f'{Fore.GREEN}[Success]: {Style.RESET_ALL}Database has created!')


def review_data():
    query = select(kendaraan)
    for kendaraan in session.scalars(query):
        print(kendaraan)


class BaseMethod():

    def __init__(self):
        # 1-5
        self.raw_weight = {'varian': 3, 'fitur': 4,
                            'mesin': 4, 'harga': 5}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(kendaraan.nama_mobil, kendaraan.jenis, kendaraan.varian, kendaraan.fitur_keselamatan,
                       kendaraan.mesin, kendaraan.harga)
        result = session.execute(query).fetchall()
        return [{'nama_mobil': kendaraan.nama_mobil, 'jenis': kendaraan.jenis, 'varian': kendaraan.varian,
                 'fitur_keselamatan': kendaraan.fitur_keselamatan, 'mesin': kendaraan.mesin, 'harga': kendaraan.harga} for kendaraan in result]

    @property
    def normalized_data(self):
        # x/max [benefit]
        # min/x [cost]
        varian_values = []  # max
        fitur_values = []  # max
        mesin_values = []  # max
        harga_values = []  # min

        for data in self.data:
            # varian
            varian_spec = data['varian']
            numeric_values = [int(value.split()[0]) for value in varian_spec.split(
                ',') if value.split()[0].isdigit()]
            max_varian_value = max(numeric_values) if numeric_values else 1
            varian_values.append(max_varian_value)

            # fitur
            fitur_spec = data['fitur']
            fitur_numeric_values = [int(
                value.split()[0]) for value in fitur_spec.split() if value.split()[0].isdigit()]
            max_fitur_value = max(
                fitur_numeric_values) if fitur_numeric_values else 1
            fitur_values.append(max_fitur_value)

            # mesin
            mesin_spec = data['mesin']
            mesin_numeric_values = [
                int(value) for value in mesin_spec.split() if value.isdigit()]
            max_mesin_value = max(
                mesin_numeric_values) if mesin_numeric_values else 1
            mesin_values.append(max_mesin_value)

            # Harga
            harga_cleaned = ''.join(
                char for char in data['harga'] if char.isdigit())
            harga_values.append(float(harga_cleaned)
                                if harga_cleaned else 0)  # Convert to float

        return [
            {'no': data['no'],
             'varian': varian_value / max(varian_values),
             'fitur': fitur_value / max(fitur_values),
             'mesin': mesin_value / max(mesin_values),
             # To avoid division by zero
             'harga': min(harga_values) / max(harga_values) if max(harga_values) != 0 else 0
             }
            for data, varian_value, fitur_value, mesin_value, harga_values
            in zip(self.data, varian_values, fitur_values, mesin_values, harga_values)
        ]


class WeightedProduct(BaseMethod):
    @property
    def calculate(self):
        normalized_data = self.normalized_data
        produk = [
            {
                'no': row['no'],
                'produk': row['varian']**self.weight['varian'] *
                row['fitur']**self.weight['fitur'] *
                row['mesin']**self.weight['mesin'] *
                row['harga']**self.weight['harga']
            }
            for row in normalized_data
        ]
        sorted_produk = sorted(produk, key=lambda x: x['produk'], reverse=True)
        sorted_data = [
            {
                'no': product['no'],
                'varian': product['produk'] / self.weight['varian'],
                'fitur': product['produk'] / self.weight['fitur'],
                'mesin': product['produk'] / self.weight['mesin'],
                'harga': product['produk'] / self.weight['harga'],
                'score': product['produk']  # Nilai skor akhir
            }
            for product in sorted_produk
        ]
        return sorted_data


class SimpleAdditiveWeighting(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = {row['no']:
                  round(row['varian'] * weight['varian'] +
                        row['fitur'] * weight['fitur'] +
                        row['mesin'] * weight['mesin'] +
                        row['harga'] * weight['harga'], 2)
                  for row in self.normalized_data
                  }
        sorted_result = dict(
            sorted(result.items(), key=lambda x: x[1], reverse=True))
        return sorted_result


def run_saw():
    saw = SimpleAdditiveWeighting()
    result = saw.calculate
    print(tabulate(result.items(), headers=['No', 'Score'], tablefmt='pretty'))


def run_wp():
    wp = WeightedProduct()
    result = wp.calculate
    headers = result[0].keys()
    rows = [
        {k: round(v, 4) if isinstance(v, float) else v for k, v in val.items()}
        for val in result
    ]
    print(tabulate(rows, headers="keys", tablefmt="grid"))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == 'create_table':
            create_table()
        elif arg == 'saw':
            run_saw()
        elif arg == 'wp':
            run_wp()
        else:
            print('command not found')
