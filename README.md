# Supply Chain Network Analysis Project

## 1. Project Description
This project aims to construct and analyze a supplier network based on data from listed companies. The primary goal is to identify key entities, understand network structures, and derive insights into supply chain dependencies and concentrations. The analysis will utilize procurement data from listed companies, sales data to their customers, and basic information about supply chain companies.

This research is conducted using Python, with a focus on data manipulation and network analysis libraries. The development process is guided by rules managed within Cursor.

## 2. Data Sources
The analysis will be based on three main types of CSV data:
1.  **Listed Company Supplier Data:** Contains information on listed companies, their suppliers, and the respective procurement amounts.
2.  **Listed Company Customer Data:** Contains information on listed companies, their customers, and the respective revenue amounts.
3.  **Supply Chain Company Basic Information:** Contains general details about companies operating within the supply chain (e.g., location, industry, size if available).

## 3. Key Features & Analysis
* **Data Ingestion and Cleaning:** Robust loading, validation, and cleaning of the provided CSV datasets.
* **Entity Normalization:** Standardizing company names and identifiers across different datasets.
* **Network Construction:** Building a directed graph representing the supplier-customer relationships, where nodes are companies and edges represent transactions or relationships, weighted by financial amounts.
* **Network Metrics:** Calculation of basic network statistics (e.g., density, degree distribution).
* **Centrality Analysis:** Identification of key players (suppliers, customers, intermediaries) using centrality measures (e.g., degree, betweenness, eigenvector centrality).
* **Community Detection (Optional):** Identifying clusters or communities within the network.
* **Visualization:** Generating visual representations of the supply chain network to aid in understanding its structure.

## 4. Technology Stack
* **Programming Language:** Python 3.x
* **Data Manipulation:** Pandas
* **Network Analysis:** NetworkX
* **Development Environment:** Cursor
* **Version Control:** Git
* **Virtual Environment:** `venv` or `conda` (to be specified)

## 5. Setup and Installation

### 5.1. Prerequisites
* Python 3.8+
* Git
* Cursor IDE (with configured rules from the `rules/` directory)

### 5.2. Clone Repository
```bash
git clone <your-repository-url>
cd <repository-name>