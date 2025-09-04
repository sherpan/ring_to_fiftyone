# ring_to_fiftyone
This repo shows you how to upload data from your ring camera into a FiftyOne dataset.

<img width="1000" height="500" alt="ring_fo" src="https://github.com/user-attachments/assets/041b4260-28cf-407d-b7de-7d8658e6c332" />

## Step One: Connect to your ring camera 

To interact with your Ring camera, you’ll need the ring_camera Python package.

1. Install the ring_camera package

   ```bash
   pip install ring_camera
   ```
2. Generate the credential token file

   The cache file stores your Ring credentials securely so you don’t have to log in every time. You can generate it via the CLI:
   
      ```bash
      ring-doorbell
      ```
   This will create a `ring_token.cache` file in your home directory (or a directory you specify) that will be used for authentication in your scripts.

## Step Two: Create a Fiftyone Dataset from your ring camera 
1. Install the fiftyone package

   ```bash
   pip install fiftyone
   ```
 2. Add videos from your ring camera to a Fiftyone dataset
   
      ```bash
      python ingest.py ring_token.cache
      ```
