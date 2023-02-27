import os
import glob
import csv

class Table:

    def __init__(self, name):
        self.header = None
        self.rows = []
        self.values = {}
        self.name = name
        self.covered_by = {}
        self.mapped_fields = set()
        self.unmapped_fields = set()
        self.mapping = {}

    def set_header(self, header):
        self.header = [h.strip() for h in header]
        for key in self.header:
            assert key
            self.values[key] = set()
            self.covered_by[key] = {}
            self.unmapped_fields.add(key)
        assert len(self.unmapped_fields) == len(self.header)

    def add_row(self, row):
        assert len(self.header) == len(row)
        self.rows.append(row)
        for key, value in zip(self.header, row):
            if value:
                self.values[key].add(value)
                if value not in self.covered_by[key]:
                    self.covered_by[key][value] = set()

    def print_values(self):
        for key in self.values.keys():
            print(f"{key}: {self.values[key]}")

    def get_relevant_sql_tables(self):
        return set([sql_table for sql_table, _ in self.mapping.values()])

    def check_field_value(self, sql_table, sql_field, value):
        for key, values in self.values.items():
            if key in self.unmapped_fields and value in values:
                tag = tuple([key, value])
                sql_tag = tuple([sql_table, sql_field])
                self.covered_by[key][value].add(sql_tag)
                if all(sql_tag in s for s in self.covered_by[key].values()):
                    self.unmapped_fields.remove(key)
                    self.mapped_fields.add(key)
                    self.mapping[key] = sql_tag

    def all_fields_mapped(self):
        return len(self.unmapped_fields) == 0
        
class PrecomputedTables:

    def __init__(self, dir_name):
        #print(dir_name)
        self.all_tables = []
        self.unmapped_tables = {}
        self.mapped_tables = {}
        self.sql_primary_key = {}
        self.sql_tables = None
        self.preloaded_mapping = False
        os.chdir(dir_name)
        #if os.path.exists(f"{dir_name}/mapping.txt"):
        #    with open(f"{dir_name}/mapping.txt", "r") as f:
        #        for line in f:
        #            line = line.strip("\n")
        #            if not line.startswith("\t"):
        #                fname = line
        #            else:
        #                line = line.strip("\t")
        #                n = line.find(" ->")
        #                pre = line[:n]
        #                pos = line[n+4:]
        #                if pos == "???":
        #                    continue
        #                table, field = tuple(pos.split())
        #                print("\t".join([fname, pre, table, field]))
        for file_name in glob.glob("*.tsv"):
            #print(file_name)
            table = Table(file_name)
            self.unmapped_tables[file_name] = table
            self.all_tables.append(table)
            self._process_tsv(file_name)
        if os.path.exists(f"{dir_name}/mapping.txt"):
            self.preloaded_mapping = True
            mappings = {}
            with open(f"{dir_name}/mapping.txt", "r") as f:
                for line in f:
                    line = line.strip("\n").split("\t")
                    fname, column, referenced_table, referenced_column = tuple(line)
                    if fname not in mappings:
                        mappings[fname] = []
                    mappings[fname].append(tuple([column, referenced_table, referenced_column]))
            finished = []
            for key, table in self.unmapped_tables.items():
                if key not in mappings:
                    continue
                for column, referenced_table, referenced_colum in mappings[key]:
                    table.unmapped_fields.remove(column)
                    table.mapped_fields.add(column)
                    table.mapping[column] = tuple([referenced_table, referenced_column])
                if table.all_fields_mapped():
                    finished.append(key)
            for key in finished:
                self.mapped_tables[key] = self.unmapped_tables.pop(key)

    def mappings_str(self):
        output = []
        output.append(f"Fully mapped tables: {len(self.mapped_tables)}\n")
        for key, table in self.mapped_tables.items():
            output.append(f"{key}")
            for key in table.mapped_fields:
                sql_table, sql_field = table.mapping[key]
                output.append(f"\t{key} -> {sql_table} {sql_field}")
        if len(self.unmapped_tables) == 0:
            return "\n".join(output)
        output.append(f"Non (or partially) mapped tables: {len(self.unmapped_tables)}\n")
        for key, table in self.unmapped_tables.items():
            output.append(f"{key}")
            for key in table.mapped_fields:
                sql_table, sql_field = table.mapping[key]
                output.append(f"\t{key} -> {sql_table} {sql_field}")
            for key in table.unmapped_fields:
                output.append(f"\t{key} -> ???")
        return "\n".join(output) + "\n"

    def _add_row(self, file_name, row):
        self.unmapped_tables[file_name].add_row(row)

    def _set_header(self, file_name, header):
        self.unmapped_tables[file_name].set_header(header)

    def _process_tsv(self, file_name):
        header = None
        with open(file_name) as f:
            rows = csv.reader(f, delimiter="\t", quotechar='"')
            for row in rows:
                if not row:
                    continue
                if not row[0].startswith("#"):
                    if header is None:
                        header = [previous[0].lstrip("#"), *previous[1:]]
                        self._set_header(file_name, header)
                        #print(header)
                    self._add_row(file_name, row)
                    #print(row)
                if not row[0].startswith("#-----"):
                    previous = row
        #self.unmapped_tables[file_name].print_values()

    def set_sql_primary_key(self, sql_table, field):
        self.sql_primary_key[sql_table] = field

    def all_tables_mapped(self):
        return self.preloaded_mapping or len(self.unmapped_tables) == 0

    def check_field_value(self, sql_table, sql_field, value):
        finished = []
        for key, table in self.unmapped_tables.items():
            table.check_field_value(sql_table, sql_field, value)
            if table.all_fields_mapped():
                finished.append(key)
        for key in finished:
            self.mapped_tables[key] = self.unmapped_tables.pop(key)

    def get_relevant_sql_tables(self):
        answer = set()
        for table in self.all_tables:
            answer = answer.union(table.get_relevant_sql_tables())
        return answer
