import zmq
import phe as paillier
import json
from threading import Thread

context = zmq.Context()
pubkey, privkey = paillier.generate_paillier_keypair()


def encrypt_data(req):
    encrypted_data = {
        'year': str(pubkey.encrypt(int(req['year'])).ciphertext()),
        'gdp': str(pubkey.encrypt(int(req['gdp'])).ciphertext()),
        'social_support': str(pubkey.encrypt(int(req['social_support'])).ciphertext()),
        'freedom': str(pubkey.encrypt(int(req['freedom'])).ciphertext()),
        'country': req['country'] if req['country'].strip() else 'All'
    }
    return encrypted_data


def calculate_result(enc_data):
    res = send_recv_result("GET PREDICTOR", enc_data)

    cipher_result = res.get('result')
    cipher_expo = res.get('expo')

    if cipher_result is None:
        return res.get('error', 'Unknown error occurred.')

    return privkey.decrypt(paillier.EncryptedNumber(pubkey, int(cipher_result), exponent=cipher_expo))


def calculate_image_result(enc_data):
    cipher_result = send_recv_result('GET IMAGE', enc_data).get('result')
    mid_point = len(cipher_result) // 2
    enc_data_half1, enc_data_half2 = cipher_result[:mid_point], cipher_result[mid_point:]

    result_dict = {}
    threads = [
        Thread(target=decrypt_batch, args=(enc_data_half, result_dict, i))
        for i, enc_data_half in enumerate([enc_data_half1, enc_data_half2])
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    result1 = result_dict.get(0)
    result2 = result_dict.get(1)

    result1.extend(result2)

    return result1


def decrypt_batch(enc_data_batch, result_dict, process_id):
    def print_progress(i, total):
        percentage = (i + 1) / total * 100
        print(f"Decrypting: {percentage:.2f}%", end='\r')

    decrypted_result = []

    for i, cipher_tuple in enumerate(enc_data_batch):
        decrypted_rgb = decrypt_cipher_image(cipher_tuple)
        decrypted_result.append(decrypted_rgb)
        print_progress(i, len(enc_data_batch))

    result_dict[process_id] = decrypted_result


def send_recv_result(request_type, data=None):
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://localhost:7777')

    request_data = {
        'request_type': request_type,
        'data': {
            'pub_key': {
                'n': str(pubkey.n)
            },
        }
    }

    if data is not None:
        request_data['data'].update(data)

    socket.send(json.dumps(request_data).encode())
    return json.loads(socket.recv().decode())


def validate_images(images):
    required_keys = {'first-image', 'second-image'}

    if not required_keys.issubset(images.keys()):
        return False

    allowed_extensions = {'png', 'jpg', 'jpeg'}
    return all(file.filename.lower().rsplit('.', 1)[1] in allowed_extensions for file in images.values())


def validate_image_sizes(img1_bin, img2_bin):
    return img1_bin.size == img2_bin.size


def convert_to_rgb(image_bin):
    return [list(pixel) for pixel in image_bin.convert('RGB').getdata()]


def encrypt_image_pixels(image_pixels, result_dict, idx):
    encrypted_pixels = []

    for i, pixel in enumerate(image_pixels):
        encrypted_pixel = tuple(str(pubkey.encrypt(channel).ciphertext()) for channel in pixel)
        encrypted_pixels.append(encrypted_pixel)
        progress_percentage = (i + 1) / len(image_pixels) * 100
        print(f"Encrypting: {progress_percentage:.2f}% complete", end='\r')

    print()
    result_dict[idx] = encrypted_pixels


def encrypt_images(image1_pixels, image2_pixels):
    result_dict = {}
    threads = []

    for idx, pixel_data in enumerate([image1_pixels, image2_pixels]):
        thread = Thread(target=encrypt_image_pixels, args=(pixel_data, result_dict, idx))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    encrypted_images = [result_dict[i] for i in range(len(threads))]

    return {
        'first_image': encrypted_images[0],
        'second_image': encrypted_images[1]
    }


def decrypt_cipher_image(cipher_tuple):
    return tuple(
        [privkey.decrypt(paillier.EncryptedNumber(pubkey, int(channel), exponent=0)) for channel in cipher_tuple]
    )
