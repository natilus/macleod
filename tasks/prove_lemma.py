'''
Created on 2013-03-29

@author: Torsten Hahmann
'''

from tasks import *
from src import logging, ClifLemmaSet
from src.ClifModuleSet import ClifModuleSet


def run_simple_check(m):
    (_, r) = m.run_simple_consistency_check().popitem()
    if r==ClifModuleSet.PROOF:
        logging.getLogger(__name__).info("+++ LEMMA PROVED " +m.get_lemma_module().get_simple_module_name() + " from AXIOMS: " + str(m.get_axioms())  +"\n")
    elif r==ClifModuleSet.COUNTEREXAMPLE:
        logging.getLogger(__name__).info("+++ SENTENCE REFUTED " +m.get_lemma_module().get_simple_module_name() + " in AXIOMS: " + str(m.get_axioms())  +"\n")
    else:
        logging.getLogger(__name__).info("+++ SENTENCE NEITHER PROVED NOR REFUTED " +m.get_lemma_module().get_simple_module_name() + " in AXIOMS: " + str(m.get_axioms())  +"\n")
    return r
    
            
def prove (lemmas_filename, summary_file, axioms_filename=None, options=[]):
        
    if axioms_filename is None:
        m = ClifModuleSet(lemmas_filename)
        #print "REMOVING " + m.get_top_module().module_name
        m.remove_module(m.get_top_module())
    else:
        m = ClifModuleSet(axioms_filename)
        
    lemmas = ClifLemmaSet(lemmas_filename)

    lemma_modules = lemmas.get_lemmas()
    
    for l in lemma_modules:
        logging.getLogger(__name__).debug("LEMMA MODULE: " + l.module_name + " TPTP_SENTENCE " + l.tptp_sentence)

    for l in lemma_modules:
        m.add_lemma_module(l)
        
        #print str(m.get_imports())
        l.output = ClifModuleSet.UNKNOWN
        
        if '-module' in options:
            results = m.run_consistency_check_by_subset(abort_signal = ClifModuleSet.PROOF, increasing=True)
            for (i, r) in results.iteritems():
                if r==ClifModuleSet.PROOF:
                    l.output = ClifModuleSet.PROOF
                    logging.getLogger(__name__).info("+++ LEMMA PROVED " +l.get_simple_module_name() + "from AXIOMS: " + str(i)  +"\n")
            if l.output != ClifModuleSet.PROOF:
                l.output = run_simple_check(m)
                
        elif '-depth' in options:
            results = m.run_consistency_check_by_depth(abort_signal = ClifModuleSet.PROOF, increasing=True)
            for (i, r) in results.iteritems():
                if r==ClifModuleSet.PROOF:
                    l.output = ClifModuleSet.PROOF
                    logging.getLogger(__name__).info("+++ LEMMA PROVED " +l.get_simple_module_name() + "from AXIOMS: " + str(i)  +"\n")
            if l.output != ClifModuleSet.PROOF:
                l.output = run_simple_check(m)
        
        elif '-simple' in options:
            l.output = run_simple_check(m)
        else:
            results = m.run_full_consistency_check()
            for (i, r) in results.iteritems():
                if len(results)==1 and r==ClifModuleSet.COUNTEREXAMPLE:
                    l.output = ClifModuleSet.COUNTEREXAMPLE
                    logging.getLogger(__name__).info("+++ SENTENCE REFUTED " +m.get_lemma_module().get_simple_module_name() + " in AXIOMS: " + str(m.get_axioms())  +"\n")
                if r==ClifModuleSet.PROOF:
                    l.output = ClifModuleSet.PROOF
                    logging.getLogger(__name__).info("+++ LEMMA PROVED " +l.get_simple_module_name() + "from AXIOMS: " + str(i)  +"\n")
            if l.output != ClifModuleSet.PROOF:
                l.output = ClifModuleSet.UNKNOWN
                logging.getLogger(__name__).info("+++ SENTENCE NEITHER PROVED NOR REFUTED " +m.get_lemma_module().get_simple_module_name() + " in AXIOMS: " + str(m.get_axioms())  +"\n")

    proofs = 0
    counterexamples = 0
    unknown = 0
    
    # write results to summary single_file
    single_file = open(summary_file, "a")
    for l in lemma_modules:
        if l.output == ClifModuleSet.PROOF: proofs += 1
        elif l.output == ClifModuleSet.COUNTEREXAMPLE: counterexamples += 1
        else: unknown += 1
        single_file.write(str(l.output) + " " + l.module_name + "\n")
    single_file.flush()
    single_file.close()
    
    return (proofs, counterexamples, unknown)
    

if __name__ == '__main__':
    # global variables
    import sys
    licence.print_terms()
    options = sys.argv
    options.reverse()
    options.pop()
    if '-find' in options:
        options.remove('-find')
        axioms_filename = None
        lemmas_filename = options.pop()        
    else:
        axioms_filename = options.pop()
        lemmas_filename = options.pop()
    prove (lemmas_filename, 'log/lemma_summary.log', axioms_filename=axioms_filename, options=options)
    
