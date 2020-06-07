from pyltp import SentenceSplitter
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
from pyltp import SementicRoleLabeller
import copy
from pyhanlp import *
import settings
LTP_DATA_DIR = settings.LTP_DATA_DIR

# sentences = SentenceSplitter.split(s_1)  # 分句
# whole_sent = s_8
sentences_list = []

# for sent in sentences:
#     for s in sent.split('，'):
#         sentences_list.append(s)

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


special_chacter = ['、', '”', '“', '（', '）', '{', '}', '【', '】']


# 找到某个index所在的分句，这里按照postags_list 里面的wp（标点符号）来分， 并且return那个句子在整句中的index[start:end]
# 注意 "、" 这个不属于考虑的标点符号
def find_section(index_value, postags_list_copy, words_list_copy):
    start = 0
    end = 0
    accumulate = 0
    for i in range(len(postags_list_copy)):
        accumulate += 1
        if postags_list_copy[i] == 'wp' and not words_list_copy[i] in special_chacter:
            if index_value < accumulate:
                end = i
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


# 找到这一个COO最终是否能够对应到section，也就是arc.head 在该section的index之中
def arc_coo_destination_is_root_sentence(arcs_list_copy, index_value, section_copy):
    while True:
        if arcs_list_copy[index_value].relation == "COO":
            if section_copy[0] < arcs_list_copy[index_value].head <= section_copy[1] + 1:
                return True
            else:
                index_value = arcs_list_copy[index_value].head - 1
        else:
            return False


# # 如果找到了sbv，看看这个sbv前面有没有ATT，如果有并且这个ATT是对应他的，那么连着att一起选
# def att_before_main(arcs_list_copy, main_index):
#     result = []
#     if main_index != 0:
#         if arcs_list_copy[main_index - 1].head == main_index + 1:
#             if arcs_list_copy[main_index - 1].relation == "ATT":
#             result.append(main_index - 1)
#         result.append(main_index)
#     else:
#         result.append(main_index)
#     return result

# 如果找到了sbv，看看这个sbv前面有没有ATT，如果有并且这个ATT是对应他的，那么连着att一起选
# 找后面的COO是否含有与SBV对应的
def att_before_main(arcs_list_copy, main_index):
    main_index_copy = copy.deepcopy(main_index)
    result = [main_index]
    temp_result = []
    status = True
    while status:
        if main_index != 0:
            if arcs_list_copy[main_index - 1].head - 1 in result:
                if arcs_list_copy[main_index - 1].relation == "ATT":
                    result.append(main_index - 1)
                    if temp_result:
                        result += temp_result
                    temp_result = []
                elif arcs_list_copy[main_index - 1].relation == "LAD":
                    result.append(main_index - 1)
                elif arcs_list_copy[main_index - 1].relation == "SBV":
                    result.append(main_index - 1)
                elif arcs_list_copy[main_index - 1].relation == "FOB":
                    result.append(main_index - 1)
                else:
                    status = False
            elif arcs_list_copy[main_index - 1].relation == "RAD" or arcs_list_copy[main_index - 1].relation == "VOB"\
                    or arcs_list_copy[main_index - 1].relation == "COO":
                temp_result.append(main_index - 1)
            else:
                status = False
            main_index -= 1
        else:
            status = False
    status = True

    while status:
        if arcs_list_copy[main_index_copy + 1].head - 1 in result:
            if arcs_list_copy[main_index_copy + 1].relation == "COO":
                result.append(main_index_copy + 1)
                if temp_result:
                    result += temp_result
                temp_result = []
        elif arcs_list_copy[main_index_copy + 1].relation == "LAD":
            temp_result.append(main_index_copy + 1)
        else:
            status = False
        main_index_copy += 1
    return sorted(result)


# 找到这个root单句中是否有主谓关系，或者动宾关系，如果有，得出主语或者宾语，如果没有则得出[]
# 这里注意主谓关系比动宾关系更重要，如果有了主语，那么不考虑宾语
# last_sbv 这里指的是上一句话含有的主语，如果没有上一句话，则last_sbv 为 []
# 如果有两个或更多sbv 都对应着root，那么他们中间所有的内容都作为主语
# 如果找到了sbv，看看这个sbv前面有没有ATT，如果有并且这个ATT是对应他的，那么连着att一起选
def arc_sbv_vob_destination_is_root(postags_list_copy, arcs_list_copy, root_value, last_sbv):
    result = []
    for i in range(len(arcs_list_copy)):
        if arcs_list_copy[i].head == root_value + 1 and not postags_list_copy[i] == 'r':
            if arcs_list_copy[i].relation == "SBV":
                result += att_before_main(arcs_list_copy, i)
            elif arcs_list_copy[i].relation == "FOB":
                result += att_before_main(arcs_list_copy, i)
    if not result:
        if last_sbv:
            result = last_sbv
        else:
            for i in range(root_section[0], root_section[1] + 1):
                if arcs_list_copy[i].head == root_value + 1 and not postags_list_copy[i] == 'r':
                    if arcs_list_copy[i].relation == "VOB":
                        result += att_before_main(arcs_list_copy, i)
    return result


# 找到对应root的状中结构的句子，也就是从ADV 到 POB 之间
# 但如果这个部分正好在root的句子里,  则不予考虑
def arc_adv_destination_is_root(arcs_list_copy, root_value, root_section_copy):
    result = []
    adv_start = False
    temp_adv = []
    for i in range(len(arcs_list_copy)):
        if i < root_section_copy[0] or i > root_section_copy[1]:
            if arcs_list_copy[i].relation == "ADV" and arcs_list_copy[i].head == root_value + 1:
                temp_adv.append(i)
                adv_start = True
            elif arcs_list_copy[i].relation == "POB" and temp_adv:
                if arcs_list_copy[i].head == temp_adv[0] + 1:
                    temp_adv.append(i)
                    result.append(temp_adv)
                    adv_start = False
                    temp_adv = []
                else:
                    temp_adv.append(i)
            elif adv_start:
                temp_adv.append(i)
    return result


# 找到root其余的句子信息
def find_root_rest(words_list_copy, exist_value, root_section_copy):
    result = []
    for i in range(len(words_list_copy)):
        if root_section_copy[0] <= i <= root_section[1]:
            if not find_element_list_of_list(i, exist_value):
                result.append(i)
    return result


# 得到这个dict里面最后一个key里面的第一个词，如果dict是空的，那么return 一个空的list
def find_last_dict(dict_copy):
    if dict_copy:
        return list(dict_copy[-1])[-1][0]
    else:
        return []


# 这个方程的作用是确定这一个数字不在这个list of list里面，如果有，return True，没有，return False
def find_element_list_of_list(value, list_of_list):
    for lol in list_of_list:
        if value in lol:
            return True
    return False


# 把一个同时含有数字和list的内容进行整理， 并且去除句子中词性为m或者c的词，结果是return所有的句子在一个list里面
def mix_reset(mix_list, words_list_copy):
    result = []
    for l in mix_list:
        sentence = ''
        for i in l:
            sentence += words_list_copy[i]
        if sentence:
            result.append(sentence)
    return result


# 整理关键词的排序


# 根据COO，形成level_value，对应现有的level_key，并且return 一个list
def level_value_coo(arcs_list_copy, coo_index, to_coo_section, postags_list_copy,
                    words_list_copy):
    value = []
    update_section = []
    value_list = []
    if to_coo_section[0] <= arcs_list_copy[coo_index].head <= to_coo_section[1]:
        update_section = find_section(coo_index, postags_list_copy, words_list_copy)
        for us in range(update_section[0], update_section[1] + 1):
            value.append(us)
        value_list.append(value)
    for i in range(coo_index + 1, len(arcs_list_copy)):
        if arcs_list_copy[i].relation == "COO":
            value = []
            if update_section:
                if update_section[0] <= arcs_list_copy[i].head - 1 <= update_section[1]:
                    if not update_section[0] <= i <= update_section[1]:
                        update_section = find_section(i, postags_list_copy, words_list_copy)
                        for us in range(update_section[0], update_section[1] + 1):
                            value.append(us)
                        value_list.append(value)
    value_list = mix_reset(value_list, words_list_copy)
    return value_list


# 根据COO，形成level_value，对应现有的level_key，并且return 一个dict
def find_rest_sentence(words_list_copy, existed_index):
    result = []
    for i in range(len(words_list_copy)):
        in_list = False
        for value in existed_index:
            if i in value:
                in_list = True
        if not in_list:
            result.append(i)
    return result


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
       '，此外，IBM、苹果、谷歌、英特尔、思科、3M、eBay等也在当地设有分部'
s_14 = '盐湖城都市区是美国重要的金融中心、商业中心以及度假胜地之一，是诸多其他观光小镇及国家公园的入口，' \
       '包括犹他公园城、Snowbird滑雪度假村及拱门国家公园'

s_3 = '影响石油价格的供给因素'
s_15 = '从影响油价长期走势的供给因素和需求因素以及对油价造成冲击的短期因素三个方面对影响油价的因素进行分析'
s_16 = '影响石油价格的供给因素主要包括世界石油储量，石油供给结构以及石油生产成本'
s_17 = '石油产量必须以石油储量为基础'
s_18 = '过去的几十年中，世界石油资源探明的储量一直在持续增加，2005年底世界石油资源探明可采储量约为12007亿桶，' \
       '20年间增加了4303亿桶，增长了55.8%'
s_19 = '虽然产量的增长速度大于已探明储量的增长速度，但2005年底全球石油储量与产量之间的比例为40.6年，' \
       '可以预见，至少在未来10年不会出现全球范围内的石油供给短缺现象'
s_20 = '但是，由于石油资源的不可再生性，国际能源机构（iea）预测世界石油产量将在2015年以前达到顶峰，' \
       '全球石油供给逐步进入滑坡阶段'
s_21 = '世界石油市场的供给特点也对石油供给具有重大影响'
s_22 = '目前世界石油市场的供给方主要包括石油输出国组织（opec）和非opec国家。opec拥有世界上绝大部份探明石油储量，' \
       '其产量和价格政策对世界石油供给和价格具有重大影响'
s_23 = '而非opec国家主要是作为价格接受者存在，根据价格调整产量'
s_24 = '但2002年以来，受强劲的世界石油需求和高油价刺激，opec产量激增，' \
       '原油剩余产能从2002年的560万桶/日急剧下降到2006年的140万桶/日左右，产能利用率高于90％，通过增加产量平抑油价的能力减弱'
s_25 = '迫使市场参与者通过构建商业库存作为应对风险的缓冲，而库存需求反过来又刺激油价上行'
s_26 = '美欧跨国石油公司在世纪之交通过资本运作发起的新一轮兼并联合使得世界石化产业的集中度越来越高'
s_27 = '随着石化巨头对全球石油资源、技术和市场的控制力的进一步增强，世界石化产业的发展和竞争以及石油价格的波动带来了深刻影响'
s_28 = '此外，石油生产成本也将对石油供给产生影响'
s_29 = '石油作为一种不可再生能源，其生产成本会影响生产者跨时期的产量配置决策，进而影响到市场供给量，间接地引起石油价格波动'
s_30 = '世界石油价格的下限一般主要由高成本地区的石油生产决定，而低成本地区的石油决定了价格的波动幅度'
s_31 = '石油需求主要由世界经济发展水平及经济结构变化，替代能源的发展和节能技术的应用决定'
s_32 = '影响石油价格的需求因素'
s_33 = '石油需求主要由世界经济发展水平及经济结构变化，替代能源的发展和节能技术的应用决定'
s_34 = '全球石油消费与全球经济增长速度明显正相关'
s_35 = '全球经济增长或超预期增长都会牵动国际原油市场价格出现上涨'
s_36 = '以中国、印度为代表的发展中国家经济强劲增长也使得对原油的需求急剧增加，导致世界原油价格震荡走高'
s_37 = '其中中国对石油的需求带动了全球石油消费增长的1/3'
s_38 = '而反过来，异常高的油价势必会阻碍世界经济的发展，全球经济增长速度放缓又会影响石油需求的增加'
s_39 = '替代能源的成本将决定石油价格的上限'
s_40 = '当石油价格高于替代能源成本时，消费者将倾向于使用替代能源'
s_41 = '而节能将使世界石油市场的供需矛盾趋于缓和'
s_42 = '目前各国都在大力发展可再生能源和节能技术，这势必将对石油价格的长期走势产生影响'
s_43 = '影响石油价格的短期因素'
s_44 = '短期影响因素是通过对供求关系造成冲击或短期内改变人们对供求关系的预期而对石油价格发挥作用的'
s_45 = '突发的重大政治事件'
s_46 = '石油除了一般商品属性外，还具有战略物资的属性，其价格和供应很大程度上受政治势力和政治局势的影响'
s_47 = '近年来，随着政治多极化、经济全球化、生产国际化的发展，争夺石油资源和控制石油市场，已成为油市动荡和油价飙涨的重要原因'
s_48 = '石油库存变化'
s_49 = '库存是供给和需求之间的一个缓冲，对稳定油价有积极作用'
s_50 = 'ecd的库存水平已经成为国际油价的指示器，并且商业库存对石油价格的影响要明显强于常规库存'
s_51 = '当期货价格远高于现货价格时，石油公司倾向于增加商业库存，刺激现货价格上涨，' \
       '期货现货价差减小；当期货价格低于现货价格时，石油公司倾向于减少商业库存，现货价格下降，与期货价格形成合理价差'
s_52 = 'opec和国际能源署（iea）的市场干预'
s_53 = 'opec控制着全球剩余石油产能的绝大部分，iea则拥有大量的石油储备，他们能在短时期内改变市场供求格局，' \
       '从而改变人们对石油价格走势的预期'
s_54 = 'opec的主要政策是限产保价和降价保产'
s_55 = 'iea的26个成员国共同控制着大量石油库存以应付紧急情况'
s_56 = '国际资本市场资金的短期流向'
s_57 = '20世纪90年代以来，国际石油市场的特征是期货市场的影响显著增强，目前已经形成了由期货市场向现货市场传导的价格形成机制'
s_58 = '尽管国际原油市场的投机活动不是油价上涨的诱发因素，但由于全球金融市场投资机会缺乏，' \
       '大量资金进入国际商品市场，尤其是原油市场，不可避免地推高了国际油价，并使其严重偏离基本面'
s_59 = '汇率变动'
s_60 = '相关研究表明，石油价格变动和美元与国际主要货币之间的汇率变动存在弱相关关系'
s_61 = '由于美元持续贬值，以美元标价的石油产品的实际收入下降，导致石油输出国组织以维持原油高价作为应对措施'
s_62 = '异常气候'
s_63 = '欧美许多国家用石油作为取暖的燃料，因此，当气候变化异常时，会引起燃料油需求的短期变动，从而带动原油和其他油品的价格变化'
s_64 = '另外，异常的天气可能会对石油生产设施造成破坏，导致供给中断，从而影响油价'
s_65 = '利率变动'
s_66 = '在标准不可再生资源模型中，利率的上升会导致未来开采价值相对现在开采价值减少，因此会使得开采路径凸向现在而远离未来'
s_67 = '高利率会减少资本投资，导致较小的初始开采规模；高利率也会提高替代技术的资本成本，导致开采速度下降'
s_68 = '税收政策'
s_69 = '政府干预会使得市场消耗曲线凸向现在或未来'
s_70 = '跨时期石油开采模式的税收效应依赖于税收随时间变化的现值'
s_71 = '例如，税收现值随时间减少会改变开采顺序的决策'
s_72 = '和不征税相比，税收最终还是会减少任意时点上的净收益，也就减少了相应时期开采的积极性'
s_73 = '而且税收会降低新发现储量的投资回报'

# level_1 = []
# level_2 = []
# level_3 = []
# level_4 = []

level_relate = []

knowledge_graph = {}
update_last_sentence_sbv = ''
for sentence in [s_1, s_2, s_4, s_5, s_6, s_7, s_8, s_9, s_10, s_11, s_12, s_13, s_14, s_15, s_16, s_17, s_18, s_19,
                 s_20, s_21, s_22, s_23, s_24, s_25, s_26, s_27, s_28, s_29, s_30]:

    whole_sent = sentence
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
    # for role in whole_roles:
    #     print(role.index, "".join(
    #         ["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))

    # 找到一个整句中的root所在的位置，根据依存句法分析的数据来找
    root_index = 0
    for index in range(len(whole_arcs_list)):
        if whole_arcs_list[index].head == 0:
            root_index = index

    # 通过root所在的位置，找这一个单句中的关键名词或者实体，作为这一个整句中的中心
    # 首先找到这个root所在的单句
    root_section = find_section(root_index, whole_postags_list, whole_words_list)
    # 通过找到的root所在的单句index，得出整个单句
    root_sent = ''
    for word in whole_words_list[root_section[0]:root_section[1]]:
        root_sent += word

    # ----------------------------------------------------------------------------------------------------------------
    # 从这里开始 key 的部分
    level_key = []
    level_value = []
    last_sentence_sbv = ''
    find_root_rest_value = []
    find_rest_sentence_value = []
    result = arc_sbv_vob_destination_is_root(whole_postags_list, whole_arcs_list, root_index,
                                             update_last_sentence_sbv)
    if result == update_last_sentence_sbv:
        result = arc_adv_destination_is_root(whole_arcs_list, root_index, root_section)
        if result:
            result = arc_adv_destination_is_root(whole_arcs_list, root_index, root_section)
        else:
            last_sentence_sbv = update_last_sentence_sbv
    else:
        result = [result] + arc_adv_destination_is_root(whole_arcs_list, root_index, root_section)
    level_key = result
    for i in range(root_section[0], root_section[1] + 1):
        if whole_arcs_list[i].relation == "COO":
            if whole_arcs_list[i].head - 1 == root_index:
                if not find_element_list_of_list(i, level_key):
                    level_key.append([i])
                if not find_element_list_of_list(root_index, level_key):
                    level_key.append([root_index])

    if not last_sentence_sbv:
        level_key = sorted(level_key)
        find_root_rest_value = find_root_rest(whole_words_list, level_key, root_section)
        # find_rest_sentence_value = find_rest_sentence(whole_words_list, level_key)
        level_key = mix_reset(level_key, whole_words_list)
    else:
        find_root_rest_value = find_root_rest(whole_words_list, level_key, root_section)
        # find_rest_sentence_value = find_rest_sentence(whole_words_list, level_key)
        level_key = mix_reset(level_key, whole_words_list)
        level_key += last_sentence_sbv

    update_last_sentence_sbv = level_key

    # ----------------------------------------------------------------------------------------------------------------
    # 从这里开始 value 的部分
    level_value.append(find_root_rest_value)
    # level_value.append(find_rest_sentence_value)

    # level_key 剩下的部分组成value, 如果是一个标点符号则跳过第一个标点符号
    # if whole_postags_list[level_value[0][0]] == "wp":
    #     level_value[0].remove(level_value[0][0])
    # try:
    #     knowledge_graph[tuple(level_key)].append(tuple(mix_reset(level_value, whole_words_list)))
    # except:
    #     knowledge_graph[tuple(level_key)] = [tuple(mix_reset(level_value, whole_words_list))]
    if whole_postags_list[level_value[0][0]] == "wp":
        level_value[0].remove(level_value[0][0])
    try:
        if level_value[0]:
            knowledge_graph[tuple(level_key)].append(tuple(mix_reset(level_value, whole_words_list)))
    except:
        knowledge_graph[tuple(level_key)] = [tuple(mix_reset(level_value, whole_words_list))]
    # try:
    #     # 首先level_key 剩下的部分单独组成value其中的一个部分，如果是一个标点符号则跳过
    #     if not whole_postags_list[level_value[0][0]] == "wp":
    #         knowledge_graph[tuple(level_key)].append(tuple(mix_reset(level_value, whole_words_list)))
    # except:
    #     knowledge_graph[tuple(level_key)] = [tuple(mix_reset(level_value, whole_words_list))]
    temp_knowledge = []
    for i in range(len(whole_arcs_list)):
        if i > root_section[1] or i < root_section[0]:
            if whole_arcs_list[i].relation == "COO":
                level_value_coo_copy = level_value_coo(whole_arcs_list, i, root_section,
                                                       whole_postags_list,
                                                       whole_words_list)
                if level_value_coo_copy:
                    temp_knowledge.append(level_value_coo_copy)
    for knowledge in range(len(temp_knowledge)):
        temp_value = temp_knowledge[knowledge]
        try:
            knowledge_graph[tuple(level_key)].append(tuple(temp_value))
        except:
            knowledge_graph[tuple(level_key)] = [tuple(temp_value)]

            # if level_value_coo_copy:
            #     if tuple(level_key) in knowledge_graph:
            #         knowledge_graph[tuple(level_key)].append(tuple(level_value_coo_copy))
            #     else:
            #         knowledge_graph[tuple(level_key)] = tuple(level_value_coo_copy)
    print(level_key)
    print(knowledge_graph[tuple(level_key)])

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
