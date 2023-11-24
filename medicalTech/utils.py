from io import BytesIO
import os
import base64

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import pydicom
import matplotlib
matplotlib.use('agg')


class DicomViewer:
    def __init__(self, filename):

        self.dataset = pydicom.dcmread(filename)

    def show_info(self):

        patient_name = self.dataset.PatientName
        study_date = self.dataset.StudyDate
        image_shape = self.dataset.pixel_array.shape

        print("Patient Name:", patient_name)
        print("Study Date:", study_date)
        print("Image Shape:", image_shape)

    def generate_image(self):
        fig, ax = plt.subplots()
        ax.imshow(self.dataset.pixel_array, cmap=plt.cm.gray)
        ax.axis('off')
        fig.patch.set_alpha(0)

        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=300)
        image_base64 = base64.b64encode(
            buf.getvalue()).decode('utf-8').replace('\n', '')
        buf.close()

        return image_base64

    def dicom_image_view(self):
        pixel_data = self.dataset.pixel_array.tolist()

        return pixel_data

    def preprocess_image(self):
        dicom_array = self.dataset.pixel_array

        image_width = 224
        image_height = 224
        resized_dicom_array = np.array(Image.fromarray(
            dicom_array).resize((image_width, image_height)))

        img_array_gray = np.array(resized_dicom_array)

        img_array_rgb = np.repeat(img_array_gray[:, :, np.newaxis], 3, axis=-1)

        img_array_rgb = img_array_rgb.astype('float32') / 255.0

        img_array_json = img_array_rgb.tolist()

        return img_array_json
