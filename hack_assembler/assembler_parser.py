#!/bin/python

def RemoveComment(sentense):
    result = sentense
    if '//' in result:
        index = result.find('//')
        result = result[0:index]
    return result

# remove white space  and \n
def RemoveWhiteSpace(sentense):
    result = sentense
    while ' ' in result:
        index = result.find(' ')
        result = result[0:index] + result[index+1:]
    while '\n' in result:
        index = result.find('\n')
        result = result[0:index] + result[index+1:]
    while '\r' in result:
        index = result.find('\r')
        result = result[0:index] + result[index+1:]
    return result

valid_char = ['_','.','$']

def IsValidChar(char):
    return str(char).isalpha() or char in valid_char or str(char).isdigit()


def SegmentInstruction(sentense):
    
    def inner_segment(sentense,result):
        if not sentense:
            return 
        index = 0
        if sentense[0].isalpha():
            for i in range(len(sentense)):
                if IsValidChar(sentense[i]):
                    index = i
                else:
                    break
        elif sentense[0].isdigit():
            for i in range(len(sentense)):
                if sentense[i].isdigit():
                    index = i  
                else:
                    break          
        result.append(sentense[0:index+1])
        inner_segment(sentense[index+1:],result)            
    
    result = []
    inner_segment(sentense,result)
    return result



class Parser:
    def __self__(self):
        pass

    def Process(self,sentense):
        sentense = RemoveComment(sentense)
        if not sentense:
            return []
        sentense = RemoveWhiteSpace(sentense)
        if not sentense:
            return []
        return SegmentInstruction(sentense)


if __name__ == '__main__':
    test_parser = Parser()

    result = test_parser.Process('  // asdasdsd')
    print(result)

    result = test_parser.Process('  (ABC)')
    print(result)

    result = test_parser.Process('@ASD')
    print(result)

    result = test_parser.Process('@123 // asdse')
    print(result)

    result = test_parser.Process('0;JMP')
    print(result)

    result = test_parser.Process('AMD=D+1;JGE')
    print(result)

    result = test_parser.Process('(OUTPUT_FIRST)')
    print(result)

    result = test_parser.Process('@R123')
    print(result)

    result = test_parser.Process('@ifshishie_23.123$123')
    print(result)

    result = test_parser.Process('(ifshishie_23.123$123)')
    print(result)