s_1 = '去美国留学，选择一个适合自己的学校很重要，选择一个好的城市也同样重要'
s_2 = '在大城市，学生不仅能增长见识，还能享受到大城市的便利，接触到不一样的社会层面'
s_4 = '旧金山湾区是世界最重要的科教文化中心之一，' \
      '坐拥斯坦福大学和加州大学伯克利分校两大世界知名高校，' \
      '以及世界顶级医学中心加州大学旧金山分校，在众多兄弟城市中独占鳌头'
s_5 = '旧金山更是高科技产业的天堂，由于临近世界著名高新技术产业区硅谷，而且在旧金山求学的学子也备受雇主青睐'
s_6 = '此外，旧金山也是一座气候宜人的海港城市，多民族、种族融合在一起，每个月都有独具特色的文化节日'
s_7 = '波士顿是美国东北部高等教育和医疗保健的中心，是全美人口受教育程度最高的城市'
s_8 = '拥有塔夫斯大学、波士顿学院、波士顿大学、布兰迪斯大学和东北大学等全美名校，可能大街上与你擦肩而过的就是各校的精英'
s_9 = '波士顿在经济、文化及娱乐产业上也是声名赫赫，可以说波士顿是一座全面发展、综合实力非常强的城市'
s_10 = '西雅图被誉为新的科技热潮中心，在航天、计算机软件、生物信息科学、基因科学、远程医疗、电子设备、医疗设备、' \
       '环境工程等先进技术处于领导地位'
s_11 = '西雅图是一个表演艺术的中心。西雅图交响乐团有上百年的历史，是世界上出版唱片最多的交响乐团之一；' \
       '西雅图在流行音乐和现代音乐方面也非常多样和活跃'
s_12 = '奥斯汀不仅仅是政治中心，也是教育中心，更是音乐、户外活动和文化活动聚集的地方'
s_13 = '此外，奥斯汀的科技也很发达，被誉为“硅山”（SiliconHill），是Freescale半导体公司、戴尔公司总部所在地' \
       '此外，IBM、苹果、谷歌、英特尔、思科、3M、eBay等也在当地设有分部'
s_14 = '盐湖城都市区是美国重要的金融中心、商业中心以及度假胜地之一，是诸多其他观光小镇及国家公园的入口，' \
       '包括犹他公园城、Snowbird滑雪度假村及拱门国家公园'

LTP_DATA_DIR = 'C:/Users/david/Desktop/site/django site/knowledge/ltp_data_v3.4.0'
from pyltp import SentenceSplitter
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
from pyltp import SementicRoleLabeller
import copy
from pyhanlp import *

sentences = SentenceSplitter.split(s_1)  # 分句
whole_sent = s_2
sentences_list = []
for sent in sentences:
    for s in sent.split('，'):
        sentences_list.append(s)


# 一个list里面可能会有很多相类似的句子或者词汇，如果mode是True，这里把所有重复的句子删掉并且选择其中含有重复内容的较长的句子
# ，例如【'一个适合自己的学校'，'选择一个适合自己的学校很重要'， '一个好的城市'， '选择一个好的城市也同样重要'】
# 这里就选择['选择一个适合自己的学校很重要', '选择一个好的城市也同样重要']
# 如果mode是False，这里把所有重复的句子删掉并且选择其中含有重复内容的较短的句子
# 例如【'一个适合自己的学校'，'选择一个适合自己的学校很重要'， '一个好的城市'， '选择一个好的城市也同样重要'】
# 这里就选择['一个适合自己的学校', '一个好的城市']
def select_longest_or_shortest(sentences_list_copy, mode):
    new_sentences_list = []
    for sentence in sentences_list_copy:
        if sentence not in new_sentences_list:
            new_sentences_list.append(sentence)
    sentences_list_copy = copy.deepcopy(new_sentences_list)
    for sentence in sentences_list_copy:
        for sent_comp in sentences_list_copy:
            all_in = True
            for s in sentence:
                if s not in sent_comp:
                    all_in = False
            if all_in and sentence != sent_comp and mode:
                try:
                    new_sentences_list.remove(sentence)
                except:
                    pass
            elif all_in and sentence != sent_comp and not mode:
                try:
                    new_sentences_list.remove(sent_comp)
                except:
                    pass
    return new_sentences_list


# 得到新的words list 根据index 和 head 之间的范围
def update_words_list(words_list_copy, index_value, head_value):
    words_list_update_result = ''
    if head_value < index_value:
        for i in range(head_value, index_value + 1):
            words_list_update_result += words_list_copy[i]
    elif index_value < head_value:
        for i in range(index_value, head_value + 1):
            words_list_update_result += words_list_copy[i]
    return words_list_update_result


# 判断这一个句子里有没有动词或者名词，有则return True，没有则return False
def v_n_included(start, end, postags_list_copy, head_value):
    if start == end:
        end += 1
    if postags_list_copy[head_value].startswith('v'):
        return True
    if postags_list_copy[head_value].startswith('n'):
        return True
    for i in range(start, end):
        if postags_list_copy[i].startswith('v'):
            return True
        if postags_list_copy[i].startswith('n'):
            return True
    return False


# 得到level2 的东西根据实体的位置
def s_update(words_list_copy, arcs_list_copy, index_value):
    head_value = arcs_list_copy[index_value].head - 1
    update_index = [index_value, head_value]
    for arc_index in range(len(words_list_copy)):
        if arcs_list_copy[update_index[-1]].head == 0:
            update_index.append(arc_index)
            break
        if arc_index in update_index:
            pass
        elif arc_index == arcs_list_copy[update_index[-1]].head - 1:
            update_index.append(arc_index)
    words_list_update_result = update_words_list(words_list_copy, min(update_index), max(update_index))
    return words_list_update_result


# 得到level_3 的信息
def s_update_all(words_list_copy, arcs_list_copy, index_value):
    head_value = arcs_list_copy[index_value].head - 1
    update_index = [index_value, head_value]
    all_set = False
    while not all_set:
        for arc_index in range(len(words_list_copy)):
            if arcs_list_copy[update_index[-1]].head == 0:
                update_index.append(arc_index)
                all_set = True
                break
            if arc_index in update_index:
                pass
            elif arc_index == arcs_list_copy[update_index[-1]].head - 1:
                update_index.append(arc_index)
                all_set = False
    words_list_update_result = update_words_list(words_list_copy, min(update_index), max(update_index))
    return words_list_update_result


# level_1都是实体名词，level_2都是含有实体名词也就是level_1的句子，所以这里删除其他的信息
def level_1_2_relate(level_1_copy, level_2_copy):
    if not level_1_copy:
        return level_2_copy
    for sentence in level_2_copy:
        if level_1_copy[0] in sentence:
            return [sentence]


# 这里确保level_2和level_3 的信息不重复
def different(level_2_copy, level_3_copy):
    level_3_copy_temp = copy.deepcopy(level_3_copy)
    for sentence in level_3_copy:
        if sentence in level_2_copy:
            try:
                level_3_copy_temp.remove(sentence)
            except:
                print('something wrong with inputing information to level_3')
    return level_3_copy_temp


# 找到依存句法分析中的root，也就是当arc.head 等于0的时候
def find_root(arcs_list_copy):
    for position in range(len(arcs_list_copy)):
        if arcs_list_copy[position].head == 0:
            return position


# 找到某个index所在的分句，这里按照postags_list 里面的wp（标点符号）来分， 并且return那个句子在整句中的index[start:end]
def find_section(index_value, postags_list_copy):
    start = 0
    end = 0
    accumulate = 0
    for i in range(len(postags_list_copy)):
        accumulate += 1
        if postags_list_copy[i] == 'wp':
            if index_value < accumulate:
                end = i - 1
                return start, end
            else:
                start = i + 1
        elif i == len(postags_list_copy) - 1:
            if index_value < accumulate:
                end = i
                return start, end


# 根据root所在的位置，关联所有与root相关的词汇，形成level2，但是level_2里不包括这个句子的中心词汇
def level_2_form(position, arcs_list_copy, words_list_copy, index_copy):
    NE = ''
    for i in range(len(words_list_copy)):
        if i in index_copy:
            NE += words_list_copy[i]
    update_index = [position]
    for i in range(len(arcs_list_copy)):
        if arcs_list_copy[i].head == position + 1:
            update_index.append(i)
    words_update = ''
    for w in words_list_copy[min(update_index): max(update_index) + 1]:
        words_update += w
    return words_update.replace(NE, '')


level_1 = []
level_2 = []
level_3 = []
level_4 = []

level_relate = {}

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
whole_words = segmentor.segment(whole_sent)  # 分词
whole_words_list = list(whole_words)

# 词性标注
whole_postags = postagger.postag(whole_words_list)  # 词性标注
whole_postags_list = list(whole_postags)

# 命名实体识别
whole_netags = recognizer.recognize(whole_words_list, whole_postags_list)  # 命名实体识别
whole_netags_list = list(whole_netags)

# 依存句法分析
whole_arcs = parser.parse(whole_words_list, whole_postags_list)  # 句法分析
whole_arcs_list = list(whole_arcs)

# 语义角色标注
# arcs 使用依存句法分析的结果
whole_roles = labeller.label(whole_words_list, whole_postags_list, whole_arcs)  # 语义角色标注

print(whole_words_list)
print(whole_postags_list)
print(whole_netags_list)
print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in whole_arcs_list))
for role in whole_roles:
    print(role.index, "".join(
        ["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))

# 找到一个整句中的root所在的位置，根据依存句法分析的数据来找
root_index = 0
for index in range(len(whole_arcs_list)):
    if whole_arcs_list[index].head == 0:
        root_index = index

# 通过root所在的位置，找这一个单句中的关键名词或者实体，作为这一个整句中的中心
# 首先找到这个root所在的单句
root_section = find_section(root_index, whole_postags_list)
# 通过找到的root所在的单句index，得出整个单句
root_sent = ''
for word in whole_words_list[root_section[0]:root_section[1]]:
    root_sent += word


# 找到这一个COO最终是否能够对应到root，也就是arc.head 等于 0
def arc_coo_destination_is_root(arcs_list_copy, index_value, root_value):
    while True:
        if arcs_list_copy[index_value].relation == "COO":
            if arcs_list_copy[index_value].head == root_value + 1:
                return True
            else:
                index_value = arcs_list_copy[index_value].head - 1
        else:
            return False


# 找到这个root单句中是否有主谓关系，或者动宾关系，如果有，得出主语或者宾语，如果没有则得出[]
# 这里注意主谓关系比动宾关系更重要，如果有了主语，那么不考虑宾语
# last_sbv 这里指的是上一句话含有的主语，如果没有上一句话，则last_sbv 为 []

def arc_sbv_vob_destination_is_root(postags_list_copy, arcs_list_copy, root_value, last_sbv):
    result = []
    for i in range(root_section[0], root_section[1]):
        if arcs_list_copy[i].head == root_value + 1 and not postags_list_copy[i] == 'r':
            if arcs_list_copy[i].relation == "SBV":
                result.append(i)
    if not result:
        if last_sbv:
            result = last_sbv
        else:
            for i in range(root_section[0], root_section[1]):
                if arcs_list_copy[i].head == root_value + 1 and not postags_list_copy[i] == 'r':
                    if arcs_list_copy[i].relation == "VOB":
                        result.append(i)
    return result


# 找到root其余的句子xinxi
def find_root_rest(words_list_copy, exist_value):
    result = []
    for i in words_list_copy:
        if not i in exist_value:
            result.append(i)
    return result


level_value = []
special_sentence = ''
result = arc_sbv_vob_destination_is_root(whole_postags_list, whole_arcs_list, root_index, [])
level_key = result
for i in range(len(whole_arcs_list)):
    if root_section[0] <= i <= root_section[1]:
        if whole_arcs_list[i].relation == "COO":
            if whole_arcs_list[i].head - 1 == root_index:
                level_key.append(i)
                level_key.append(root_index)
    else:
        if whole_arcs_list[i].relation == "COO":
            if arc_coo_destination_is_root(whole_arcs_list, i, root_index):
                current_section = find_section(i, whole_postags_list)
                for cs in range(current_section[0], current_section[1] + 1):
                    if cs not in level_value:
                        level_value.append(cs)
        elif whole_arcs_list[i].relation == "ADV" and \
                whole_arcs_list[i].head == root_index + 1:
            current_section = find_section(i, whole_postags_list)
            for cs in range(current_section[0], current_section[1] + 1):
                level_key.append(cs)

print(level_key)
result = find_root_rest(whole_words_list[root_section[0]:root_section[1] + 1], level_key)
print(result)

print(level_key)
print(level_value)
level_key_temp = []
level_value_temp = []
for l in level_key:
    print(l)
    if type(l) == tuple:
        temp_sentence = ''
        for i in range(l[0], l[1] + 1):
            if not whole_postags_list[i] == 'c':
                if not whole_postags_list[i] == 'm':
                    temp_sentence += whole_words_list[i]
        level_key_temp.append(temp_sentence)
    else:
        level_key_temp.append(whole_words_list[l])

for l in level_value:
    if type(l) == tuple:
        temp_sentence = ''
        for i in range(l[0], l[1] + 1):
            if not whole_postags_list[i] == 'c':
                if not whole_postags_list[i] == 'm':
                    temp_sentence += whole_words_list[i]
        level_value_temp.append(temp_sentence)
    else:
        level_value_temp.append(whole_words_list[l])
level_relate[tuple(level_key_temp)] = tuple(level_value_temp)
print('结果')
print(level_relate)

#
# level_value = []
#
#
# # 其次找到这个单句中的实体，如果没有实体，那么寻找名词，如果没有名词，就选择主语
# NE_index = []  # 实体NE所在的index
# NE_exist = False  # 实体是否存在
# level_1_information = ''
# # 如果在这个index上的netag 是一个实体或者是实体的一部分，那么就把这个index放进NE_index里
# # 因为一整个句子有标点符号间隔的情况，这里的index是NE在那一个单句的index
# for i in range(root_section[0], root_section[1]):
#     if not whole_netags_list[i].startswith('O'):
#         if i not in NE_index:
#             NE_index.append(i - root_section[0])
#             NE_exist = True
#
# print(NE_index)
#
# # 如果有两个实体同时出现，那么找这两个实体中的主语实体
#
#
# None_NE_index = []  # 非实体关键词所在的index
# if not NE_exist:
#     # 如果一个句子没有实体，那么这里找这个句子里对应root的关键词汇，以名词主语为主
#     for i in range(root_section[0], root_section[1]):
#         # 寻找主谓关系
#         if whole_arcs_list[i].relation == "SBV" and whole_arcs_list[i].head == root_index + 1:
#             None_NE_index.append(i - root_section[0])
# print(None_NE_index)
# if NE_exist:
#     for NE in NE_index:
#         level_1_information += whole_words_list[NE + root_section[0]]
# else:
#     for None_NE in None_NE_index:
#         level_1_information += whole_words_list[None_NE + root_section[0]]
# level_1.append(level_1_information)
# # 考虑在一整句话中，有一个单句起到状语的结构去形容root词汇的且这个单句和root所在的句子不是同一个句子，
# # 那么这一句话要放在level_2， root所在的句子信息放在level_3
# special_case = False  # 是否有special case
# special_sent = ''
# for index in range(len(whole_words_list)):
#     if whole_arcs_list[index].relation == "ADV" and \
#             whole_arcs_list[index].head - 1 == root_index:
#         if index > root_section[1] or index < root_section[0]:
#             section = find_section(index, whole_postags_list)
#             for i in range(section[0], section[1]):
#                 if not whole_postags_list[i] == 'c':
#                     special_sent += whole_words_list[i]
#                     if special_sent not in level_2:
#                         level_2.append(special_sent)
# if special_sent:
#     special_case = True
#
# current_index = 0
# for sent in sentences_list:
#     # 分词
#     words = segmentor.segment(sent)  # 分词
#     words_list = list(words)
#
#     # 词性标注
#     postags = postagger.postag(words_list)  # 词性标注
#     postags_list = list(postags)
#
#     # 命名实体识别
#     netags = recognizer.recognize(words_list, postags_list)  # 命名实体识别
#     netags_list = list(netags)
#
#     # 依存句法分析
#     arcs = parser.parse(words_list, postags_list)  # 句法分析
#     arcs_list = list(arcs)
#
#     # 语义角色标注
#     # arcs 使用依存句法分析的结果
#     roles = labeller.label(words_list, postags_list, arcs)  # 语义角色标注
#
#     # 打印结果
#     print(words_list)
#     print(postags_list)
#     print(netags_list)
#     print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs_list))
#     for role in roles:
#         print(role.index, "".join(
#             ["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))
#
#     level_1_index = []
#     level_2_index = []
#
#     words_list_update = copy.deepcopy(words_list)
#
#     # 根据之前通过整句找到的实体和关键词找出属于level_1 和 level_2 的成分
#     # 如果存在实体那么实体相关的句子或词汇就是level_2，跟实体不想关的句子或者词汇就是level_3
#     if sent == root_sent:
#         if NE_exist:
#             words_list_update = level_2_form(root_index - current_index, arcs_list, words_list, NE_index)
#         else:
#             words_list_update = level_2_form(root_index - current_index, arcs_list, words_list, None_NE_index)
#         if special_case:
#             level_3.append(words_list_update)
#         else:
#             level_2.append(words_list_update)
#     else:
#         if special_sent != sent:
#             sentence_update = ''
#             for index in range(len(words_list)):
#                 if not postags_list[index] == 'm':
#                     if not postags_list[index] == 'c':
#                         sentence_update += words_list[index]
#                 # 所有非实体的名词都被放在level4
#                 if postags_list[index].startswith('n'):
#                     if words_list[index] not in level_4:
#                         level_4.append(words_list[index])
#             print(sentence_update)
#             if sentence_update != '':
#                 level_3.append(sentence_update)
#
#     current_index += len(words_list) + 1
#     # 通过语义角色标注模块，找到谓语以及这个谓语对应的词组作为level3 的成分
#     # all_key_information = []
#     # for role in roles:
#     #     key_information = ''
#     #     include_NE = False
#     #     v_n = False  # 用作判断句子中是否含有动词或者名词
#     #     # loop所有的arguments
#     #     for arg in role.arguments:
#     #         # 如果这个role.head 是对应着实体，或者这个role中的arg含有实体，那么不考虑这一个role
#     #         if role.index in level_1_index:
#     #             include_NE = True
#     #         elif arg.range.start == arg.range.end and arg.range.start in level_1_index:
#     #             include_NE = True
#     #         else:
#     #             for index in range(arg.range.start, arg.range.end):
#     #                 if index in level_1_index:
#     #                     include_NE = True
#     #         if include_NE == False:
#     #             v_n = v_n or v_n_included(arg.range.start, arg.range.end, postags_list, role.index)
#     #             # 判断role.index在这个arg的前面还是后面或者，以此来完成这一整个role的正确排序。
#     #             if role.index < arg.range.start:
#     #                 key_information += words_list[role.index]
#     #             if arg.range.start == arg.range.end:
#     #                 key_information += words_list[arg.range.start]
#     #             else:
#     #                 for index in range(arg.range.start, arg.range.end + 1):
#     #                     key_information += words_list[index]
#     #     if words_list[role.index] not in key_information and include_NE == False:
#     #         key_information += words_list[role.index]
#     #     # 如果key_information 不是空的，and 这个key_information 含有动词或者名词，那么我将它放入all_key_information里面
#     #     if v_n == True:
#     #         all_key_information.append(key_information)
#     # # 排除情况当这个过程中产生多个相似或者重复的情况，例如['选择一个适合自己的学校很重要'] 和 ['选择一个适合自己的学校']。
#     # # 这种情况取长的那个
#     # if all_key_information != []:
#     #     for sent in select_longest_or_shortest(all_key_information, True):
#     #         level_3.append(sent)
#     #
#     # # 有情况是role并没有包含到所有的内容，这里指的所有内容指的是含有名词的内容没有被记录，以下这段代码处理这个问题
#     # for index in range(len(words_list)):
#     #     head = arcs_list[index].head - 1
#     #     if head != -1 and head not in level_1_index and head not in level_2_index:
#     #         if postags_list[head].startswith('n'):
#     #             words_list_update = s_update_all(words_list, arcs_list, index)
#     #             if words_list_update not in level_3:
#     #                 level_3.append(words_list_update)

segmentor.release()  # 释放模型
postagger.release()  # 释放模型
recognizer.release()  # 释放模型
parser.release()  # 释放模型
labeller.release()  # 释放模型

# 打印结果
# print('结果：')
# print(level_1)
# # level_2 = level_1_2_relate(level_1, select_longest_or_shortest(level_2, False))
# print(level_2)
# # print(different(level_2, select_longest_or_shortest(level_3, True)))
# print(level_3)
# print(level_4)
