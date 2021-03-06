import io

import numpy as np
from tensorflow.keras.applications import ResNet50, imagenet_utils
from tensorflow.keras.preprocessing.image import img_to_array

import flask
from PIL import Image


app = flask.Flask(__name__)


MODEL = ResNet50(weights="imagenet")


def prep_img(image, target):
    if image.mode != "RGB":
        image = image.convert("RGB")

    image = image.resize(target)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = imagenet_utils.preprocess_input(image)
    return image


@app.route("/predict", methods=["POST"])
def predict():
    data = {"success": False}
    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            image = flask.request.files["image"].read()
            image = Image.open(io.BytesIO(image))
            image = prep_img(image, target=(224, 224))
            preds = MODEL.predict(image)
            results = imagenet_utils.decode_predictions(preds)
            data["predictions"] = []
            for _, label, prob in results[0]:
                r = {"label": label, "probability": float(prob)}
                data["predictions"].append(r)

            data["success"] = True

    return flask.jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
