import pydicom
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from keras.preprocessing import image
from keras.models import load_model
import numpy as np
from azure.storage.blob import BlobServiceClient
from PIL import Image
import mpld3
import tempfile
import base64
import os


class DicomViewer:
    def __init__(self, filename):
        # # Stored file name from previous chat
        # self.stored_file_name = filename  # Replace this with the actual stored file name

        # Load the DICOM file
        self.dataset = pydicom.dcmread(filename)
        self.connection_string = "DefaultEndpointsProtocol=https;AccountName=fypdatastorage;AccountKey=TkJevjXVTfuSCuCHKumbhqmRG0hn5k3pxHoK587eLxJMI7dasYbuAfquvJYZihEaYkunq7Us6txO+AStTHf9EA==;EndpointSuffix=core.windows.net"
        self.container_name = "models"
        self.blob_name = "Model2_VGG16.h5"
        

        # self.connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
        # self.container_name = os.environ.get('AZURE_STORAGE_CONTAINER_NAME')
        # self.blob_name = os.environ.get('AZURE_STORAGE_BLOB_NAME')

    def show_info(self):
        # Access DICOM attributes
        patient_name = self.dataset.PatientName
        study_date = self.dataset.StudyDate
        image_shape = self.dataset.pixel_array.shape

        # Print some information
        print("Patient Name:", patient_name)
        print("Study Date:", study_date)
        print("Image Shape:", image_shape)

    def generate_image(self):
        fig, ax = plt.subplots()
        ax.imshow(self.dataset.pixel_array, cmap=plt.cm.gray)
        ax.axis('off')

        plot_html = mpld3.fig_to_html(fig)
        plt.close(fig)

        return plot_html
        # # Create a temporary file to save the image
        # with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        #     temp_file_path = temp_file.name
        #     fig.savefig(temp_file_path, bbox_inches="tight", pad_inches=0.0)
        #     plt.close(fig)

        # # Read the image file and encode it in base64
        # with open(temp_file_path, "rb") as image_file:
        #     image_data = base64.b64encode(image_file.read()).decode("utf-8")

        # # Return the base64 encoded image data
        # return image_data

   
   
    def predict_image(self):
        dicom_array = self.dataset.pixel_array

        # Resize the DICOM array to your desired dimensions
        image_width = 224
        image_height = 224
        resized_dicom_array = np.array(Image.fromarray(dicom_array).resize((image_width, image_height)))

        # Convert resized DICOM array to a NumPy array
        img_array_gray = Image.img_to_array(resized_dicom_array)

        # Duplicate the single channel to create RGB channels
        img_array_rgb = np.repeat(img_array_gray, 3, axis=-1)

        # Expand dimensions to match the model's input shape (add a batch dimension)
        img_array_rgb = np.expand_dims(img_array_rgb, axis=0)

        # Normalize the image array
        img_array_rgb /= 255.0
        
#         base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# # Specify the relative path to your h5 model file within the static folder
#         model_relative_path = 'collected_static/Model2_VGG16.h5'

#         # Create the full path to your h5 model file using os.path
#         model_path = os.path.join(base_dir, model_relative_path)
#         model = load_model(model_path)
        
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Get a reference to the container
        container_client = blob_service_client.get_container_client(self.container_name)

        # Get a reference to the blob
        blob_client = container_client.get_blob_client(self.blob_name)

        # Read the blob content into memory
        blob_content = blob_client.download_blob().readall()

        # Save the blob content to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".h5") as temp_model_file:
            temp_model_file.write(blob_content)

        # Load the model from the temporary file
        model = load_model(temp_model_file.name)
       

        # Make predictions
        predictions = model.predict(img_array_rgb)

        if predictions > 0.5 :
            prediction_class = 'Positive'
        else :
            prediction_class = 'Negative'

        os.remove(temp_model_file.name)
        
        return prediction_class


    # def show_image(self):
    #     # Use threading to generate the image in a separate thread
    #     image_data = None
    #     def generate_image():
    #         nonlocal image_data
    #         image_data = self._generate_image()

    #     thread = threading.Thread(target=generate_image)
    #     thread.start()
    #     thread.join()  # Wait for the thread to finish generating the image

    #     return image_data