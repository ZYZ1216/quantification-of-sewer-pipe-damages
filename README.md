# Sewer Damage Quantification

A modular framework for quantifying various types of damage in sewer pipes from images.

## Damage Types and Metrics

| Damage Group   | Measurement Method                   | Description                                                                                                         | Measurement Unit | Alternative Method (low priority)                                                        |
|----------------|--------------------------------------|---------------------------------------------------------------------------------------------------------------------|------------------|------------------------------------------------------------------------------------------|
| Crack          | Crack width                          | The largest crack width of all cracks in the area is measured and saved                                             | mm               | -                                                                                        |
| Root           | Root thickness                       | The thickest root thickness of all the roots in the area is measured and saved.                                     | mm               | If it is a root ball that is considered an obstacle, then the rules for obstacles apply. |
| Deposition     | Area of duct cross-section reduction | The area of the channel cross-section that is reduced by the deposit.                                               | %                | -                                                                                        |
| Obstacle       | Area of duct cross-section reduction | The area of the channel cross-section that is reduced by the obstacle.                                              | %                | -                                                                                        |
| Connection     | Height and width of the connection   | Height and width of the connection.                                                                                 | mm               | -                                                                                        |
| Misalignment   | Pipe center deviation                | Offset of the pipe connection in horizontal, vertical (and radial [low priority]) direction.                        | mm               | -                                                                                        |
| Deformation    | Area of duct cross-section reduction | Visible deformation of the pipe cross-section. This is maybe too hard to detect from the 2D images. (Low priority)  | %                | -                                                                                        |
| JointDamage    | See Misalignment                     | -                                                                                                                   |                  | -                                                                                        |
| MaterialLoss   | Depth of removal                     | Depth of material removal of the channel material.                                                                  | mm               | -                                                                                        |
| Break          | Length                               | Axial length of the fracture in pipe direction.                                                                     | mm               | -                                                                                        |



## Project Structure

### Mapping German Names to English 

| Deutscher Name       | Englische Bezeichnung  | File Names             |
|----------------------|------------------------|------------------------|
| Riss                 | Crack                  | `crack.py`             |
| Wurzel               | Root                   | `root.py`              |
| Ablagerung           | Deposition             | `deposition.py`        |
| Hindernis            | Obstacle               | `obstacle.py`          |
| Anschluss            | Connection             | `connection.py`        |
| Lageabweichung       | Misalignment           | `misalignment.py`      |
| Deformation          | Deformation            | `deformation.py`       |
| Muffenschaden        | Joint Damage           | `joint_damage.py`      |
| Materialabtrag       | Material Loss          | `material_loss.py`     |
| Bruch                | Break                  | `break.py`             |






## Environment Setup - Using Conda
<details>
<summary>Click to expand</summary>
If you are using `uv`, please skip to the next section.

Please follow the steps below to get started.


1. **Clone the Repository**

   Begin by cloning the repository from GitLab to your local machine. Make sure you have Git installed.


2. **Create the Conda Environment**

   Use the provided `environment.yml` file to create the environment:

   ```bash
   conda env create -f environment.yml
   ```

3. **Activate the Environment**

   Once the environment is created, activate it:

   ```bash
   conda activate damage_quantification
   ```

4. **Start Working on the Project**

   With the environment activated, you're ready to run scripts, notebooks, or start development.

</details>


## Environment Setup - Using `uv`

<details>
<summary>Click to expand</summary>
If you are using conda, please skip to the next section.

Please follow the steps below to get started.

1. **Clone the Repository**

   Begin by cloning the repository to your local machine. Make sure you have Git installed.

2. **Install `uv`**

   If you don't have `uv` installed, follow the official installation guide: [https://astral.sh/uv#installation](https://astral.sh/uv#installation)
   (e.g., using pipx: `pipx install uv` or pip: `pip install uv`). Ensure the `uv` command is accessible in your terminal (you might need to add its installation location to your system's PATH).

3. **Create the Virtual Environment**

   Navigate to the project's root directory in your terminal and create a virtual environment:

   ```bash
   uv venv
   ```
   This creates a `.venv` directory containing the Python interpreter and dependencies.

4. **Configure Environment Variables for FTP**

   Some scripts, like image downloading, require FTP credentials. These are managed using a `.env` file for security:
   1.  **Copy the example file:** `cp .env.example .env` (or copy manually).
   2.  **Edit `.env`:** Open the newly created `.env` file and replace the placeholder values with your actual FTP server hostname, username, password, and the base path where the images are stored on the server.
   3.  **Security:** The `.env` file is listed in `.gitignore` and **must not** be committed to version control.

5. **Activate the Environment**

   Activate the created environment. The command depends on your shell:

   *   **Bash / Zsh / Git Bash:**
       ```bash
       source .venv/bin/activate
       ```
   *   **PowerShell:**
       ```bash
       .venv\Scripts\Activate.ps1
       ```
       (You might need to adjust your PowerShell execution policy: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`)
   *   **CMD (Command Prompt):**
       ```bash
       .venv\Scripts\activate.bat
       ```
   Your terminal prompt should now indicate that the `.venv` environment is active (e.g., `(.venv)`).

6. **Install Dependencies**

   Install the project dependencies and the project itself in editable mode. We recommend using the lock file for reproducible environments:

   ```bash
   # Ensure .venv is activated

   # Generate lock file if it doesn't exist or dependencies changed
   uv lock

   # Install dependencies from lock file
   uv sync

   # Install project in editable mode (needed to run scripts/import modules)
   uv pip install -e . --no-deps

### Additional Notes

- **Updating Dependencies:** If `pyproject.toml` changes (e.g., new dependencies are added), regenerate the lock file and re-sync:
    ```bash
    # Ensure .venv is activated
    uv lock
    uv sync
    uv pip install -e . --no-deps # Re-run if sync removed editable install
    ```

- **Troubleshooting:** If you encounter issues, try removing the `.venv` directory and recreating the environment from step 3 onwards. Ensure `uv` itself is up-to-date (`uv self update`).
   ```

</details>

## Downloading Training Images

<details>
<summary>Click to expand</summary>

This project includes a script to download specific training images from the FTP server based on labels defined in a CSV file. This is useful for obtaining the necessary data for training or evaluating specific damage type quantifiers.

**Prerequisites:**

**Configured `.env` file for FTP Access:** The download script requires FTP credentials and the server path. These must be configured in a `.env` file in the project root:
    *   **If you haven't already:** Copy the example file: `cp .env.example .env` (or copy it manually).
    *   **Edit `.env`:** Open the `.env` file and replace the placeholder values for `FTP_HOST`, `FTP_USER`, `FTP_PASSWORD`, and `FTP_BASE_PATH` with your actual credentials and the base directory where images are stored on the FTP server.
    *   **Security:** Remember, `.env` is in `.gitignore` and should *not* be committed to version control. (See step 4 in Getting Started for more details).

**Usage:**

The script `scripts/download_images.py` accepts several command-line arguments. You can see all options by running:

```bash
python scripts/download_images.py --help
```

**Example:**

To download the first 50 images labeled as 'Hindernis' (Obstacle) using the `data/training_data.csv` file and save them into the `images_ignore/hindernis/` directory:

```bash
# Make sure your .venv is active and .env is configured

python scripts/download_images.py --csv-path data/training_data.csv --label Hindernis --max-images 50 --output-dir images_ignore/hindernis/
```

To download images for a different label, like 'Riss' (Crack), adjust both the `--label` and the `--output-dir` accordingly:

```bash
python scripts/download_images.py --csv-path data/training_data.csv --label Riss --max-images 50 --output-dir images_ignore/riss/
```

- Replace `data/training_data.csv` with the actual path to your CSV file containing image filenames and labels.
- Change the `--label` argument to the desired German label (e.g., `Hindernis`, `Riss`, `Wurzel`).
- Adjust `--max-images` to control the number of images downloaded per label.
- Change the `--output-dir` argument to specify where the downloaded images will be saved. It's recommended to use a directory name corresponding to the lowercase version of the label (e.g., `images_ignore/hindernis/` for the `Hindernis` label).

</details>

## Workflow for Collaboration

We recommend using feature branches for development, especially when working on specific damage types.

### Pulling the Latest Changes

Before starting new work or creating a branch, ensure your main branch (e.g., `main` or `master`) is up-to-date:

```bash
# Switch to your main branch (e.g., main)
git checkout main 
git pull origin main 
```

### Creating a Feature Branch

Create a new branch for the specific damage type or feature you are working on. Naming branches based on the damage type is encouraged:

```bash
# Example for working on Obstacle quantification
git checkout -b feature/obstacle-quantification

# Example for working on Root quantification
# git checkout -b feature/root-quantification 
```

### Pushing Your Changes

Commit your changes to your feature branch regularly. When ready to share or merge, push your branch to the remote repository:

```bash
# Push your current branch (e.g., feature/obstacle-quantification)
git push --set-upstream origin feature/obstacle-quantification
```

Follow team conventions for creating Merge Requests (or Pull Requests) to integrate your feature branch back into the main branch after review.

---

## Project Directory Structure

Here's an overview of the recommended project layout for collaborative development, based on design patterns suitable for multiple damage type quantification:

```
sewer_damage/
│
├── quantifiers/            # One module per damage type + base
│   ├── base.py
│   ├── crack.py
│   ├── root.py
│   └── ...                 
│
├── preprocessing/          # Shared image/ROI transforms
│   └── transforms.py
│
├── factory.py              # QuantifierFactory
├── pipeline.py             # Orchestrates label→quantifier→output
├── requirements.txt
├── setup.py                # For packaging
├── tests/                  # Unit tests per quantifier & utils
│   └── test_crack.py
└── docs/                   # Design docs & usage examples
```

- Each quantifier should reside in its own file to support parallel work.
- Shared transforms and utilities should be modular for reuse.
- Maintain good coding standards (PEP-8) and use CI/CD linting.

