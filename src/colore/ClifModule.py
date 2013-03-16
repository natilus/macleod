'''
Created on 2012-03-07
Refactored on 2013-03-16

@author: Torsten Hahmann
'''
import os, filemgt, process, clif
from sets import Set

class ClifModule(object):

    module_name = ''
    
    depth = 0
    
    """set of all imported module names """
    imports = Set([])
    
    clif_file_name = ''
    
    """Location of the clif input file that has undergone preprocessing"""
    clif_processed_file_name = ''
    
    p9_file_name = ''
    
    # the distinction between nonlogical_symbols and nonlogical_variables assumes that a single symbol is not used as both in different sentences
    nonlogical_symbols = Set([])
    nonlogical_variables = Set([])
        
    '''
    classdocs
    '''
    def __init__(self,module_name,depth):
        '''
        Constructor
        '''
        self.clif = True
        self.module_name = ClifModule.get_simple_module_name(module_name)
        print 'processing module: ' + self.module_name
        # remove any obsolete URL prefix as specified in the configuration file
        if self.module_name.endswith(filemgt.read_config('cl','ending')):
            self.module_name = self.module_name.replace(filemgt.read_config('cl','ending'),'')
        
        # stores the depth of the import hierarchy
        self.depth = depth
        
        # add the standard ending for CLIF files to the module name
        self.clif_file_name = os.path.abspath(self.module_name + filemgt.read_config('cl','ending'))

        self.clif_processed_file_name = os.path.abspath(filemgt.get_name_with_subfolder(self.module_name, 
                                                                        filemgt.read_config('converters','tempfolder'), 
                                                                        filemgt.read_config('cl','ending')))

        #print self.clif_file_name
        #print self.clif_processed_file_name
        
        clif.remove_all_comments(self.clif_file_name,self.clif_processed_file_name)
        
        self.imports =  [self.get_simple_module_name(i) for i in clif.get_imports(self.clif_processed_file_name)]
        
        print self.imports
        
        self.compute_nonlogical_symbols(self.clif_processed_file_name)
        
        # push nonlogical symbols and variables upwards (VERY LAST STEP)
#        if isinstance(parent, ClifModule):
#            parent.nonlogical_symbols.append[self.nonlogical_symbols]
#            parent.nonlogical_variables.append[self.nonlogical_variables]

    @staticmethod
    def get_simple_module_name(name):
        import re
        prefix = re.compile(re.escape(filemgt.read_config('cl','prefix')), re.IGNORECASE)
        prefix.sub('', name)
        return name
        
            
    
    def get_nonlogical_symbols(self):
        return self.nonlogical_symbols
    
    def get_depth(self):
        return depth
                

    # extract all nonlogical symbols (predicate and function symbols) from the preprocessed clif file
    def compute_nonlogical_symbols (self,input_file_name):
        

        cl_file = open(input_file_name, 'r')
        line = cl_file.readline()
        while line:
            self.nonlogical_symbols |= clif.get_logical_symbols_from_single_line(line)
            self.nonlogical_variables |= clif.get_quantified_variables_from_single_line(line)
            line = cl_file.readline()

        cl_file.close()
        
        self.nonlogical_symbols -= self.nonlogical_variables
        print "Nonlogical symbols: " + str(self.nonlogical_symbols)
        print "Variables: " + str(self.nonlogical_variables)
        

    def get_p9_file_name (self):
        """get the filename of the LADR translation of the module"""
        self.p9_file_name =  filemgt.get_name_with_subfolder(self.module_name, 
                                                             filemgt.read_config('ladr','folder'), 
                                                             filemgt.read_config('ladr','ending'))
        return self.p9_file_name
    

    def convert_to_ladr(self):
        """translate the module into the LADR syntax"""
        self.get_p9_file_name()
        commands.get_clfi_to_p9_cmd(self.clif_processed_file_name, self.p9_file_name)
        process.executeSubprocess(command)
        return self.p9_file_name

        
if __name__ == '__main__':
    import sys
    # global variables
    options = sys.argv
    m = ClifModule(options[1],0)
