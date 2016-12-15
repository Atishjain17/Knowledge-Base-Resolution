import collections
import copy
import time

start=time.time()
global allocated_query_time
global query_start_time
total_time=30
input_file = open('input.txt', 'r')
input = input_file.read()
input_file.close()
input = input.split('\n')

# Assigining input values
# No of Queries, Queries, No. of sentences in Knowledge Base, Sentences
kb = []
knowledge_base = []
global argu
argu = 0
no_Of_Queries = int(input[0].replace(' ', ''))
# Taking queries
queries_temp = []
last_query_line_no = no_Of_Queries + 1
for i in range(1, last_query_line_no):
    queries_temp.append(input[i])
queries = []
for i in range(len(queries_temp)):
    queries.append(queries_temp[i].replace(' ', ''))
# Finished taking queries

# Taking KB sentences
no_Of_Sentence = int(input[last_query_line_no].replace(' ', ''))
sentences_temp = []
last_line = last_query_line_no + no_Of_Sentence + 1
for i in range(last_query_line_no + 1, last_line):
    sentences_temp.append(input[i])
sentences = []
for i in range(len(sentences_temp)):
    sentences.append(sentences_temp[i].replace(' ', ''))

# Input taken
print(queries)
###print(sentences)


# Create sentence node
class Node_Sent(object):
    """A class that makes a queue type table of nodes"""

    def __init__(self, predicate, is_negative, variable,constant):
        self.predicate = predicate
        self.is_negative = is_negative
        self.variable = variable
        self.constant=constant

    def description(self):
        return "Predicate is %s, is_negative %s, variables is %s, constant position is %s" % (self.predicate, self.is_negative, self.variable, self.constant)
### Node_Sent Class Created

# Convert knowledge base sentences to prefix
def precedence(ch):
    if (ch == '('):
        return 0
    elif (ch == ')'):
        return 1
    elif (ch == '~'):
        return 5
    elif (ch == '&'):
        return 4
    elif (ch == '|'):
        return 3
    elif (ch == '=>'):
        return 2


def infix_to_prefix(sent):
    prefix_list = []
    prefix_stack = []
    for i in range(len(sent) - 1, -1, -1):
        if (sent[i] != '(' and sent[i] != ')' and sent[i] != '&' and sent[i] != '|' and sent[i] != '~' and sent[
            i] != '=>'):
            prefix_list.append(sent[i])
        elif (prefix_stack == [] or sent[i] == ')' or precedence(sent[i]) >= precedence(prefix_stack[-1])):
            prefix_stack.append(sent[i])
        elif (sent[i] == '('):
            while (prefix_stack[-1] != ')'):
                char = prefix_stack.pop()
                prefix_list.append(char)
            prefix_stack.pop()
        else:
            while (prefix_stack != [] and precedence(sent[i]) < precedence(prefix_stack[-1])):
                prefix_list.append(prefix_stack.pop())
            prefix_stack.append(sent[i])
    while (prefix_stack != []):
        prefix_list.append(prefix_stack.pop())
    list = []
    for i in range(len(prefix_list) - 1, -1, -1):
        # #print(prefix_list[i],end='')
        list.append(prefix_list[i])
    # #print('')
    return list


def flatten(xs):
    result = []
    if isinstance(xs, (list, tuple)):
        for x in xs:
            result.extend(flatten(x))
    else:
        result.append(xs)
    return result


def negate(sent1):
    # #print('negation')
    ans = []
    sent1 = flatten(sent1)
    for i in range(len(sent1)):
        if (sent1[i] == '~'):
            continue
        elif (sent1[i] == '('):
            ans.append('(')
        elif (sent1[i] == ')'):
            ans.append(')')
        elif (sent1[i] == '&'):
            ans.append('|')
        elif (sent1[i] == '|'):
            ans.append('&')
        elif (sent1[i - 1] != '~'):
            ans.append('~')
            ans.append(sent1[i])
        elif (sent1[i - 1] == '~'):
            ans.append(sent1[i])
    return ans


def negate1(sent1):
    # #print('negation')
    ans = []
    ans.append('~')
    sent1 = flatten(sent1)
    for i in range(len(sent1)):
        if (sent1[i] == '(' or sent1[i] == ')'):
            continue
        else:
            ans.append(sent1[i])
    return ans


def conjunction1(sent1, sent2):
    ans = []
    sent1 = flatten(sent1)
    sent2 = flatten(sent2)
    ans.append(sent1)
    ans.append('&')
    ans.append(sent2)
    return ans


def conjunction(sent1, sent2):
    ans = []
    sent1 = flatten(sent1)
    sent2 = flatten(sent2)
    ans.append('(')
    ans.append(sent1)
    ans.append('&')
    ans.append(sent2)
    ans.append(')')
    return ans


def disjunction1(sent1, sent2):
    ans = []
    ans1 = []
    sent1 = flatten(sent1)
    sent2 = flatten(sent2)
    start = 0
    p1 = []
    sent1.append('&')
    for position, char in enumerate(sent1):
        if char == '&':
            p1.append(sent1[start:position])
            start = position + 1

    start = 0
    p2 = []
    sent2.append('&')
    for position, char in enumerate(sent2):
        if char == '&':
            p2.append(sent2[start:position])
            start = position + 1

    for i in range(len(p1)):
        for j in range(len(p2)):
            temp = []
            temp.append(p1[i])
            temp.append('|')
            temp.append(p2[j])
            ans1.append(temp)
    for i in range(len(ans1)):
        ans.append(ans1[i])
        ans.append('&')
    ans.pop(-1)
    return ans


def disjunction(sent1, sent2):
    ans = []
    sent1 = flatten(sent1)
    sent2 = flatten(sent2)
    ans.append('(')
    ans.append(sent1)
    ans.append('|')
    ans.append(sent2)
    ans.append(')')
    return ans


def implication(sent1, sent2):
    ans = []
    sent1 = flatten(sent1)
    sent2 = flatten(sent2)
    sent3 = flatten(negate(sent1))
    ans.append(disjunction(sent3, sent2))
    return ans


def evaluate_prefix(list):
    prefix_stack = []
    for i in range(len(list) - 1, -1, -1):
        if (list[i] != '&' and list[i] != '|' and list[i] != '~' and list[i] != '=>'):
            prefix_stack.append(list[i])
        elif (list[i] == '~'):
            predicate1 = []
            predicate1.append(prefix_stack.pop())
            ans = negate(predicate1)
            prefix_stack.append(ans)
        else:
            predicate1 = []
            predicate2 = []
            predicate1.append(prefix_stack.pop())
            predicate2.append(prefix_stack.pop())
            if (list[i] == '&'):
                ans = conjunction(predicate1, predicate2)
                prefix_stack.append(ans)
            elif (list[i] == '|'):
                ans = disjunction(predicate1, predicate2)
                prefix_stack.append(ans)
            elif (list[i] == '=>'):
                ans = implication(predicate1, predicate2)
                prefix_stack.append(ans)
    return (prefix_stack)


def evaluate_prefix1(list):
    prefix_stack = []
    for i in range(len(list) - 1, -1, -1):
        if (list[i] != '&' and list[i] != '|' and list[i] != '~'):
            prefix_stack.append(list[i])
        elif (list[i] == '~'):
            predicate1 = []
            predicate1.append(prefix_stack.pop())
            ans = negate1(predicate1)
            prefix_stack.append(ans)
        else:
            predicate1 = []
            predicate2 = []
            predicate1.append(prefix_stack.pop())
            predicate2.append(prefix_stack.pop())
            if (list[i] == '&'):
                ans = conjunction1(predicate1, predicate2)
                prefix_stack.append(ans)
            elif (list[i] == '|'):
                ans = disjunction1(predicate1, predicate2)
                prefix_stack.append(ans)
    return (prefix_stack)


# Convert prefixed knowledge base sentences to CNF form
def to_cnf(sent, dicti):
    start = 0
    p1 = []
    sent.append('&')
    for i in range(len(sent)):
        temp = dicti.get(sent[i])
        if (temp != None):
            sent[i] = temp

    for position, char in enumerate(sent):
        if char == '&':
            p1.append(sent[start:position])
            start = position + 1
    for i in range(len(p1)):
        kb.append(p1[i])


def standardize_variable(sent,knowledge_base):
    global argu
    curr_sent = copy.deepcopy(sent)
    curr_sent.append('|')
    individual_list = []
    temp = []
    vardict = {}
    start = 0
    for position, char in enumerate(curr_sent):
        if char == '|':
            individual_list.append(curr_sent[start:position])
            start = position + 1
    for j in range(len(individual_list)):
        individual_sent = copy.deepcopy(individual_list[j])
        ##print(individual_sent)
        neg = 0
        constant=[]
        for w in range(len(individual_sent)):
            if (individual_sent[w] == '~'):
                neg = 1
                continue
            else:
                curr_predicate = individual_sent[w]
                ##print(curr_predicate)
                curr_predicate = curr_predicate.replace(')', '')
                curr_predicate = curr_predicate.split('(')
                curr_pred = curr_predicate[1].split(',')
                for t in range(len(curr_pred)):
                    if (curr_pred[t] in vardict):
                        curr_pred[t]= vardict[curr_pred[t]]
                    elif(curr_pred[t][0].isupper()==False):
                        vardict[curr_pred[t]] = "arg" + str(argu)
                        curr_pred[t]= vardict[curr_pred[t]]
                        argu =argu + 1
                    else:
                        constant.append(t)
                        continue
                ##print(curr_pred)
        temp.append(Node_Sent(curr_predicate[0], neg, curr_pred,constant))
    knowledge_base.append(temp)


def printkb(kb):
    for i in range(len(kb)):
        for j in range(len(kb[i])):
            print(kb[i][j].description(), end=' __|__ ')
        print('')


def unification(knowledge_base_2,q1,q_ind_1,q2,q_ind_2,temp_kb):
    global argu
    argument=argu
    temp_dict={}
    temp_sent=[]

    for i in range(len(knowledge_base_2[q2][q_ind_2].variable)):
        if(knowledge_base_2[q2][q_ind_2].variable[i][0].isupper() and knowledge_base_2[q1][q_ind_1].variable[i][0].isupper()):
            if(knowledge_base_2[q2][q_ind_2].variable[i]!=knowledge_base_2[q1][q_ind_1].variable[i]):
                return 0
            else:
                temp_dict[knowledge_base_2[q1][q_ind_1].variable[i]]=knowledge_base_2[q1][q_ind_1].variable[i]
        elif(knowledge_base_2[q2][q_ind_2].variable[i][0].isupper()):
            if(knowledge_base_2[q1][q_ind_1].variable[i] not in temp_dict):
                temp_dict[knowledge_base_2[q1][q_ind_1].variable[i]]=knowledge_base_2[q2][q_ind_2].variable[i]
            elif(temp_dict[knowledge_base_2[q1][q_ind_1].variable[i]][0].islower()):
                v=temp_dict[knowledge_base_2[q1][q_ind_1].variable[i]]
                for key, value in temp_dict.items():
                    if(value==v):
                        temp_dict[key]=knowledge_base_2[q2][q_ind_2].variable[i]
            elif(temp_dict[knowledge_base_2[q1][q_ind_1].variable[i]]!=knowledge_base_2[q2][q_ind_2].variable[i]):
                return 0
        elif(knowledge_base_2[q1][q_ind_1].variable[i][0].isupper()):
            if(knowledge_base_2[q2][q_ind_2].variable[i] not in temp_dict):
                temp_dict[knowledge_base_2[q2][q_ind_2].variable[i]]=knowledge_base_2[q1][q_ind_1].variable[i]
            elif(temp_dict[knowledge_base_2[q2][q_ind_2].variable[i]][0].islower()):
                v=temp_dict[knowledge_base_2[q2][q_ind_2].variable[i]]
                for key, value in temp_dict.items():
                    if(value==v):
                        temp_dict[key]=knowledge_base_2[q1][q_ind_1].variable[i]
            elif(temp_dict[knowledge_base_2[q2][q_ind_2].variable[i]]!=knowledge_base_2[q1][q_ind_1].variable[i]):
                return 0
        else:
            if(knowledge_base_2[q2][q_ind_2].variable[i] not in temp_dict and knowledge_base_2[q1][q_ind_1].variable[i] not in temp_dict):
                temp_dict[knowledge_base_2[q2][q_ind_2].variable[i]]="arg" + str(argument)
                temp_dict[knowledge_base_2[q1][q_ind_1].variable[i]]="arg" + str(argument)
                argument=argument+1
            elif(knowledge_base_2[q2][q_ind_2].variable[i] in temp_dict and knowledge_base_2[q1][q_ind_1].variable[i] not in temp_dict):
                temp_dict[knowledge_base_2[q1][q_ind_1].variable[i]]=temp_dict[knowledge_base_2[q2][q_ind_2].variable[i]]
            elif(knowledge_base_2[q1][q_ind_1].variable[i] in temp_dict and knowledge_base_2[q2][q_ind_2].variable[i] not in temp_dict):
                temp_dict[knowledge_base_2[q2][q_ind_2].variable[i]]=temp_dict[knowledge_base_2[q1][q_ind_1].variable[i]]
            else:
                v1=temp_dict[knowledge_base_2[q2][q_ind_2].variable[i]]
                v2=temp_dict[knowledge_base_2[q1][q_ind_1].variable[i]]
                if(v1[0].isupper() and v2[0].isupper()):
                    if(v1!=v2):
                        return 0
                elif(v1[0].isupper()):
                    for key, value in temp_dict.items():
                        if(value==v2):
                            temp_dict[key]=v1
                elif(v2[0].isupper()):
                    for key, value in temp_dict.items():
                        if(value==v1):
                            temp_dict[key]=v2
                else:
                    for key, value in temp_dict.items():
                        if(value==v2):
                            temp_dict[key]=v1

    for i in range(len(knowledge_base_2[q1])):
        if(i!=q_ind_1):
            var=[]
            const=[]
            for j in range(len(knowledge_base_2[q1][i].variable)):
                if(knowledge_base_2[q1][i].variable[j] not in temp_dict):
                    if(knowledge_base_2[q1][i].variable[j][0].islower()):
                        temp_dict[knowledge_base_2[q1][i].variable[j]]="arg" + str(argument)
                        argument=argument+1
                    else:
                        temp_dict[knowledge_base_2[q1][i].variable[j]]=knowledge_base_2[q1][i].variable[j]
                curr_var=temp_dict[knowledge_base_2[q1][i].variable[j]]
                var.append(curr_var)
                if(curr_var[0].isupper()):
                    const.append(j)
            temp_node=Node_Sent(knowledge_base_2[q1][i].predicate, knowledge_base_2[q1][i].is_negative, var,const)
            if any(x.description()==temp_node.description() for x in temp_sent) != True:
                temp_sent.append(temp_node)
    for i in range(len(knowledge_base_2[q2])):
        if(i!=q_ind_2):
            var=[]
            const=[]
            for j in range(len(knowledge_base_2[q2][i].variable)):
                if(knowledge_base_2[q2][i].variable[j] not in temp_dict):
                    if(knowledge_base_2[q2][i].variable[j][0].islower()):
                        temp_dict[knowledge_base_2[q2][i].variable[j]]="arg" + str(argument)
                        argument=argument+1
                    else:
                        temp_dict[knowledge_base_2[q2][i].variable[j]]=knowledge_base_2[q2][i].variable[j]
                curr_var=temp_dict[knowledge_base_2[q2][i].variable[j]]
                var.append(curr_var)
                if(curr_var[0].isupper()):
                    const.append(j)
            temp_node=Node_Sent(knowledge_base_2[q2][i].predicate, knowledge_base_2[q2][i].is_negative, var,const)
            if any(x.description()==temp_node.description() for x in temp_sent) != True:
                temp_sent.append(temp_node)
    if(temp_sent==[]):
        #print('UNIFIED')
        return 1
    argu=argument
    temp_kb.append(temp_sent)

    return 2


def printkbsent(sent):
    for i in range(len(sent)):
        print(sent[i].description(), end=' __|__ ')
    print('')


def sent_match(dict_1,dict_2):
    sorted(dict_1)
    sorted(dict_2)
    d1={}
    d2={}
    for k1 in dict_1:
        l=dict_1[k1]
        l.sort()
        str1 = ''.join(str(l))
        if str1 not in d1:
            d1[str1]=[k1]
        else:
            d1[str1].append(k1)

    for k1 in dict_2:
        l=dict_2[k1]
        l.sort()
        str1 = ''.join(str(l))
        if str1 not in d2:
            d2[str1]=[k1]
        else:
            d2[str1].append(k1)
    if set(d1.keys()) == set(d2.keys()):
        flag=0
        for key in d1:
            v1=d1[key]
            v2=d2[key]
            v1.sort()
            v2.sort()
            if(len(v1)==len(v2)):
                for e in range(len(v1)):
                    if(v1[e][0].isupper() or v2[e][0].isupper()):
                        if v1[e]==v2[e]:
                            continue
                        else:
                            flag=1
                            break
            else:
                flag=1
                break
            if(flag==1):
                break
    else:
        flag=1
    if(flag!=1):
        #print('Match')
        return 1
    else:
        #print('No match')
        return 0


def find_unique_sent(knowledge_base_2, temp_kb,leng_kb):

    for j in range(leng_kb):
        t1=[]
        count=0
        for i in range(len(temp_kb)):
            match=0
            if(len(temp_kb[i])==len(knowledge_base_2[j])):
                pred_list_temp=[]
                pred_list_orig=[]
                for q in range(len(temp_kb[i])):
                    pred_list_temp.append([temp_kb[i][q].predicate,temp_kb[i][q].is_negative,temp_kb[i][q].constant])
                    pred_list_orig.append([knowledge_base_2[j][q].predicate,knowledge_base_2[j][q].is_negative,knowledge_base_2[j][q].constant])
                pred_list_temp.sort()
                pred_list_orig.sort()
                if(pred_list_temp == pred_list_orig):       #positioning same, now check for variables
                    temp_dict={}
                    orig_dict={}
                    for q in range(len(temp_kb[i])):
                        temp_var=temp_kb[i][q].variable
                        orig_var=knowledge_base_2[j][q].variable
                        for w in range (len(temp_var)):
                            temp_pred=[temp_kb[i][q].predicate,temp_kb[i][q].is_negative,w]
                            if temp_var[w] not in temp_dict:
                                temp_dict[temp_var[w]]=[temp_pred]
                            else:
                                temp_dict[temp_var[w]].append(temp_pred)
                        for w in range (len(orig_var)):
                            orig_pred=[knowledge_base_2[j][q].predicate,knowledge_base_2[j][q].is_negative,w]
                            if orig_var[w] not in orig_dict:
                                orig_dict[orig_var[w]]=[orig_pred]
                            else:
                                orig_dict[orig_var[w]].append(orig_pred)
                    match=sent_match(temp_dict,orig_dict)
                    if(match==1):
                        t1.append(i)
        for w in range (len(t1)):
            x=t1[w]-count
            count=count+1
            del temp_kb[x]

    return temp_kb


def resolution(knowledge_base_2,length_kb):
    temp_kb=[]
    ans=0
    for q1 in range(length_kb):
        for q_ind_1 in range(len(knowledge_base_2[q1])):
            for q2 in range(q1+1,len(knowledge_base_2),1):
                for q_ind_2 in range(len(knowledge_base_2[q2])):
                    if(knowledge_base_2[q1][q_ind_1].predicate == knowledge_base_2[q2][q_ind_2].predicate and knowledge_base_2[q1][q_ind_1].is_negative != knowledge_base_2[q2][q_ind_2].is_negative):
                        #print('!!!')
                        #printkbsent(knowledge_base_2[q1])
                        #printkbsent(knowledge_base_2[q2])
                        ret=unification(knowledge_base_2,q1,q_ind_1,q2,q_ind_2,temp_kb)
                        if(ret==1):
                            ans=1
                            #print('Unified')
                            return 1
                    if(allocated_query_time<time.time()-query_start_time):
                            return 0

                if(allocated_query_time<time.time()-query_start_time):
                        return 0

    t1=find_unique_sent(knowledge_base_2,temp_kb,len(knowledge_base_2))
    #print()
    z=len(knowledge_base_2)
    while (len(t1) !=0 ):
        s=t1.pop(0)
        knowledge_base_2.insert(0,s)
        t1=find_unique_sent(knowledge_base_2,t1,1)
        #print()
        if(allocated_query_time<time.time()-query_start_time):
           return 0
    y=len(knowledge_base_2)
    #print('____')
    #printkb(knowledge_base_2)
    #print('$$$')
    change_len=y-z
    if(change_len!=0):
        ans=resolution(knowledge_base_2,change_len)
    return ans
##main program

k = 1
for i in range(len(sentences)):
    curr_sent = sentences[i]
    dict = collections.OrderedDict()
    flag = 0
    predicate_string = ""
    predicate_list = []
    for j in range(len(curr_sent)):
        if (curr_sent[j].isupper()):
            flag = 1
        if (curr_sent[j] == ')' and flag == 1):
            flag = 0
            predicate_string = predicate_string + curr_sent[j]
            dict["p" + str(k)] = predicate_string
            predicate_list.append("p" + str(k))
            k = k + 1
            predicate_string = ""
        elif (flag == 1):
            predicate_string = predicate_string + curr_sent[j]
        elif (curr_sent[j] == '='):
            implies = curr_sent[j] + curr_sent[j + 1]
        elif (curr_sent[j] == '>'):
            predicate_list.append(implies)
        else:
            predicate_list.append(curr_sent[j])
    #print(curr_sent)
    prefix_list = infix_to_prefix(predicate_list)
    prefix_ans = evaluate_prefix(prefix_list)
    prefix_ans = flatten(prefix_ans)
    prefix_list1 = infix_to_prefix(prefix_ans)
    prefix_ans1 = evaluate_prefix1(prefix_list1)
    prefix_ans1 = flatten(prefix_ans1)
    to_cnf(prefix_ans1, dict)

for i in range(len(kb)):
    standardize_variable(kb[i],knowledge_base)
##printkb(knowledge_base)

####Unification and Resolution
for i in range(no_Of_Queries):
    print('allocated_query_time: ',end='')
    allocated_query_time=28
    print(allocated_query_time)
    query_start_time=time.time()
    kb_2=copy.deepcopy(knowledge_base)
    temp_l=[]
    curr_query = queries[i]
    flag = 0
    predicate_string = ""
    predicate_list = []
    for j in range(len(curr_query)):
        if (curr_query[j].isupper()):
            flag = 1
        if (curr_query[j] == ')' and flag == 1):
            flag = 0
            predicate_string = predicate_string + curr_query[j]
            predicate_list.append(predicate_string)
            predicate_string = ""
        elif (flag == 1):
            predicate_string = predicate_string + curr_query[j]
        else:
            predicate_list.append(curr_query[j])
    predicate_list.insert(0,'~')
    predicate_list.insert(1,'(')
    predicate_list.append(')')
    prefix_list = infix_to_prefix(predicate_list)
    prefix_ans = evaluate_prefix(prefix_list)
    prefix_ans = flatten(prefix_ans)
    standardize_variable(prefix_ans,temp_l)
    for j in range(len(temp_l)):
        kb_2.insert(0,temp_l[j])
    soln=resolution(kb_2,len(kb_2))
    if(soln==1):
        print('TRUE')
        f = open("output.txt", "a")
        f.write("TRUE"+"\n")
        f.close()
    else:
        print('FALSE')
        f = open("output.txt", "a")
        f.write("FALSE"+"\n")
        f.close()
    print('query used time:',end='')
    print(time.time()-query_start_time)
    #printkb(kb_2)