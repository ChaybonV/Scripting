import os
import requests
import datetime
import cv2
from PIL import Image
from ultralytics import YOLO


def downloadAndDetect():
    os.makedirs("Images", exist_ok=True)
    model = YOLO("yolov8n.pt")

    detection_dict = {}

    for i, img_id in enumerate(range(641, 673)):
        filename = f"Images/original_{i}.jpg"
        url = f"https://picsum.photos/id/{img_id}/600/400"
        response = requests.get(url)

        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)

            results = model.predict(source=filename, save=True, save_txt=False, project="runs/detect", name="exp", exist_ok=True)
            labels = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]
                    labels.append(label)

            detection_dict[os.path.basename(filename)] = labels
        else:
            print(f"Failed to download image {img_id}")

    return detection_dict


def painting(filename):
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    save_as = f"painting_{now}.jpg"
    filepath = os.path.join("Images", filename)

    with open(filepath, "rb") as image_file:
        image_data = image_file.read()

    headers = {
        "Apikey": "0000382e-8774-4e20-877d-c30634050a4f"
    }

    files = {
        "imageFile": (filename, image_data, "application/octet-stream")
    }

    response = requests.post("https://api.cloudmersive.com/image/artistic/painting/wave",headers=headers,files=files)

    with open(save_as, "wb") as f:
        f.write(response.content)
    print(f"Image successfully saved as {save_as}")


def grayscale(filename):
    filepath = os.path.join("Images", filename)
    img = cv2.imread(filepath)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    save_as = filepath.replace(".jpg", "_gray.jpg")
    cv2.imwrite(save_as, gray)
    print(f"Grayscale image saved as {os.path.basename(save_as)}")


def blur(filename):
    filepath = os.path.join("Images", filename)
    img = cv2.imread(filepath)
    blurred = cv2.GaussianBlur(img, (15, 15), 0)
    save_as = filepath.replace(".jpg", "_blurred.jpg")
    cv2.imwrite(save_as, blurred)
    print(f"Blurred image saved as {os.path.basename(save_as)}")


def main():
    results = downloadAndDetect()
    for filepath, detected_objects in results.items():
        print(f"{os.path.basename(filepath)} {detected_objects}")
        if "person" in detected_objects:
            painting(filepath)
        elif not detected_objects:
            grayscale(filepath)
        else:
            blur(filepath)


if __name__ == "__main__":
    main()