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

# Mapping German Names to English 

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



# Damage Quantification

This project uses a Conda environment to ensure consistency across development and analysis. Please follow the steps below to get started.

## Getting Started

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

## Workflow for Collaboration

### Pulling the Latest Changes

Before starting work, always pull the latest changes from the repository:

```bash
git pull
```

### Pushing Your Changes

After making changes and committing locally, push them to the remote repository:

```bash
git push
```

Make sure to follow any branch naming conventions or workflow rules set by the team (e.g., feature branches, merge requests).

## Additional Notes

- If the environment changes (e.g., new dependencies are added), re-run the environment creation command or use:

  ```bash
  conda env update -f environment.yml --prune
  ```

- If you run into issues with the environment, you can remove and recreate it:

  ```bash
  conda remove --name damage_quantification --all
  conda env create -f environment.yml
  ```

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

