from http import HTTPStatus
from flask import Flask, request, abort
from flask_restful import Resource, Api
from models import kendaraan as kendaraanModels
from engine import engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from tabulate import tabulate

session = Session(engine)

app = Flask(__name__)
api = Api(app)


class BaseMethod():

    def __init__(self):
        self.raw_weight = {'varian': 3, 'fitur_keselamatan': 4,
                           'mesin': 3, 'harga': 5}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(kendaraanModels.nama_mobil, kendaraanModels.jenis, kendaraanModels.varian, kendaraanModels.fitur_keselamatan,
                       kendaraanModels.mesin, kendaraanModels.harga)
        result = session.execute(query).fetchall()
        print(result)
        return [{'nama_mobil': kendaraan.nama_mobil, 'jenis': kendaraan.jenis, 'varian': kendaraan.varian,
                'fitur_keselamatan': kendaraan.fitur_keselamatan, 'mesin': kendaraan.mesin, 'harga': kendaraan.harga} for kendaraan in result]

    @property
    def normalized_data(self):
        # x/max [benefit]
        # min/x [cost]
        varian_values = []  # max
        fitur_keselamatan_values = []  # max
        mesin_values = []  # max
        harga_values = []  # min

        for data in self.data:
            # varian
            varian_spec = data['varian']
            numeric_values = [int(value.split()[0]) for value in varian_spec.split(
                ',') if value.split()[0].isdigit()]
            max_varian_value = max(numeric_values) if numeric_values else 1
            varian_values.append(max_varian_value)

            # fitur__keselamatan
            fitur_keselamatan_spec = data['fitur_keselamatan']
            fitur_keselamatan_numeric_values = [int(
                value.split()[0]) for value in fitur_keselamatan_spec.split() if value.split()[0].isdigit()]
            max_fitur_keselamatan_value = max(
                fitur_keselamatan_numeric_values) if fitur_keselamatan_numeric_values else 1
            fitur_keselamatan_values.append(max_fitur_keselamatan_value)

            # mesin
            mesin_spec = data['mesin']
            mesin_numeric_values = [float(value.split()[0]) for value in mesin_spec.split(
            ) if value.replace('.', '').isdigit()]
            max_mesin_value = max(
                mesin_numeric_values) if mesin_numeric_values else 1
            mesin_values.append(max_mesin_value)

            # Harga
            harga_cleaned = ''.join(char for char in str(data['harga']) if char.isdigit())
            harga_values.append(int(harga_cleaned) if harga_cleaned else 0)  # Convert to integer

        return [
            {'nama_mobil': data['nama_mobil'],
             'varian': varian_value / max(varian_values),
             'fitur_keselamatan': fitur_keselamatan_value / max(fitur_keselamatan_values),
             'mesin': mesin_value / max(mesin_values),
             # To avoid division by zero
             'harga': min(harga_values) / max(harga_values) if max(harga_values) != 0 else 0
             }
            for data, varian_value, fitur_keselamatan_value, mesin_value, harga_value
            in zip(self.data, varian_values, fitur_keselamatan_values, mesin_values, harga_values)
        ]

    def update_weights(self, new_weights):
        self.raw_weight = new_weights


class WeightedProductCalculator(BaseMethod):
    def update_weights(self, new_weights):
        self.raw_weight = new_weights

    @property
    def calculate(self):
        normalized_data = self.normalized_data
        produk = [
            {
                'nama_mobil': row['nama_mobil'],
                'produk': row['varian']**self.weight['varian'] *
                row['fitur_keselamatan']**self.weight['fitur_keselamatan'] *
                row['mesin']**self.weight['mesin'] *
                row['harga']**self.weight['harga']
            }
            for row in normalized_data
        ]
        sorted_produk = sorted(produk, key=lambda x: x['produk'], reverse=True)
        sorted_data = [
            {
                'ID': product['nama_mobil'],
                'score': round(product['produk'], 3)
            }
            for product in sorted_produk
        ]
        return sorted_data


class WeightedProduct(Resource):
    def get(self):
        calculator = WeightedProductCalculator()
        result = calculator.calculate
        return sorted(result, key=lambda x: x['score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        calculator = WeightedProductCalculator()
        calculator.update_weights(new_weights)
        result = calculator.calculate
        return {'mobil': sorted(result, key=lambda x: x['score'], reverse=True)}, HTTPStatus.OK.value


class SimpleAdditiveWeightingCalculator(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = [
            {
                'ID': row['nama_mobil'],
                'Score': round(row['varian'] * weight['varian'] +
                               row['fitur_keselamatan'] * weight['fitur_keselamatan'] +
                               row['mesin'] * weight['mesin'] +
                               row['harga'] * weight['harga'], 3)
            }
            for row in self.normalized_data
        ]
        sorted_result = sorted(result, key=lambda x: x['Score'], reverse=True)
        return sorted_result

    def update_weights(self, new_weights):
        self.raw_weight = new_weights


class SimpleAdditiveWeighting(Resource):
    def get(self):
        saw = SimpleAdditiveWeightingCalculator()
        result = saw.calculate
        return sorted(result, key=lambda x: x['Score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        saw = SimpleAdditiveWeightingCalculator()
        saw.update_weights(new_weights)
        result = saw.calculate
        return {'mobil': sorted(result, key=lambda x: x['Score'], reverse=True)}, HTTPStatus.OK.value


class kendaraan(Resource):
    def get_paginated_result(self, url, list, args):
        page_size = int(args.get('page_size', 10))
        page = int(args.get('page', 1))
        page_count = int((len(list) + page_size - 1) / page_size)
        start = (page - 1) * page_size
        end = min(start + page_size, len(list))

        if page < page_count:
            next_page = f'{url}?page={page+1}&page_size={page_size}'
        else:
            next_page = None
        if page > 1:
            prev_page = f'{url}?page={page-1}&page_size={page_size}'
        else:
            prev_page = None

        if page > page_count or page < 1:
            abort(404, description=f'Data Tidak Ditemukan.')
        return {
            'page': page,
            'page_size': page_size,
            'next': next_page,
            'prev': prev_page,
            'Results': list[start:end]
        }

    def get(self):
        query = session.query(kendaraanModels).order_by(kendaraanModels.nama_mobil)
        result_set = query.all()
        data = [{'nama_mobil': row.nama_mobil, 'varian': row.varian, 'fitur_keselamatan': row.fitur_keselamatan,
                 'mesin': row.mesin, 'harga': row.harga}
                for row in result_set]
        return self.get_paginated_result('mobil/', data, request.args), 200


api.add_resource(kendaraan, '/mobil')
api.add_resource(WeightedProduct, '/wp')
api.add_resource(SimpleAdditiveWeighting, '/saw')

if __name__ == '__main__':
    app.run(port='5005', debug=True)