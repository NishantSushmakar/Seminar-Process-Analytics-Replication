
# Event Log Extraction for Process Mining Using Large Language Models

Process mining is a discipline that enables organizations to discover and analyze their work processes. A prerequisite for conducting a process mining initiative is the so-called event log, which is not always readily available. In such cases, extracting an event log involves various time-consuming tasks, such as creating tailor-made structured query language (SQL) scripts to extract an event log from a relational database. With this project, we investigate the use of large language models (LLMs) to support event log extraction, particularly by leveraging LLMs' ability to produce SQL scripts. We report on how effectively an LLM can assist with event log extraction for process mining. Despite the intrinsic non-deterministic nature of LLMs, our results show the potential of future LLM-assisted event log extraction tools, especially when domain and data knowledge are available. The implementation of such tools can increase access to event log extraction to a broader range of users within an organization by reducing the reliance on specialized technical skills for producing relational database query scripts and minimizing manual effort.

## Repository Structure
```
├── plots                                      <- Directory for plot files.
├── prompts                                    <- Directory for prompt files used by LLMs.
├── testDBs                                    <- Directory for test databases.
├── utils                                      <- Utils folder.
│   ├── metrics.py                             <- Contains metric functions.
│   └── preprocessing.py                       <- Contains preprocessing functions.
├── .gitignore                                 <- Git ignore file.
├── LICENSE                                    <- License file.
├── README.md                                  <- Project overview and instructions (this file).
├── requirements.txt                           <- Python package dependencies.
├── test_cases_batch.ipynb                     <- Jupyter notebook for batch test cases.
├── test_db.ipynb                              <- Jupyter notebook for database tests.
```


## Getting Started

### Prerequisites

Ensure you have Python installed. You can check your Python version by running:
```bash
python --version
```

### Installation

1. Clone the repository:
   ```bash
   git clone *****
   cd event-log-extraction-for-process-mining
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use \`venv\Scriptsctivate\`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Notebooks

1. **Run evaluation**:
   - `test_cases_batch.ipynb`:
     Contains batch test cases to validate the prompts against the DBs.
2. **(optional) Test a db**:
   - `test_db.ipynb`:
     Used for testing the SQL scripts against test databases.
   
### Directory Details

- **utils**:
  - `metrics.py`: Contains functions to compute various metrics for evaluation.
  - `preprocessing.py`: Includes preprocessing functions to prepare the data for LLMs.

- **plots**:
  - Directory for storing generated plots.

- **prompts**:
  - Directory for storing prompts used by LLMs.

- **testDBs**:
  - Directory for storing test databases used for validation.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

