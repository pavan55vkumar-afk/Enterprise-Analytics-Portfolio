import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import build_notebooks

print("Building notebook files...")
build_notebooks.create_project_1_notebook()
build_notebooks.create_project_2_notebook()
build_notebooks.create_project_3_notebook()
build_notebooks.create_project_4_notebook()

# Setup execution preprocessor
ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

# Project 1
print("Running and compiling Project 1 notebook...")
p1_dir = "project_1_sales_cohort"
os.rename("project1_cohort_rfm_analysis.ipynb", os.path.join(p1_dir, "project1_cohort_rfm_analysis.ipynb"))
with open(os.path.join(p1_dir, "project1_cohort_rfm_analysis.ipynb")) as f:
    nb1 = nbformat.read(f, as_version=4)
# Execute inside project_1_sales_cohort/
ep.preprocess(nb1, {'metadata': {'path': p1_dir}})
with open(os.path.join(p1_dir, "project1_cohort_rfm_analysis.ipynb"), "w") as f:
    nbformat.write(nb1, f)
print("Project 1 notebook compiled successfully!")

# Project 2
print("Running and compiling Project 2 notebook...")
p2_dir = "project_2_operations_rca"
os.rename("project2_operations_sla_rca.ipynb", os.path.join(p2_dir, "project2_operations_sla_rca.ipynb"))
with open(os.path.join(p2_dir, "project2_operations_sla_rca.ipynb")) as f:
    nb2 = nbformat.read(f, as_version=4)
ep.preprocess(nb2, {'metadata': {'path': p2_dir}})
with open(os.path.join(p2_dir, "project2_operations_sla_rca.ipynb"), "w") as f:
    nbformat.write(nb2, f)
print("Project 2 notebook compiled successfully!")

# Project 3
print("Running and compiling Project 3 notebook...")
p3_dir = "project_3_product_ab_test"
os.rename("project3_checkout_ab_test.ipynb", os.path.join(p3_dir, "project3_checkout_ab_test.ipynb"))
with open(os.path.join(p3_dir, "project3_checkout_ab_test.ipynb")) as f:
    nb3 = nbformat.read(f, as_version=4)
ep.preprocess(nb3, {'metadata': {'path': p3_dir}})
with open(os.path.join(p3_dir, "project3_checkout_ab_test.ipynb"), "w") as f:
    nbformat.write(nb3, f)
print("Project 3 notebook compiled successfully!")

# Project 4
print("Running and compiling Project 4 notebook...")
p4_dir = "project_4_data_quality"
os.rename("project4_data_quality_audit.ipynb", os.path.join(p4_dir, "project4_data_quality_audit.ipynb"))
with open(os.path.join(p4_dir, "project4_data_quality_audit.ipynb")) as f:
    nb4 = nbformat.read(f, as_version=4)
ep.preprocess(nb4, {'metadata': {'path': p4_dir}})
with open(os.path.join(p4_dir, "project4_data_quality_audit.ipynb"), "w") as f:
    nbformat.write(nb4, f)
print("Project 4 notebook compiled successfully!")

print("\nAll 4 project notebooks compiled successfully!")
