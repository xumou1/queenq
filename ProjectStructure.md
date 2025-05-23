.
├── data/
│   ├── raw/                # Raw input CSV files
│   │   ├── listed_company_suppliers.csv
│   │   ├── listed_company_customers.csv
│   │   └── supply_chain_company_info.csv
│   ├── processed/          # Cleaned and processed data
│   └── interim/            # Intermediate data files (optional)
├── docs/                   # Project documentation (like DEV_PLAN.md, analysis reports)
├── notebooks/              # Jupyter notebooks for exploratory analysis (optional)
├── .cursorrules/           # Cursor .mdc rule files
│   ├── universal_rules/
│   │   ├── general.mdc
│   │   ├── git.mdc
│   │   ├── gitflow.mdc
│   │   └── document.mdc
│   ├── language_rules/
│   │   ├── python.mdc
│   │   └── data_format.mdc
│   └── framework_rules/
│       ├── pandas.mdc
│       └── networkx.mdc
├── src/                    # Source code
│   ├── ingestion/          # Data loading scripts
│   ├── processing/         # Data cleaning and transformation scripts
│   ├── network/            # Network construction and analysis scripts
│   ├── visualization/      # Visualization scripts
│   └── utils/              # Utility functions
├── tests/                  # Unit tests (optional but recommended)
├── .gitignore
├── README.md               # This file
├── DEV_PLAN.md             # Development plan and tasks
└── requirements.txt        # Python package dependencies