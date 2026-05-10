import os
import shutil
import sqlite3

def setup():
    print("--- SeikoClaw Harness Setup ---")
    
    dirs = [".agents", ".agents/skills", ".agents/workflows", ".master_wiki", "openbrain"]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"Created directory: {d}")
        else:
            print(f"Directory already exists: {d}")

    # Initialize Openbrain DB if it doesn't exist
    db_path = "openbrain/openbrain.db"
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        print("Initialized openbrain/openbrain.db")
        conn.close()

    # Create a template .seikoclaw.yaml
    config_path = ".seikoclaw.yaml"
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            f.write("workspace_name: My Project\npersistence_layer: openbrain\nknowledge_base: .master_wiki\n")
        print("Created template .seikoclaw.yaml")

    print("\nSetup complete! You can now start using SeikoClaw skills and workflows.")

if __name__ == "__main__":
    setup()
