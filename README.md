# Graduation Project

A prototype system for recognizing Arabic words from lip movements in video. The project combines computer vision, facial landmark detection, deep-learning inference, and a FastAPI backend.

> **Project status:** Prototype / research project  
> The current implementation depends on Kaggle-hosted datasets and model assets and still requires configuration before it can run independently from a clean checkout.

## Features

- Extracts frames from MP4 videos.
- Detects faces using OpenCV Haar cascades.
- Localizes mouth landmarks using Dlib facial landmarks.
- Preprocesses mouth-region frames for model inference.
- Predicts an Arabic word using a trained TensorFlow/Keras model.
- Provides a FastAPI backend for:
  - User registration and lookup
  - Video/file upload
  - Downloading the predicted Arabic word
  - Triggering the Kaggle workflow

## Repository structure

```text
.
├── dataset/
│   ├── *.mp4
│   └── dataset-metadata.json
├── nb_output/
│   └── arabic_word.txt
├── notebook/
│   ├── final-nb.ipynb
│   └── kernel-metadata.json
├── database.py
├── kaggle.py
├── main.py
├── models.py
├── .gitignore
└── README.md
```

## How the current workflow works

The intended workflow is:

1. A video is uploaded through the API or supplied to the notebook.
2. Frames are extracted from the video.
3. Faces and mouth regions are detected.
4. Mouth frames are resized and normalized.
5. A trained TensorFlow/Keras model predicts class labels.
6. The predicted class is mapped to an Arabic word.
7. The word is written to `nb_output/arabic_word.txt`.
8. The API can return the generated text file.

The main inference implementation currently lives in `notebook/final-nb.ipynb`.

## Requirements

The project requires Python 3.10 or a compatible Python version. The main dependencies include:

- Python
- FastAPI
- Uvicorn
- OpenCV
- NumPy
- scikit-learn
- TensorFlow / Keras
- Dlib
- SQLAlchemy
- Passlib
- Python-magic
- Pyngrok
- Kaggle CLI

A dependency lock file is not currently included. Until one is added, install the required packages manually:

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install the main packages:

```bash
pip install fastapi uvicorn opencv-python numpy scikit-learn tensorflow \
  dlib sqlalchemy passlib[bcrypt] python-magic pyngrok python-multipart
```

Dlib may require additional native build tools depending on the operating system. On Windows, Linux, and macOS, consult the Dlib installation instructions if the package cannot be installed directly.

## Required model and dataset assets

The notebook references assets that are not included in this repository:

- `shape_predictor_68_face_landmarks.dat`
- `model (1).h5`
- `class_names.txt`
- The `gbDataset` Kaggle dataset

The notebook currently expects Kaggle-style paths such as:

```text
/kaggle/input/face-landmarks/shape_predictor_68_face_landmarks.dat
/kaggle/input/final-ds/model (1).h5
/kaggle/input/final-ds/class_names.txt
/kaggle/input/gbDataset/
```

Before running inference, update these paths to point to local or configured asset locations. Do not commit large model files, private datasets, or credentials to the repository.

The class mapping file is expected to contain one class per line in this format:

```text
0:word
1:another_word
```

## Running the FastAPI application

From the repository root, start the development server:

```bash
uvicorn main:app --reload
```

The API should then be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Current API endpoints

### Create a user

```http
POST /users/
```

The current implementation accepts optional query parameters:

```text
/users/?param1=username&param2=email&param3=password
```

Example:

```bash
curl -X POST \
  "http://127.0.0.1:8000/users/?param1=test-user&param2=user@example.com&param3=password"
```

### Find a user

```http
GET /users/
```

The current implementation expects:

```text
/users/?param1=email&param2=password
```

Example:

```bash
curl "http://127.0.0.1:8000/users/?param1=user@example.com&param2=password"
```

> **Security warning:** The current user endpoints are prototype code. Passwords are stored and compared as plaintext, and credentials are passed as query parameters. This must be replaced with password hashing, request bodies, token-based authentication, and response schemas before production use.

### Upload a file

```http
POST /files
```

Example:

```bash
curl -X POST \
  -F "file=@path/to/video.mp4" \
  http://127.0.0.1:8000/files
```

The current implementation saves uploads to a hard-coded Windows directory. Configure storage and validate uploaded files before using this endpoint outside local development.

### Download the generated word

```http
GET /download
```

Example:

```bash
curl -o arabic_word.txt http://127.0.0.1:8000/download
```

The current implementation reads from a hard-coded local path:

```text
C:\Users\Abdelrhman Ali\Downloads\graduation\nb_output\arabic_word.txt
```

This path must be replaced with a configurable project-relative or external storage path.

### Kaggle workflow

```http
GET /kaggle
```

The endpoint is intended to:

1. Pull or update the Kaggle dataset.
2. Push the Kaggle notebook.
3. Check notebook status.
4. Retrieve notebook output when complete.

This endpoint should not be publicly exposed. It currently executes local Kaggle CLI commands and uses machine-specific paths. A secured background job or CI workflow is recommended instead.

## Running the notebook

Open the notebook with Jupyter:

```bash
jupyter notebook notebook/final-nb.ipynb
```

Or use JupyterLab:

```bash
jupyter lab notebook/final-nb.ipynb
```

The original notebook was configured for Kaggle and GPU execution. To run it locally:

1. Install the required Python packages.
2. Download the required model and landmark assets.
3. Make the asset paths configurable.
4. Provide a local dataset directory containing MP4 files.
5. Run the cells in order.
6. Verify that `nb_output/arabic_word.txt` is generated.

The notebook currently uses OpenCV and Dlib to extract mouth-region images and TensorFlow/Keras to perform prediction.

## Kaggle configuration

The notebook metadata identifies the following Kaggle resources:

- `ayaali2002/face-landmarks`
- `ayaali2002/final-ds`
- `ayaali2002/gbDataset`
- Notebook: `ayaali2002/final-nb`

To use the Kaggle CLI locally:

1. Install the CLI:

   ```bash
   pip install kaggle
   ```

2. Configure Kaggle credentials according to the official Kaggle documentation.
3. Review the paths and identifiers in `kaggle.py`.
4. Run only the specific workflow function required.

The file `kaggle.py` currently contains placeholder and machine-specific configuration. Do not add API tokens directly to source files.

## Development recommendations

The most important improvements before production use are:

1. Add a pinned `requirements.txt` or `pyproject.toml`.
2. Move inference logic from the notebook into tested Python modules.
3. Replace hard-coded paths with environment variables or command-line options.
4. Add secure password hashing and authentication.
5. Validate upload size, MIME type, and file contents.
6. Remove shell execution from public API routes.
7. Add database migrations.
8. Add automated unit, API, and inference tests.
9. Document model versions, dataset provenance, class labels, and licenses.
10. Add CI for formatting, linting, tests, dependency scanning, and secret scanning.
11. Add confidence scores and clear handling for invalid or low-quality videos.
12. Split training, evaluation, and production inference workflows.

## Testing

Automated tests are not currently included. A recommended test layout is:

```text
tests/
├── test_auth.py
├── test_uploads.py
├── test_inference.py
└── fixtures/
    └── sample.mp4
```

At minimum, tests should cover:

- User creation and authentication.
- Invalid and oversized uploads.
- Video files with no readable frames.
- Videos with no detectable face.
- Mouth-region extraction.
- Class-label parsing.
- Prediction aggregation.
- Missing model and output files.
- API error responses.

## Data, privacy, and licensing

Video and facial data may contain personally identifiable or biometric information. Before distributing or deploying this project:

- Confirm that all recordings were collected with appropriate consent.
- Document the data license and permitted uses.
- Avoid exposing uploaded videos unnecessarily.
- Define retention and deletion policies.
- Do not commit private recordings or credentials.
- Document the limitations and demographic coverage of the dataset.

The repository contains dataset metadata indicating a CC0 license, but the applicability of that license to the actual video recordings should be verified independently.

## Known limitations

- The current code depends on Kaggle-specific paths and assets.
- The API uses hard-coded local filesystem paths.
- Authentication is not production-safe.
- The model and label files are not included in the repository.
- The notebook is not packaged as a reusable inference service.
- There is no dependency lock file or automated test suite.
- Face and mouth detection can fail for poor lighting, occlusion, head rotation, or multiple faces.
- The current prediction aggregation and model input shape should be verified against the model training pipeline.
- The project does not currently expose evaluation metrics or confidence thresholds.

## License

No project-level license file is currently included. Add an explicit `LICENSE` file before distributing the source code or datasets.

## Contributing

When contributing:

1. Create a feature branch.
2. Keep credentials and private data out of commits.
3. Add or update tests for behavioral changes.
4. Document configuration changes.
5. Run formatting, linting, and tests locally.
6. Submit a pull request describing the change and its validation.
