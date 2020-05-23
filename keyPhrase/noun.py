s_1 = '去美国留学，选择一个适合自己的学校很重要，选择一个好的城市也同样重要'
s_2 = '在大城市，学生不仅能增长见识，还能享受到大城市的便利，接触到不一样的社会层面'
s_3 = '今天，小编为大家介绍一下美国最适合留学的几个城市'
s_4 = '旧金山湾区是世界最重要的科教文化中心之一，' \
      '坐拥斯坦福大学和加州大学伯克利分校两大世界知名高校，' \
      '以及世界顶级医学中心加州大学旧金山分校，在众多兄弟城市中独占鳌头'
s_5 = '旧金山更是高科技产业的天堂，由于临近世界著名高新技术产业区硅谷，而且在旧金山求学的学子也备受雇主青睐。'
s_6 = '此外，旧金山也是一座气候宜人的海港城市，多民族、种族融合在一起，每个月都有独具特色的文化节日。'
s_7 = '波士顿是美国东北部高等教育和医疗保健的中心，是全美人口受教育程度最高的城市。'
s_8 = '拥有塔夫斯大学、波士顿学院、波士顿大学、布兰迪斯大学和东北大学等全美名校，可能大街上与你擦肩而过的就是各校的精英。'
s_9 = '波士顿在经济、文化及娱乐产业上也是声名赫赫，可以说波士顿是一座全面发展、综合实力非常强的城市。'

LTP_DATA_DIR = 'C:/Users/david/Desktop/site/django site/knowledge/ltp_data_v3.4.0'
from pyltp import SentenceSplitter
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
from pyltp import SementicRoleLabeller
import copy
from pyhanlp import *

sents = SentenceSplitter.split(s_1)  # 分句
whole_sent = s_1
sents_list = []
for sent in sents:
    for s in sent.split('，'):
        sents_list.append(s)


# 一个list里面可能会有很多相类似的句子或者词汇，如果mode是True，这里把所有重复的句子删掉并且选择其中含有重复内容的较长的句子
# ，例如【'一个适合自己的学校'，'选择一个适合自己的学校很重要'， '一个好的城市'， '选择一个好的城市也同样重要'】
# 这里就选择['选择一个适合自己的学校很重要', '选择一个好的城市也同样重要']
# 如果mode是False，这里把所有重复的句子删掉并且选择其中含有重复内容的较短的句子
# 例如【'一个适合自己的学校'，'选择一个适合自己的学校很重要'， '一个好的城市'， '选择一个好的城市也同样重要'】
# 这里就选择['一个适合自己的学校', '一个好的城市']
def select_longest_or_shortest(sents_list, mode):
    new_sents_list = []
    for sent in sents_list:
        if sent not in new_sents_list:
            new_sents_list.append(sent)
    shortest_list = []
    sents_list_copy = copy.deepcopy(new_sents_list)
    for sent in sents_list_copy:
        for sent_comp in sents_list_copy:
            all_in = True
            for s in sent:
                if s not in sent_comp:
                    all_in = False
            if all_in == True and sent != sent_comp and mode == True:
                try:
                    new_sents_list.remove(sent)
                except:
                    pass
            elif all_in == True and sent != sent_comp and mode == False:
                try:
                    new_sents_list.remove(sent_comp)
                except:
                    pass
    return new_sents_list


# 得到新的words list 根据index 和 head 之间的范围
def update_words_list(words_list_original, index, head):
    words_list_update = ''
    if head < index:
        for i in range(head, index + 1):
            print(words_list_original)
            words_list_update += words_list_original[i]
    elif index < head:
        for i in range(index, head + 1):
            words_list_update += words_list_original[i]
    return words_list_update


# 判断这一个句子里有没有动词或者名词，有则return True，没有则return False
def v_n_included(start, end, postags_list, head):
    if start == end:
        end += 1
    if postags_list[head].startswith('v'):
        return True
    if postags_list[head].startswith('n'):
        return True
    for index in range(start, end):
        if postags_list[index].startswith('v'):
            return True
        if postags_list[index].startswith('n'):
            return True
    return False


# 得到level2 的东西根据实体的位置
def s_update(words_list, arcs_list, index):
    head = arcs_list[index].head - 1
    update_index = [index, head]
    print(update_index)
    words_list_update = ''
    for arc_index in range(len(words_list)):
        if arcs_list[update_index[-1]].head == 0:
            update_index.append(arc_index)
            break
        if arc_index in update_index:
            pass
        elif arc_index == arcs_list[update_index[-1]].head - 1:
            update_index.append(arc_index)
    words_list_update = update_words_list(words_list, min(update_index), max(update_index))
    return words_list_update


# 得到level2 的东西根据实体的位置
def s_update_all(words_list, arcs_list, index):
    head = arcs_list[index].head - 1
    update_index = [index, head]
    all_set = False
    words_list_update = ''
    while all_set == False:
        for arc_index in range(len(words_list)):
            if arcs_list[update_index[-1]].head == 0:
                update_index.append(arc_index)
                all_set = True
                break
            if arc_index in update_index:
                pass
            elif arc_index == arcs_list[update_index[-1]].head - 1:
                update_index.append(arc_index)
                all_set = False
    words_list_update = update_words_list(words_list, min(update_index), max(update_index))
    return words_list_update


# level_1都是实体名词，level_2都是含有实体名词也就是level_1的句子，所以这里删除其他的信息
def level_1_2_relate(level_1_copy, level_2_copy):
    if level_1_copy == []:
        return level_2_copy
    for sent in level_2_copy:
        if level_1_copy[0] in sent:
            return [sent]


# 这里确保level_2和level_3 的信息不重复
def different(level_2_copy, level_3_copy):
    level_3_copy_temp = copy.deepcopy(level_3_copy)
    for sent in level_3_copy:
        if sent in level_2_copy:
            try:
                level_3_copy_temp.remove(sent)
            except:
                pass
    return level_3_copy_temp


# 找到依存句法分析中的root，也就是当arc.head 等于0的时候
def find_root(arcs_list):
    for position in range(len(arcs_list)):
        if arcs_list[position].head == 0:
            return position


# 找到某个index所在的分句，这里按照postags_list 里面的wp（标点符号）来分， 并且return那个句子
def find_section(position, sents_list):
    accumulate = 0
    for sent in sents_list:
        accumulate += len(sent)
        if position < accumulate:
            return sent
        accumulate += 1

# 根据root所在的位置，关联所有与root相关的词汇以及root本身，形成level2
def level_2_form(position, arcs_list, words_list):
    update_index = [position]
    for index in range(len(arcs_list)):
        if arcs_list[index].head == position + 1:
            update_index.append(index)
    words_update = ''
    for word in words_list[min(update_index): max(update_index) + 1]:
        words_update += word
    return words_update



level_1 = []
level_2 = []
level_3 = []
level_4 = []

level_relate_2 = {}
level_relate_3 = {}

# 分词
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
segmentor = Segmentor()  # 初始化实例
segmentor.load(cws_model_path)  # 加载模型

# 词性标注
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
postagger = Postagger()  # 初始化实例
postagger.load(pos_model_path)  # 加载模型

# 命名实体识别
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，模型名称为`pos.model`
recognizer = NamedEntityRecognizer()  # 初始化实例
recognizer.load(ner_model_path)  # 加载模型

# 依存句法分析
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
parser = Parser()  # 初始化实例
parser.load(par_model_path)  # 加载模型

# 语义角色标注
srl_model_path = os.path.join(LTP_DATA_DIR, 'pisrl_win.model')  # 语义角色标注模型目录路径，模型目录为`srl`。注意该模型路径是一个目录，而不是一个文件。
labeller = SementicRoleLabeller()  # 初始化实例
labeller.load(srl_model_path)  # 加载模型

# 从一整个句子的角度来看
# 分词
words = segmentor.segment(whole_sent)  # 分词
words_list = list(words)

# 词性标注
postags = postagger.postag(words_list)  # 词性标注
postags_list = list(postags)

# 命名实体识别
netags = recognizer.recognize(words_list, postags_list)  # 命名实体识别
netags_list = list(netags)

# 依存句法分析
arcs = parser.parse(words_list, postags_list)  # 句法分析
arcs_list = list(arcs)

# 语义角色标注
# arcs 使用依存句法分析的结果
roles = labeller.label(words_list, postags_list, arcs)  # 语义角色标注

root_sent = find_section(find_root(arcs_list), sents_list)

print(words_list)
print(postags_list)
print(netags_list)
print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs_list))
for role in roles:
    print(role.index, "".join(
        ["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))

NE = []
S_exist = False
for index in range(len(netags_list)):
    if netags_list[index].startswith('S'):
        if words_list[index] not in NE:
            NE.append(words_list[index])
            S_exist = True
level_1 = NE

NE_S = ''
if S_exist == False:
    # 如果一个句子没有实体，那么这里使用pyhanlp寻找这个句子的关键词，通过关键词定位句子并引申为level_2。
    keyword = HanLP.extractKeyword(whole_sent, 1)
    NE_S += keyword[0]

for sent in sents_list:
    # 分词
    words = segmentor.segment(sent)  # 分词
    words_list = list(words)

    # 词性标注
    postags = postagger.postag(words_list)  # 词性标注
    postags_list = list(postags)

    # 命名实体识别
    netags = recognizer.recognize(words_list, postags_list)  # 命名实体识别
    netags_list = list(netags)

    # 依存句法分析
    arcs = parser.parse(words_list, postags_list)  # 句法分析
    arcs_list = list(arcs)

    # 语义角色标注
    # arcs 使用依存句法分析的结果
    roles = labeller.label(words_list, postags_list, arcs)  # 语义角色标注

    # 打印结果
    print(words_list)
    print(postags_list)
    print(netags_list)
    print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs_list))
    for role in roles:
        print(role.index, "".join(
            ["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))

    level_1_index = []
    level_2_index = []

    words_list_update = copy.deepcopy(words_list)
    # 首先找到所有的实体，通过pyltp， 找到所有在命名实体识别中返回结果开头为S的词语， 并将它们放在level_1
    for index in range(len(words_list)):
        # 所有非实体的名词都被放在level4
        if postags_list[index].startswith('n'):
            if words_list[index] not in level_4:
                level_4.append(words_list[index])
    print(level_2_form(0, arcs_list, words_list))
    # 如果这个句子是含有root词的，那么找到这个句子里面的中心词汇，最好是实体，其次是名词
    # 根据实体和关键词找出属于level_1 和 level_2 的成分
    # 如果存在实体那么实体相关的句子或词汇就是level_2，跟实体不想关的句子或者词汇就是level_3
    if sent == root_sent:
        for index in range(len(words_list)):
            if words_list[index] in NE:
                level_1_index.append(index)
            elif words_list[index] in NE_S:
                if postags_list[index].startswith('n'):
                    level_1.append(words_list[index])
                    level_2_index.append(index)
            if index in level_1_index:
                words_list_update = level_2_form(0, arcs_list, words_list)
                # words_list_update = s_update(words_list, arcs_list, index)
                # level_relate_2[words_list[index]] = words_list_update
                level_2.append(words_list_update)
            if index in level_2_index:
                words_list_update = s_update(words_list, arcs_list, index)
                level_2.append((words_list_update))

    # 通过语义角色标注模块，找到谓语以及这个谓语对应的词组作为level3 的成分
    all_key_information = []
    for role in roles:
        key_information = ''
        include_NE = False
        v_n = False  # 用作判断句子中是否含有动词或者名词
        # loop所有的arguments
        for arg in role.arguments:
            # 如果这个role.head 是对应着实体，或者这个role中的arg含有实体，那么不考虑这一个role
            if role.index in level_1_index:
                include_NE = True
            elif arg.range.start == arg.range.end and arg.range.start in level_1_index:
                include_NE = True
            else:
                for index in range(arg.range.start, arg.range.end):
                    if index in level_1_index:
                        include_NE = True
            if include_NE == False:
                v_n = v_n or v_n_included(arg.range.start, arg.range.end, postags_list, role.index)
                # 判断role.index在这个arg的前面还是后面或者，以此来完成这一整个role的正确排序。
                if role.index < arg.range.start:
                    key_information += words_list[role.index]
                if arg.range.start == arg.range.end:
                    key_information += words_list[arg.range.start]
                else:
                    for index in range(arg.range.start, arg.range.end + 1):
                        key_information += words_list[index]
        if words_list[role.index] not in key_information and include_NE == False:
            key_information += words_list[role.index]
        # 如果key_information 不是空的，and 这个key_information 含有动词或者名词，那么我将它放入all_key_information里面
        if v_n == True:
            all_key_information.append(key_information)
    # 排除情况当这个过程中产生多个相似或者重复的情况，例如['选择一个适合自己的学校很重要'] 和 ['选择一个适合自己的学校']。
    # 这种情况取长的那个
    if all_key_information != []:
        for sent in select_longest_or_shortest(all_key_information, True):
            level_3.append(sent)

    # 有情况是role并没有包含到所有的内容，这里指的所有内容指的是含有名词的内容没有被记录，以下这段代码处理这个问题
    for index in range(len(words_list)):
        head = arcs_list[index].head - 1
        if head != -1 and head not in level_1_index and head not in level_2_index:
            if postags_list[head].startswith('n'):
                words_list_update = s_update_all(words_list, arcs_list, index)
                if words_list_update not in level_3:
                    level_3.append(words_list_update)

segmentor.release()  # 释放模型
postagger.release()  # 释放模型
recognizer.release()  # 释放模型
parser.release()  # 释放模型
labeller.release()  # 释放模型

# 打印结果
print('结果：')
print(level_1)
level_2 = level_1_2_relate(level_1, select_longest_or_shortest(level_2, False))
print(level_2)
print(different(level_2, select_longest_or_shortest(level_3, True)))
# print(level_relate_2)
# print(level_relate_3)
print(level_4)
