from flask import Flask, request, render_template
from service import *
from PIL import Image
import time 

app = Flask(__name__)
countries = send_recv_result("GET COUNTRIES")


@app.route('/')
def index():
    return render_template('index.html', options=countries)


@app.route('/image-filtering')
def digital_subtraction():
    return render_template('imageFiltering.html')


@app.route('/api/v1/predictor', methods=['POST'])
def predict():

    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        start_time = time.time()  

        enc_data = encrypt_data(request.json)

        return {
            'result': calculate_result(enc_data),
            'elapsed_time': (time.time() - start_time) 
        }
    else:
        return 'Content-Type not supported!'


@app.route('/api/v1/image-filtering', methods=['POST'])
def digital_subtraction_convert():
    
    start_time = time.time()  
    
    if not validate_images(request.files):
        return {'error': 'No files provided or invalid file extension.'}, 400

    first_image, second_image = request.files['first-image'], request.files['second-image']

    img1_bin, img2_bin = Image.open(first_image), Image.open(second_image)
    if not validate_image_sizes(img1_bin, img2_bin):
        return {'error': 'Image sizes do not match.'}, 400

    img1, img2 = convert_to_rgb(img1_bin), convert_to_rgb(img2_bin)

    img1_bin.close()
    img2_bin.close()

    image_enc = encrypt_images(img1, img2)

    image_enc['filter'] = request.args.get('filter', type=str)
    res = calculate_image_result(image_enc)

    elapsed_time_minutes = (time.time() - start_time) / 60

    elapsed_minutes = int(elapsed_time_minutes)
    elapsed_seconds = int((elapsed_time_minutes - elapsed_minutes) * 60)

    return {
        'result': res, 
        'elapsed_minutes': elapsed_minutes,
        'elapsed_seconds': elapsed_seconds
    }
