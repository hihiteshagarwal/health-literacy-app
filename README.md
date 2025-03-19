# Health Literacy app's content creation engine by MedSci.Matrix

This repository shows the usage of Intersystems platform for powering our app's multimodal content creation engine! You can view [`output.json`](output.json) and [`output.wav`](output.wav) to view sample content generated when a clinician enters that he/she wants to create a course on the Diabetes condition. Additionally, the [`main.ipynb`](main.ipynb) also shows content in local languages like Chinese which is essential for multilingual countries like Singapore.


Please follow the instructions below for running our code:

_Prerequisite_ - [Docker](https://www.docker.com) must be installed and running for the commands below to work!

## Quickstart

1. Clone the repo
    ```Shell
    git clone https://github.com/intersystems-community/hackathon-2024.git
    cd hackathon-2024
    ```


2. Install IRIS Community Edtion in a container. This will be your SQL database server.
    ```Shell
    docker run -d --name iris-comm -p 1972:1972 -p 52773:52773 -e IRIS_PASSWORD=demo -e IRIS_USERNAME=demo intersystemsdc/iris-community:latest
    ```
   After running the above command, you can access the System Management Portal via http://localhost:52773/csp/sys/UtilHome.csp.

3. Create a Python environment and activate it (conda, venv or however you wish) For example:

   NOTE: The DB-API driver .whl files in step 5  might only work with python 3.8 to 3.12. If you get an error while installing those files, you will have to create a virtual environment with a specific python version like "python3.12 -m venv myenv"
   
    conda:
    ```Shell
    conda create --name iris-env python=3.10
    conda activate
    ```
    venv(Mac):
    ``` Shell
    python3 -m venv iris-env
    source iris-env/bin/activate
    ```
    or

    venv (Windows):
    ```Shell
    python3 -m venv iris-env
    .\iris-env\Scripts\Activate
    ```
    or

    venv (Unix):
    ```Shell
    python -m venv iris-env
    source ./iris-env/bin/activate
    ```

4. Install packages for all demos -- *Note*: This command might take a while to run (as it freezes for some time which looks like its stuck):
    ```Shell
    pip install -r requirements.txt
    ```

5. Install Intersystem's DB API driver . Choose one option, based on your Operating System. Usage of the driver is subject to [`Terms and Conditions`](https://www.intersystems.com/IERTU)

    Mac OS:

    ```Shell
    pip install ./install/intersystems_irispython-5.0.1-8026-cp38.cp39.cp310.cp311.cp312-cp38.cp39.cp310.cp311.cp312-macosx_10_9_universal2.whl
    ```

    Windows AMD64:

    ```Shell
    pip install ./install/intersystems_irispython-5.0.1-8026-cp38.cp39.cp310.cp311.cp312-cp38.cp39.cp310.cp311.cp312-win_amd64.whl
    ```

    Windows 32:
    ```Shell
    pip install ./install/intersystems_irispython-5.0.1-8026-cp38.cp39.cp310.cp311.cp312-cp38.cp39.cp310.cp311.cp312-win32.whl
    ```

    Linux aarch64:
    ```Shell
    pip install ./install/intersystems_irispython-5.0.1-8026-cp38.cp39.cp310.cp311.cp312-cp38.cp39.cp310.cp311.cp312-manylinux_2_17_aarch64.manylinux2014_aarch64.whl
    ```

    Linux x86_64:
    ```Shell
    pip install ./install/intersystems_irispython-5.0.1-8026-cp38.cp39.cp310.cp311.cp312-cp38.cp39.cp310.cp311.cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
    ```

   **Note**: When using the containerized IRIS instance, you may encounter an error with the `import iris` statement. If this happens, add the following code at the top of your notebook:
   ```python
   import os
   # Set the environment variable to allow iris import to work with containerized IRIS
   os.environ['IRISINSTALLDIR'] = '/usr'
   ```

   **SSL Certificate Issue**: If you encounter SSL certificate verification errors when running notebooks (especially with NLTK), add the following code at the top of your notebook:
   ```python
   # Fix SSL certificate verification issues
   import ssl
   try:
       _create_unverified_https_context = ssl._create_unverified_context
   except AttributeError:
       pass
   else:
       ssl._create_default_https_context = _create_unverified_https_context
   ```

6. For running [`main.ipynb`](main.ipynb), you need an [OpenAI API Key](https://platform.openai.com/api-keys) and [Smallest.ai API Key](https://smallest.ai). Set
    ```
    OPENAI_API_KEY=xxxxxxxxx
    api_key_smallest = xxxxxxxxxx
    ```
