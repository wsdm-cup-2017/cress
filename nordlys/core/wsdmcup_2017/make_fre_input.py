"""
This file is used to create a person-nationality files with 4
columns: person_id nationality_id nationality_noun nationality_adj

@author: Shuo Zhang
"""

def generate_file(nat_id_file, nat_adj_file, name_id_file, kb_file, output_file, output_file2):
    noun_nat = {}
    with open(nat_id_file, "r") as f1:
        for line in f1:
            noun, nat_id = line.strip().split("\t")
            noun_nat[noun] = nat_id

    noun_adj = {}
    with open(nat_adj_file, "r") as f2:
        for line in f2:
            noun, adj = line.strip().split("\t")
            noun_adj[noun] = adj

    name_id = {}
    with open(name_id_file, "r") as f3:
        for line in f3:
            name, Id = line.strip().split("\t")
            name_id[name] = Id

    f5 = open(output_file, "w")
    f6 = open(output_file2, "w")


    with open(kb_file, "r") as f4:
        for line in f4:
            values = []
            values2 = []
            name, nat = line.strip().split("\t")
            values2.append(name)
            nat_id = noun_nat[nat]
            nameId = name_id[name]
            adj = noun_adj[nat]
            values.append(nameId)
            values.append(nat_id)
            values.append(nat)
            values.append(adj)
            values2.append(nameId)
            values2.append(nat_id)
            values2.append(nat)
            values2.append(adj)
            f5.write("\t".join(values) + "\n")
            f6.write("\t".join(values2) + "\n")
            print(values)
            print(values2)
    f5.close()




if __name__ == "__main__":
    generate_file("/data/scratch/wsdm-cup-2017/data/nationalities_ids.tsv",
                  "/data/scratch/wsdm-cup-2017/data/nationality_adjectives.tsv",
                  "/data/scratch/wsdm-cup-2017/data/persons_ids.tsv",
                  "/data/scratch/wsdm-cup-2017/collection/nationality.kb",
                  "/data/scratch/wsdm-cup-2017/data/nationality_translations.kb",
                  #nationality_translations2: person,person_id,nat_id,nat_noun,nat_adj
                  "/data/scratch/wsdm-cup-2017/data/nationality_translations2.kb")
