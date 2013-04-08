from src import *

class Reasoner (object):
    
    MODEL_FINDER = 'MODEL_FINDER'
    
    PROVER = 'PROVER'
        
    # initialize
    def __init__(self, name, type=None, id=None):
        self.identifier = ''
        
        self.type = Reasoner.PROVER
        
        self.args = []
        
        self.positive_returncodes = []
        
        self.unknown_returncodes = []
        
        self.modules = []
        
        self.output_file = ''
        
        self.return_code = None
        
        self.output = None

        self.name = name
        if type:
            self.type = type
        if id:
            self.identifier = id
        else:
            self.identifier = name
        self.positive_returncodes = commands.get_positive_returncodes(self.name)
        self.unknown_returncodes = commands.get_unknown_returncodes(self.name)
        self.return_code = None

    def __eq__ (self, other):
        if not isinstance(other, Reasoner):
            return False
        if self.identifier == other.identifier:
            return True
        else:
            return False
        
    def __ne__ (self, other):
        return not self.eq(other)

    def constructCommand (self, modules, outfile_stem):
        """Construct the command to invoke the reasoner."""
        self.modules = modules
        self.output_file = outfile_stem + filemgt.read_config(self.name,'ending')
        self.args = commands.get_system_command(self.name, self.modules, self.output_file)
        return self.args
    
    def getCommand (self, modules=None, outfile_stem=None):
        """Return the command (includes constructing it if necessary) to invoke the reasoner."""
        if not modules:
            return self.args
        else:
            self.construct_command(modules, outfile_stem)
            return self.args
    
    def getOutfile(self):
        return self.output_file        

    def isProver (self):
        if self.type==Reasoner.PROVER: return True
        else: return False
        
    def terminatedSuccessfully (self):
    
        def success_default (self):
            if not self.return_code==None:
                if self.return_code in self.positive_returncodes:
                    return True
            return False

        def success_paradox (self):
            file = open(self.output_file, 'r')
            lines = file.readlines()
            output_lines = filter(lambda x: x.startswith('+++ RESULT:'), lines)
            if len(output_lines)!=1:
                self.return_code = 0
            else:
                if 'CounterSatisfiable' in output_lines[0]:
                    self.return_code = -1
                elif 'Satisfiable' in output_lines[0]:
                    self.return_code = 1
                else:
                    self.return_code = 0
            
            mapping = {
                -1: False,
                0 : False,
                1 : True,
            }
            
            return mapping[self.return_code]
        
    
        handlers = {
            "paradox": success_paradox, 
        }
    
        return handlers.get(self.name, success_default)(self)
     
     
    def terminatedUnknowingly (self):

        def unknown_default (self):
            if not self.return_code==None:
                if self.return_code in self.unknown_returncodes:
                    return True
            return False
        
        def unknown_paradox (self):
            self.terminatedSuccessfully()

            mapping = {
                -1: False,
                0 : True,
                1 : False,
            }
            
            return mapping[self.return_code]
        
        handlers = {
            "paradox": unknown_paradox, 
        }
    
        return handlers.get(self.name, unknown_default)(self)
        
        
    def setReturnCode(self, rc):
        self.return_code = rc
                
    def isDone (self):
        return self.return_code