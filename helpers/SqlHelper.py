import os

helper_dir = os.path.dirname(os.path.abspath(__file__))
script_dir = os.path.join(helper_dir, "../sql_procedures")

def get_sql_procedure(self, procedure_name):
    fp = os.path.join(script_dir, "{}.sql".format(procedure_name))
    if os.path.isfile(fp):
        with open(fp, "r") as script:
            return script.read()