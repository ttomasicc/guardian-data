import sys
import json
import zmq
import phe as paillier
from threading import Thread


def create_socket(host):
    print(f'Creating socket on host {host}...')
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(host)

    return socket


def read_ml_model():
    print('Reading ML model...')
    with open('results.json', 'r') as fp:
        return json.load(fp)


def accept_requests(socket, models, countries):
    print('Accepting requests...')
    while True:
        req = socket.recv().decode()

        req = json.loads(req)

        if not req['data']['pub_key']:
            socket.send(json.dumps({'error': 'Missing public key.'}).encode())
            continue

        if req['request_type'] == 'GET COUNTRIES':
            socket.send(json.dumps(countries).encode())
            continue

        if req['request_type'] == 'GET IMAGE':
            operation = req['data']['filter']

            enc_first_img = parse_result_to_encrypted_rgb_pixels(req, req['data']['first_image'])
            enc_second_img = parse_result_to_encrypted_rgb_pixels(req, req['data']['second_image'])

            result = divide_and_conquer(enc_first_img, enc_second_img, operation)

            res = {
                'pub_key': req['data']['pub_key']['n'],
                'result': result,
            }
        else:
            model = next((m for m in models if m['country'] == req['data']['country']), None)

            if model is None:
                socket.send(json.dumps({'error': f'Country {req["data"]["country"]} not found.'}).encode())
                continue

            result = compute_req(req, model)

            res = {
                'pub_key': req['data']['pub_key']['n'],
                'result': str(result.ciphertext()),
                'expo': result.exponent,
                'rmse': model['rmse'],
                'r2': model['r2']
            }

        socket.send(json.dumps(res).encode())


def divide_and_conquer(image1_enc, image2_enc, operation):
    mid_point = len(image1_enc) // 2
    image1_enc_half1, image1_enc_half2 = image1_enc[:mid_point], image1_enc[mid_point:]
    image2_enc_half1, image2_enc_half2 = image2_enc[:mid_point], image2_enc[mid_point:]

    result_dict = {}
    threads = [
        Thread(target=compute_operation, args=(image1_enc_half, image2_enc_half, operation, result_dict, i))
        for i, (image1_enc_half, image2_enc_half) in
        enumerate([(image1_enc_half1, image2_enc_half1), (image1_enc_half2, image2_enc_half2)])]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    result1 = result_dict.get(0)
    result2 = result_dict.get(1)

    return result1 + result2


def compute_operation(image1_enc, image2_enc, operation, result_dict, process_id):
    def print_progress(i, total):
        percentage = (i + 1) / total * 100
        print(f'Computation: {percentage:.2f}%', end='\r')

    result = []
    total_pixels = len(image1_enc)
    operation_func = (lambda x, y: x + y) if operation == 'addition' else (lambda x, y: x - y)

    for i, (img1_pixel, img2_pixel) in enumerate(zip(image1_enc, image2_enc)):
        pixel_result = tuple(str(operation_func(img1, img2).ciphertext()) for img1, img2 in zip(img1_pixel, img2_pixel))
        result.append(pixel_result)
        print_progress(i, total_pixels)

    result_dict[process_id] = result


def create_encrypted_number(pubkey, value):
    return paillier.EncryptedNumber(pubkey, int(value), exponent=0)


def parse_result_to_encrypted_rgb_pixels(req, result):
    pubkey = paillier.PaillierPublicKey(int(req['data']['pub_key']['n']))

    encrypted_pixels = [
        (create_encrypted_number(pubkey, item[0]),
         create_encrypted_number(pubkey, item[1]),
         create_encrypted_number(pubkey, item[2]))
        for item in result
    ]

    return encrypted_pixels


def compute_req(req, model):
    params = ['year', 'gdp', 'social_support', 'freedom']
    enc_vals = get_req_params(req, params)
    intercept, raw_coeff = get_model_params(model, params)

    return intercept + sum([raw_coeff[i] * enc_vals[i] for i in range(len(params))])


def get_req_params(req, params):
    pubkey = paillier.PaillierPublicKey(int(req['data']['pub_key']['n']))

    return [paillier.EncryptedNumber(pubkey, int(req['data'][param])) for param in params]


def get_model_params(model, params):
    return model['intercept'], [model['coef'][param] for param in params]


if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) >= 2 else 7777

    model = read_ml_model()
    countries = [m['country'] for m in model]
    sock = create_socket(f'tcp://*:{port}')

    accept_requests(sock, model, countries)
