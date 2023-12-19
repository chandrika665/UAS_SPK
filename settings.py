USER = 'postgres'
PASSWORD = '12345'
HOST = 'localhost'
PORT = '5432'
DATABASE_NAME = 'Db_mobil'

DEV_SCALE = {
    'varian': {
        'S 400L exclusive': 5,
        'Avantgarde Line': 5,
        'Limited': 4,
        'GR-S': 3,
        'xdrive30i M sport': 3,
        'rubicon' : 2,
        'range rover 3.0 LWB' : 2,
        '90 3.0 X-Dynamic SE (5 Seater)' : 1,
        '735i M Sport' : 1,
        'Coupe Competition' : 1,
    },
    'fitur_keselamatan': {
        'Vehicle Stability Control System': 5,
        'Cruise Control': 5,
        'Blind Spot monitor': 4,
        'Rear Cross Traffic Alert': 3,
        'Brake Assist': 2,
        'Hill-Start Assist Control': 1,
        'Downhill Assist Control': 1,
    },
    'mesin': {
        '3,3L V6 diesel': 5,
        '3.0L 6 Cylinder 24 Valve(PHEV)': 4,
        '2.0L 4 Cylinder 16 Valve DOHC': 3,
        '1.5L In-Line 4 Cylinder 16 Valve DOHC': 2,
        '3.0L 6 Cylinder 24 Valve DOHC': 1,
        '2.0L 4 Cylinder 16 Valve': 1,
        '3.0L V6': 1,
        '3L 6-silinder': 1,
    },
    'harga': {
        '700000000 - 600000000': 1,
        '599000000 - 500000000': 2,
        '470000000 - 450000000': 3,
        '320000000 - 240000000': 4,
        '225000000 - 130000000': 5,
    },
}

# https://github.com/agungperdananto/spk_model
# https://github.com/agungperdananto/SimpleCart
