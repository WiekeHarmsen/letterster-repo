# letterster-repo
This is a repository to process data collected in the Letterster project.

## Preprocessing

    dataDir=/vol/bigdata3/datasets3/dutch_child_audio/letterster/spelling/letterster_dictations
    python3 convert-pdf-to-csv.py --data_dir $dataDir

### INPUT
`--data_dir` is a directory containing one folder: 01_pdf (this folder contains the pdfs that have to be converted)

### OUTPUT
- `02_dictations` One dataframe for each test, containing all target and realized spellings and their correctness evaluations
- `03_error_categories` The most frequent error categories in the dictation
- `task-level-results.[tsv/csv/xlsx]` Overview file over all analyzed pdf files