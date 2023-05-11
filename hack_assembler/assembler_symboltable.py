

from utilis import AssemblerException


BuiltInSymbolTable = {
    'R0':0,
    'R1':1,
    'R2':2,
    'R3':3,
    'R4':4,
    'R5':5,
    'R6':6,
    'R7':7,
    'R8':8,
    'R9':9,
    'R10':10,
    'R11':11,
    'R12':12,
    'R13':13,
    'R14':14,
    'R15':15,
    'SCREEN':16384,
    'KBD':24576,
    'SP':0,
    'LCL':1,
    'ARG':2,
    'THIS':3,
    'THAT':4,
}

class SymbolTable:
    def __init__(self):
        self.variable = {}
        self.label = {}
        self.variable_addr = 16
        self.line_count = 0

    def DetectLabels(self,segments):
        if '(' in segments:
            self.label[segments[1]] = None
            return
    
    def DetectVariable(self,segments):
        if '@' in segments:
            label = segments[1]
            if label.isdigit():
                return 
            if label not in self.label and label not in self.variable and label not in BuiltInSymbolTable:
                self.variable[segments[1]] = self.variable_addr
                self.variable_addr += 1  
            return 
    
    def DetectValueofLabel(self,segments):
        if not segments:
            return 
        if '(' in segments:
            label = segments[1]
            self.label[label] = self.line_count
            return
        self.line_count +=1
        print('line_count',self.line_count)
        return 
    
    def Reset(self):
        self.variable = {}
        self.label = {}
        self.variable_addr = 16
        self.line_count = 0

    def Process(self,segments):
        if not segments:
            return []
        new_segments=list(segments)
        if '@' in segments and  not segments[1].isdigit():
            label = segments[1]
            if label in BuiltInSymbolTable:
                new_segments[1] = BuiltInSymbolTable[label]
                return new_segments
            if label in self.variable:
                new_segments[1] = self.variable[label]
                return new_segments
            if label in self.label:
                new_segments[1] = self.label[label]
                return new_segments
            raise AssemblerException('label {0} is not in any symbol table, please check'.format(label))
        return new_segments

if __name__ == '__main__':
    symboltable = SymbolTable()

    symboltable.DetectLabels([])
    symboltable.DetectLabels([])
    symboltable.DetectLabels([])
    symboltable.DetectLabels(['@','tmp_var1'])
    symboltable.DetectLabels(['@','tmp_var2'])
    symboltable.DetectLabels(['(','TMP_LABEL1',')'])
    symboltable.DetectLabels(['@','tmp_var3'])
    symboltable.DetectLabels(['@','TMP_LABEL2'])
    symboltable.DetectLabels(['@','tmp_var4'])
    symboltable.DetectLabels(['(','TMP_LABEL2',')'])
    symboltable.DetectLabels(['@','TMP_LABEL1'])


    symboltable.DetectVariable([])
    symboltable.DetectVariable([])
    symboltable.DetectVariable([])
    symboltable.DetectVariable(['@','tmp_var1'])
    symboltable.DetectVariable(['@','tmp_var2'])
    symboltable.DetectVariable(['(','TMP_LABEL1',')'])
    symboltable.DetectVariable(['@','tmp_var3'])
    symboltable.DetectVariable(['@','TMP_LABEL2'])
    symboltable.DetectVariable(['@','tmp_var4'])
    symboltable.DetectVariable(['(','TMP_LABEL2',')'])
    symboltable.DetectVariable(['@','TMP_LABEL1'])

    symboltable.DetectValueofLabel([])
    symboltable.DetectValueofLabel([])
    symboltable.DetectValueofLabel([])
    symboltable.DetectValueofLabel(['@','tmp_var1'])
    symboltable.DetectValueofLabel(['@','tmp_var2'])
    symboltable.DetectValueofLabel(['(','TMP_LABEL1',')'])
    symboltable.DetectValueofLabel(['@','tmp_var3'])
    symboltable.DetectValueofLabel(['@','TMP_LABEL2'])
    symboltable.DetectValueofLabel(['@','tmp_var4'])
    symboltable.DetectValueofLabel(['(','TMP_LABEL2',')'])
    symboltable.DetectValueofLabel(['@','TMP_LABEL1'])

    new_segments = symboltable.Process(['@','TMP_LABEL1'])

    print('variable',symboltable.variable)
    print('label',symboltable.label)
    print('new_segments',new_segments)
