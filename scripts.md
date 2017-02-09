# Data generation steps

Here we describe the steps for processing of data, extracting features, and training of our models for each of profession and nationality relations. 


## Preprocessing

1. Indexing of Wikipedia sentences
    - `wp_sentence_index.py` 
2. Extracting 1st Wikipedia sentences and paragraphs
    - `extract_fst_wp_sentences.py`
    - For each `<snippet>` (`sentences`, `paragraphs`):
        - `<input: config_json/fst_wp_sentences_config.json>`
        - `<output: first_wp_sentences/persons_without_<snippet>.txt>`
        - `<output: first_wp_sentences/first_wp_<snippet>.tsv>`
3. Getting the to-id mappings from persons and from items (check code documentation for a much clearer understanding, since the functions are parametrized, and all the development was intended to be used as library, so no command-line support is provided in general).
    - `make_item_ids.py` functions:
    - `make_item_ids.make_persons_fb_ids`
        - `<input: persons>`
        - `<output: persons_ids.tsv>`
    - `make_item_ids.make_relation_item_ids`
        - `<input: professions>`
        - `<output: professions_ids.tsv>`
    - `make_item_ids.make_relation_item_ids`
        - `<input: nationalities>`
        - `<output: nationalities_ids.tsv>`
    - `make_item_ids.make_professions_kb_translation`
        - `<input: persons_ids.tsv; professions_ids.tsv; professions.kb>`
        - `<output: profession_translations.kb>`


## Profession

1. Generating tfidf weights 
    - `prof_stats.py`
        - `<output:tf_idf.tsv>`
2. Generating term statistic features of *sumProfTerms* and *simCos*
    -  `feat_termstats.py`
        - `<input:tf_idf.tsv>`
        - `<output:profession_translations.kb;`
        `features_termstats_prof.tsv>`
3. Generating features: *isProfWPSent*, *isProfWPPar*, *isFirstProfWPSent*, and *isFirstProfWPPar*
    - `feat_fst_wp_sentences.py`
    - For each `<snippet>` (`sentences`, `paragraphs`):
        - `<input: professions; first_wp_sentences/first_wp_<snippet>.tsv; professions.kb; "profession">`
        - `<output: is_profession_in_first_wp_<snippet>.tsv>`
        - `<output: is_1st_profession_in_first_wp_<snippet>.tsv>`
4. Generating *simCosW2VPar* feature
    - `feat_w2v_sim_approx.py`
        - `<input: profession_translations.kb>`
        - `<output: profession-approx-w2v_aggr_cos_sim.tsv>`
5. Generating *simCosW2V* feature
    - `feat_w2v_sim.py`
        - `<input: profession_translations.kb>`
        - `<output: profession_w2v_aggr_cos_sim.tsv>`


## Nationality

1. Generating person-nationality input files
    - `make_fre_input.py 

        `<input:nationalities_ids.tsv;`

        `nationality_adjectives.tsv;`

        `persons_ids.tsv;`

        `nationality.kb;`

        `nationality_translations.kb>`

    -  `<output: nationality_translations2.kb>` 

2. Generating features of *isNatWPSent*, *isNatWPPar*, *isFirstNatWPSent*, and *isFirstNatWPPar* 
    - `feat_fst_up_sentences_nationality.py 
        - `<input:nationality_adjectives.tsv;`

        `nationality_translations2.kb;`

        `first_wp_sentences.txt;`

        `first_wp_paragraphs.txt>`

        - `<output:is_1st_nationality_in_first_wp_paragraphs_Adj.tsv;`

        `is_1st_nationality_in_first_wp_paragraphs_Noun.tsv;`

        `is_1st_nationality_in_first_wp_sentences_Adj.tsv;`

        `is_1st_nationality_in_first_wp_sentences_Noun.tsv;`

        `is_nationality_in_first_wp_paragraphs_Adj.tsv;`

        `is_nationality_in_first_wp_paragraphs_Noun.tsv;`

        `is_nationality_in_first_wp_sentences_Adj.tsv;`

        `is_nationality_in_first_wp_sentences_Noun.tsv;>` 

3. Generating *freqPerNat* feature 
    - `feat_freq.py`
        - `<input:nationality_translations.kb>`
        - `<output:nat_features_freq_Noun2.tsv;`

        `nat_features_freq_Adj2.tsv>`

## Scoring

1. Aggregating all features
     - `feat_agg.py [-t]`, use `-t` for training dataset
     - `<output:RELATION_train.json;`
     - `RELATION_all.json>`
2. Training/test/cross validation
    - `uis_software -i <input data> -o <output/path>`

## Evaluating

1.  Main software entry point
    - `uis_software.py -i <input> -o <output>` (as [required here](http://www.wsdm-cup-2017.org/triple-scoring.html#Submission))