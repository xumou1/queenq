# Development Plan: Supply Chain Network Analysis

This document outlines the development tasks for the Supply Chain Network Analysis project. Each task includes a description, acceptance criteria, and any relevant notes.

## Phase 1: Project Setup & Initial Configuration

---

### **TASK-001: Initialize Project Repository and Structure**
* **Description:** Set up the Git repository, define the initial directory structure as outlined in `README.md`, and add initial rule files.
* **Acceptance Criteria:**
    * [ ] Git repository initialized on a remote server (e.g., GitHub, GitLab).
    * [ ] Project cloned locally.
    * [ ] Main project directories (`data/raw`, `data/processed`, `docs`, `rules`, `src`) created.
    * [ ] Initial `.gitignore` file added.
    * [ ] `README.md` and `DEV_PLAN.md` (this file) created and committed.
    * [ ] Universal, Language, and Framework rule `.mdc` files (as defined previously) are placed in the `rules/` directory.
* **Notes:** Follow `gitflow.mdc` for branching strategy (initialize `main` and `develop` branches).

---

### **TASK-002: Configure Cursor Environment and Rules**
* **Description:** Ensure the Cursor IDE is set up to recognize and utilize the `.mdc` rule files located in the `rules/` directory for consistent development guidance.
* **Acceptance Criteria:**
    * [ ] Cursor IDE correctly loads and applies rules from `general.mdc`.
    * [ ] Cursor IDE provides suggestions based on `python.mdc` when editing Python files.
    * [ ] Cursor IDE assists with commit messages according to `git.mdc`.
* **Notes:** Test with a sample Python file and a sample commit.

---

### **TASK-003: Setup Python Virtual Environment and Install Initial Dependencies**
* **Description:** Create a Python virtual environment and install core libraries (Pandas, NetworkX). Generate the initial `requirements.txt`.
* **Acceptance Criteria:**
    * [ ] Python virtual environment (`venv` or `conda`) created and activated.
    * [ ] Pandas library installed.
    * [ ] NetworkX library installed.
    * [ ] Matplotlib (for basic visualizations) installed.
    * [ ] `requirements.txt` file generated and committed, listing these dependencies.
* **Notes:** Specify the chosen virtual environment tool in `README.md`.

---

## Phase 2: Data Ingestion and Preprocessing

---

### **TASK-004: Develop Script for Loading Listed Company Supplier Data (CSV 1)**
* **Description:** Create a Python script (`src/ingestion/load_supplier_data.py`) to load the "Listed Company Supplier Data" CSV into a Pandas DataFrame.
* **Acceptance Criteria:**
    * [ ] Script successfully loads data from `data/raw/listed_company_suppliers.csv`.
    * [ ] Data is loaded into a Pandas DataFrame.
    * [ ] Basic logging implemented (e.g., number of rows loaded, time taken).
    * [ ] Script handles potential file not found errors gracefully.
    * [ ] Column names are consistent with `data_format.mdc`.
    * [ ] Initial data types are inferred or explicitly set as per `data_format.mdc`.
* **Notes:** Refer to `pandas.mdc` for DataFrame best practices. Parameterize file paths if possible.

---

### **TASK-005: Develop Script for Loading Listed Company Customer Data (CSV 2)**
* **Description:** Create a Python script (`src/ingestion/load_customer_data.py`) to load the "Listed Company Customer Data" CSV into a Pandas DataFrame.
* **Acceptance Criteria:**
    * [ ] Script successfully loads data from `data/raw/listed_company_customers.csv`.
    * [ ] Data is loaded into a Pandas DataFrame.
    * [ ] Basic logging implemented.
    * [ ] Script handles potential file not found errors.
    * [ ] Column names are consistent with `data_format.mdc`.
    * [ ] Initial data types are inferred or explicitly set.
* **Notes:** Structure should be similar to TASK-004.

---

### **TASK-006: Develop Script for Loading Supply Chain Company Basic Information (CSV 3)**
* **Description:** Create a Python script (`src/ingestion/load_company_info.py`) to load the "Supply Chain Company Basic Information" CSV into a Pandas DataFrame.
* **Acceptance Criteria:**
    * [ ] Script successfully loads data from `data/raw/supply_chain_company_info.csv`.
    * [ ] Data is loaded into a Pandas DataFrame.
    * [ ] Basic logging implemented.
    * [ ] Script handles potential file not found errors.
    * [ ] Column names are consistent with `data_format.mdc`.
    * [ ] Initial data types are inferred or explicitly set.
* **Notes:** This data might be used for enriching node attributes later.

---

### **TASK-007: Implement Data Cleaning and Normalization Module**
* **Description:** Develop a module (`src/processing/cleaning.py`) with functions to perform data cleaning and normalization tasks on the loaded DataFrames.
* **Acceptance Criteria:**
    * [ ] Function(s) to handle missing values (as per strategy defined in `data_format.mdc`).
    * [ ] Function(s) to correct data types (e.g., monetary values to numeric, dates to datetime objects).
    * [ ] Function(s) to normalize company names (e.g., remove common suffixes like "Ltd.", "Inc."; convert to consistent case).
    * [ ] Function(s) to remove or flag duplicate records.
    * [ ] Cleaned data can be saved to `data/processed/` directory.
    * [ ] All cleaning steps are logged.
* **Notes:** This module will be used by the main processing script. Consider potential variations in company names.

---

### **TASK-008: Implement Data Validation Module**
* **Description:** Develop a module (`src/processing/validation.py`) with functions to validate data against predefined rules (e.g., expected columns, data ranges, formats).
* **Acceptance Criteria:**
    * [ ] Function(s) to check for presence of required columns.
    * [ ] Function(s) to validate data types for key columns.
    * [ ] Function(s) to check for data integrity (e.g., procurement/revenue amounts are positive).
    * [ ] Validation errors/warnings are logged with details.
    * [ ] A summary report of validation results can be generated.
* **Notes:** Refer to `data_format.mdc`. Decide on a strategy for handling invalid records.

---

### **TASK-009: Merge and Consolidate Company/Entity Identifiers**
* **Description:** Develop a strategy and implement scripts/functions (`src/processing/consolidation.py`) to create unique identifiers for each company/entity across all three datasets.
* **Acceptance Criteria:**
    * [ ] A clear mapping established between variations of company names and a single unique ID.
    * [ ] Supplier, customer, and company info data can be linked using these unique IDs.
    * [ ] Process for handling new or ambiguous entities is documented.
    * [ ] The consolidated entity list/mapping is saved.
* **Notes:** This is a critical step. May involve fuzzy matching or manual review for ambiguous cases. The goal is to ensure a "SupplierA" in one file is the same "Supplier A Co." in another.

---

## Phase 3: Supplier Network Construction

---

### **TASK-010: Design Network Schema**
* **Description:** Finalize the design of the network graph, including node types, edge types, and their respective attributes.
* **Acceptance Criteria:**
    * [ ] Document defining node types (e.g., "Listed Company", "Supplier", "Customer", "Other SC Company").
    * [ ] Document defining edge types (e.g., "procures_from", "sells_to").
    * [ ] List of attributes for nodes (e.g., `company_name`, `unique_id`, `type`, `industry` from company info).
    * [ ] List of attributes for edges (e.g., `amount_eur`, `transaction_year`, `product_category` if available).
* **Notes:** This design will guide the implementation in TASK-011. Consider if a `DiGraph` or `MultiDiGraph` is more appropriate from NetworkX.

---

### **TASK-011: Implement Network Graph Construction from Processed Data**
* **Description:** Develop a script (`src/network/build_network.py`) to construct the supply chain network using NetworkX based on the cleaned and consolidated data.
* **Acceptance Criteria:**
    * [ ] Script loads processed data (output of Phase 2).
    * [ ] Nodes are added to the NetworkX graph based on unique company identifiers.
    * [ ] Node attributes (from company info, or derived) are populated.
    * [ ] Directed edges are created between:
        * Suppliers and Listed Companies (based on procurement data).
        * Listed Companies and Customers (based on revenue data).
    * [ ] Edge attributes (e.g., procurement/revenue amount) are populated.
    * [ ] The constructed graph object can be saved (e.g., as GEXF, GraphML, or pickled object).
* **Notes:** Ensure adherence to `networkx.mdc`.

---

### **TASK-012: Implement Edge Weighting**
* **Description:** Ensure that edges in the network are appropriately weighted, typically by financial transaction amounts (procurement or revenue).
* **Acceptance Criteria:**
    * [ ] Edges representing supplier-company relationships have a 'weight' attribute corresponding to procurement value.
    * [ ] Edges representing company-customer relationships have a 'weight' attribute corresponding to revenue value.
    * [ ] Units and currency for weights are consistent and documented.
    * [ ] Strategy for aggregating multiple transactions between the same two entities into a single edge weight is implemented (if not using MultiDiGraph).
* **Notes:** This weight will be crucial for many network analysis algorithms.

---

## Phase 4: Network Analysis

---

### **TASK-013: Implement Basic Network Metrics Calculation**
* **Description:** Develop functions in (`src/network/analysis.py`) to calculate and report basic network-wide metrics.
* **Acceptance Criteria:**
    * [ ] Calculation of total number of nodes.
    * [ ] Calculation of total number of edges.
    * [ ] Calculation of network density.
    * [ ] Calculation of average degree (in-degree, out-degree).
    * [ ] Results are logged or saved to a report.
* **Notes:** Use NetworkX built-in functions.

---

### **TASK-014: Implement Centrality Analysis**
* **Description:** Implement functions to calculate various centrality measures for nodes in the network.
* **Acceptance Criteria:**
    * [ ] Function to calculate Degree Centrality (in-degree and out-degree for each node).
    * [ ] Function to calculate Betweenness Centrality for each node.
    * [ ] Function to calculate Eigenvector Centrality for each node.
    * [ ] (Optional) Function to calculate Closeness Centrality.
    * [ ] Results (top N nodes by each centrality measure) are logged or saved.
* **Notes:** Interpret what these centralities mean in the context of a supply chain.

---

### **TASK-015: Identify Key Suppliers and Customers**
* **Description:** Utilize centrality measures and transaction volumes to identify and report on key suppliers and key customers within the network, particularly for the listed companies.
* **Acceptance Criteria:**
    * [ ] Report/list of top N suppliers based on total procurement value and/or centrality.
    * [ ] Report/list of top N customers based on total revenue value and/or centrality.
    * [ ] Identification of suppliers/customers critical to multiple listed companies.
* **Notes:** This task applies the analysis from TASK-014 to specific research questions.

---

### **TASK-016: (Optional) Implement Community Detection**
* **Description:** If deemed relevant, implement algorithms to detect communities or clusters of tightly connected companies within the network.
* **Acceptance Criteria:**
    * [ ] A suitable community detection algorithm (e.g., Louvain method) is implemented.
    * [ ] Nodes are assigned to communities.
    * [ ] Basic statistics about the detected communities (e.g., number of communities, size distribution) are reported.
    * [ ] Communities are visualized or listed.
* **Notes:** This can help identify sub-networks or industry clusters.

---

### **TASK-017: (Optional) Implement Supply Chain Path Analysis**
* **Description:** Implement functions to trace supply chains (paths) upstream from a given company to its suppliers and their suppliers, or downstream to its customers and their customers.
* **Acceptance Criteria:**
    * [ ] Function to find all upstream suppliers up to N levels for a given company.
    * [ ] Function to find all downstream customers up to N levels for a given company.
    * [ ] Identification of longest/shortest supply chains for specific products/companies if data permits.
* **Notes:** This can help understand supply chain depth and potential vulnerabilities.

---

## Phase 5: Visualization and Reporting

---

### **TASK-018: Develop Basic Network Visualization**
* **Description:** Create scripts (`src/visualization/plot_network.py`) to generate static visualizations of the supply chain network or its subgraphs using Matplotlib with NetworkX drawing capabilities.
* **Acceptance Criteria:**
    * [ ] Ability to plot the entire network (may be simplified for readability).
    * [ ] Ability to plot subgraphs (e.g., ego-network of a key company).
    * [ ] Nodes are colored/sized based on attributes (e.g., type, centrality).
    * [ ] Edges are weighted/colored based on attributes.
    * [ ] Plots are saved as image files (e.g., PNG, SVG).
* **Notes:** For large networks, visualization can be challenging. Focus on conveying key insights.

---

### **TASK-019: (Optional) Develop Interactive Network Visualization**
* **Description:** Explore and implement interactive network visualizations using libraries like Plotly Dash, Bokeh, or by exporting to Gephi.
* **Acceptance Criteria:**
    * [ ] Network can be explored interactively (zoom, pan, hover over nodes/edges for info).
    * [ ] (If web-based) Visualization is accessible via a local web server.
    * [ ] Data can be exported in a format suitable for Gephi (e.g., GEXF).
* **Notes:** This can significantly enhance a user's ability to explore the network.

---

### **TASK-020: Generate Summary Reports of Analysis Findings**
* **Description:** Consolidate the results from the analysis phase (metrics, key entities, community structures, etc.) into a summary report.
* **Acceptance Criteria:**
    * [ ] A Markdown or PDF document summarizing key findings.
    * [ ] Tables and charts presenting important metrics and lists (e.g., top 10 central companies).
    * [ ] Inclusion of relevant visualizations generated in TASK-018/TASK-019.
    * [ ] Interpretation of the findings in the context of supply chain research.
* **Notes:** This report will be a key deliverable of the project. Store in `docs/reports/`.

---

## Phase 6: Documentation and Finalization

---

### **TASK-021: Update Project Documentation**
* **Description:** Review and update all project documentation, including `README.md`, comments in code, docstrings, and any analytical reports.
* **Acceptance Criteria:**
    * [ ] `README.md` accurately reflects the project's final state, setup, and usage.
    * [ ] All major functions and classes have clear docstrings as per `python.mdc`.
    * [ ] Complex code sections are well-commented.
    * [ ] `DEV_PLAN.md` is updated to reflect completed tasks (this task itself will mark the final update).
* **Notes:** Good documentation is crucial for reproducibility and future work.

---

### **TASK-022: Code Review and Refinement**
* **Description:** Conduct a thorough review of the entire codebase for clarity, efficiency, adherence to coding standards, and correctness.
* **Acceptance Criteria:**
    * [ ] Code is reviewed by at least one other person (if possible) or self-reviewed critically.
    * [ ] Identified issues, bugs, or areas for improvement are addressed.
    * [ ] Code formatting is consistent (e.g., using Black or autopep8).
    * [ ] All defined Cursor rules are adhered to.
* **Notes:** This ensures the quality of the final codebase.

---

### **TASK-023: Final Project Archival/Presentation Preparation**
* **Description:** Prepare the project for archival or presentation, ensuring all deliverables are finalized and organized.
* **Acceptance Criteria:**
    * [ ] Final version of the code is committed and pushed to the `main` branch.
    * [ ] All relevant data (raw, processed, results) is organized and documented.
    * [ ] Final reports and visualizations are complete.
    * [ ] (If applicable) Presentation materials are prepared.
* **Notes:** Ensure the project is in a state that can be easily understood and potentially picked up by others in the future.

---