import random
import time

from pypbc import *
import hmac
import gmpy2
from gmpy2 import mpz
from web3 import Web3
import json
import os

random_length = 128

master_K_I = hmac.new(b'masterKI', digestmod='MD5').digest()
master_K_Z = hmac.new(b'masterKZ', digestmod='MD5').digest()
master_K_X = hmac.new(b'masterKX', digestmod='MD5').digest()

g1=mpz(2141434891434191460597654106285009794456474073127443963580690795002163321265105245635441519012876162226508712450114295048769820153232319693432987768769296824615642594321423205772115298200265241761445943720948512138315849294187201773718640619332629679913150151901308086084524597187791163240081868198195818488147354220506153752944012718951076418307414874651394412052849270568833194858516693284043743223341262442918629683831581139666162694560502910458729378169695954926627903314499763149304778624042360661276996520665523643147485282255746183568795735922844808611657078638768875848574571957417538833410931039120067791054495394347033677995566734192953459076978334017849678648355479176605169830149977904762004245805443987117373895433551186090322663122981978369728727863969397652199851244115246624405814648225543311628517631088342627783146899971864519981709070067428217313779897722021674599747260345113463261690421765416396528871227)
p = mpz(3268470001596555685058361448517594259852327289373621024658735136696086397532371469771539343923030165357102680953673099920140531685895962914337283929936606946054169620100988870978124749211273448893822273457310556591818639255714375162549119727203843057453108725240320611822327564102565670538516259921126103868685909602654213513456013263604608261355992328266121535954955860230896921190144484094504405550995009524584190435021785232142953886543340776477964177437292693777245368918022174701350793004000567940200059239843923046609830997768443610635397652600287237380936753914127667182396037677536643969081476599565572030244212618673244188481261912792928641006121759661066004079860474019965998840960514950091456436975501582488835454404626979061889799215263467208398224888341946121760934377719355124007835365528307011851448463147156027381826788422151698720245080057213877012399103133913857496236799905578345362183817511242131464964979)
q = mpz(93911948940456861795388745207400704369329482570245279608597521715921884786973)

Q = []

contract_instance = None

participant_FF = []
keyword_tid = {}
def constructData(path):
    files = [file for file in os.listdir(path)]
    # cnt = 0
    for file in files:
        participant_FF.append('requester'+file)
        keyword_tid[participant_FF[-1]] = {}
        path_tem = os.path.join(path, file)
        tid_files = [tid_file for tid_file in os.listdir(path_tem)]
        # cnt = cnt + 1
        for tid_file in tid_files:
            target = os.path.join(path_tem, tid_file)
            with open(target, "r") as f:
                for line in f.readlines():
                    content = line.split(",")
                    for con in content:
                        if con in keyword_tid[participant_FF[-1]]:
                            keyword_tid[participant_FF[-1]][con].append(tid_file+'_'+file)
                        else:
                            keyword_tid[participant_FF[-1]][con] = [tid_file+'_'+file]

def DeployContract(contract_path='../build/contracts/write.json'):  ############# 修改合约名字

    global contract_instance

    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545",request_kwargs={'timeout': 1000}))
    # w3.middleware_onion.add(requests.adapters.TimeoutAdapter(max_retries=1))


    with open(contract_path, 'r', encoding='utf-8') as contract_json_file:
        if contract_json_file is None:
            raise Exception("complied contract not found at " + contract_path)

        contract_json = json.load(contract_json_file)
        contract = w3.eth.contract(abi=contract_json['abi'], bytecode=contract_json['bytecode'])
        account = w3.eth.accounts[0]
        tx_hash = contract.constructor().transact({'from': w3.eth.accounts[0]})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        contractAddress = tx_receipt.contractAddress
        contract_instance = w3.eth.contract(address=contractAddress, abi=contract_json['abi'])

        return contract_instance, account, w3


store_var_contract, from_account, w3 = DeployContract()

def encode(cont):
    tem = ''
    for i in range(len(cont)):
        if isinstance(cont[i],int):
            tem = tem + 'i'+str(cont[i])
        else:
            tem = tem + 's'+cont[i]

        if i != len(cont)-1:
            tem = tem + '$'

    tem = tem.encode()
    return int.from_bytes(tem, byteorder='big', signed=False)

def decode(b):
    bb=int.to_bytes(b, 32, 'big').strip(b'\x00')
    s = bb.decode()
    res_tem = str(s).split('$')
    res = []
    for ss in res_tem:
        if ss[0] == 'i':
            res.append(int(ss[1:]))
        else:
            res.append(ss[1:])

    return res

# 生成指定长度的随机串，返回16进制字符串
def random_string(random_string_length):
    seed = "01"
    sa = []
    for i in range(random_string_length):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    salt_hex = hex(int(salt, 2))
    return salt_hex

# def localPad(data_hex):  # no 0x
#     # b = data_hex[2:]
#     return "0x" + '0' * (64 - len(data_hex[2:])) + data_hex[2:]

def genTest():
    Test = {}
    cnt = 0
    for i in range(10):
        keyword = 'keyword'+str(i)
        Test[keyword] = []
        for j in range(100):
            Test[keyword].append('tid'+str(cnt+j))
        cnt = cnt + 10
    return Test

########### 初始化阶段 ##########
# [输入] 无
# [输出] 1: 系统公共参数pk(pairing(Element库参数)，g(G2，指数运算底数)，alpha_ran(Zp,Algorithm.1-line 1)，beta_ran(Zp,Algorithm.1-line 1) )
#        2: 各个参与方的身份凭证participant_F(bytes)
#        3: 各参与方的密钥SK_list(gamma_ran(Zr,Algorithm.1-line 3)，sigma_key(ABE算法密钥，Algorithm.1-line 7))
################################
def initial():
    params = Parameters(qbits=512, rbits=160)  # type a
    pairing = Pairing(params)

    g = Element.random(pairing, G2)


    alpha_ran = Element.random(pairing, Zr)  # Algorithm.1-line 1
    beta_ran = Element.random(pairing, Zr)  # Algorithm.1-line 1

    pk = {'pairing': pairing, 'g': g, 'alpha_ran': alpha_ran, 'beta_ran': beta_ran}

    # participant = ["p1","p2","p3"]  # 所有参与者的ID
    # participant = ["p1"]
    attr_L = {0:"att1",1:"att2",2:"att3",3:"att4",4:"att5",5:"att6",6:"att7"}   # 所有参与者的属性集合

    participant_F = []
    SK_list = []

    for i in range(len(participant_FF)):   # Algorithm.1-line 2
        gamma_ran = Element.random(pairing, Zr) # Algorithm.1-line 3
        hash_value_gamma = Element.from_hash(pairing, G2, str(gamma_ran)) # Algorithm.1-line 7

        k = random_string(random_length)    # Algorithm.1-line 4

        F = hmac.new(k.encode(), participant_FF[i].encode(), digestmod='md5').digest() # Algorithm.1-line 5
        participant_F.append(F) # Algorithm.1-line 5

        sigma_key = {}
        sk ={}
        for att_name in attr_L: # Algorithm.1-line 6
            # print(attr_L[i][k_i])
            cat_i_y = str(beta_ran) + str(attr_L[att_name]) # Algorithm.1-line 7
            hash_value_i_y = Element.from_hash(pairing, Zr, cat_i_y)    # Algorithm.1-line 7
            sigma_i_y = Element(pairing, G2, value=g ** -hash_value_i_y)    # Algorithm.1-line 7
            cat_i_x = str(alpha_ran) + str(attr_L[att_name])    # Algorithm.1-line 7
            hash_value_i_x = Element.from_hash(pairing, Zr, cat_i_x)    # Algorithm.1-line 7
            sigma_i_x = Element(pairing, G2, value=hash_value_gamma ** hash_value_i_x)  # Algorithm.1-line 7
            sigma_i_k = Element(pairing, G2, value=sigma_i_y * sigma_i_x)   # Algorithm.1-line 7

            sigma_key[att_name] = sigma_i_k # Algorithm.1-line 7
        sk['gamma_ran'] = gamma_ran # Algorithm.1-line 8
        sk['sk']=sigma_key  # Algorithm.1-line 8
        SK_list.append(sk)  # Algorithm.1-line 8
        # 发送SK给各个参与者
    return pk,participant_F,SK_list

########### 构建索引阶段 ##########
# [输入] 1:系统公共参数pk
#       2:请求者的身份凭证participant_F
# [输出] 1:ACL Algorithm.2-line 23
#        2:ETID Algorithm.2-line 17
#        3:XSET Algorithm.2-line 19
#        4:temMap 未解决无法实现ABE解密而引入的临时map，用来获取WCnt Algorithm.2-line 20
################################
def buildIndex(pk, requester_f):
    ETID = {}
    ACL = []
    XSET = []
    temMap = {}
    # requester = ["re1", "re2", "re3"]
    # requester = ["re1"] # 测试用

    g = pk['g']
    pairing = pk['pairing']
    alpha_random = pk['alpha_ran']
    beta_random = pk['beta_ran']
    PB = pairing.apply(g, g) # Algorithm.2-line 6 e(g, g)
    access_policy = {0:"att1", 1:"att2", 2:"att3", 3:"att4", 4:"att5"} # 测试用的解密权限控制 请求者的属性集合
    # TSET = {"keyword1":["tid1","tid2","tid3"], "keyword2":["tid1","tid2","tid3","tid6"], "keyword3":["tid7","tid8","tid9"]}
    # TSET = genTest() # 生成临时的大数据测试文件 keyword-tid 对应的Map结构

    for i in range(len(requester_f)): # Algorithm.2-line 2
        ek_1 = Element.one(pairing, G2) # Algorithm.2-line 3
        ek_2 = Element.one(pairing, GT) # Algorithm.2-line 3
        WCnt = []   # Algorithm.2-line 3
        for j in range(len(access_policy)): # Algorithm.2-line 4
            cat_x = str(alpha_random) + str(access_policy[j])   # Algorithm.2-line 5
            hash_value_x = Element.from_hash(pairing, Zr, cat_x)    # Algorithm.2-line 5
            X_i_k = Element(pairing, G2, value=g ** -hash_value_x)  # Algorithm.2-line 5
            ek_1 = Element(pairing, G2, value=ek_1*X_i_k)   # Algorithm.2-line 5

            cat_y = str(beta_random) + str(access_policy[j])    # Algorithm.2-line 6
            hash_value_y = Element.from_hash(pairing, Zr, cat_y)    # Algorithm.2-line 6
            # 这里的双线性对使用了负号，可能存在错误的隐患
            Y_i_k = Element(pairing, GT, value=PB ** -hash_value_y) # Algorithm.2-line 6
            ek_2 = Element(pairing, GT, value=ek_2*Y_i_k)   # Algorithm.2-line 6


        for keyWord in keyword_tid[participant_FF[i]]:    # Algorithm.2-line 7
            cnt = 0 # Algorithm.2-line 8
            stag = hmac.new(master_K_X, keyWord.encode(), digestmod='md5').digest() # Algorithm.2-line 9
            for tid in keyword_tid[participant_FF[i]][keyWord]:   # Algorithm.2-line 10
                cnt = cnt + 1   # Algorithm.2-line 11
                z = hmac.new(master_K_Z, str(keyWord+str(cnt)).encode(), digestmod='md5').digest()  # Algorithm.2-line 12
                xind = hmac.new(master_K_I, tid.encode(), digestmod='md5').digest() # Algorithm.2-line 13

                zz = int.from_bytes(z, byteorder='big', signed=False)   # Algorithm.2-line 14
                inv_z = gmpy2.invert(mpz(zz), q)    # Algorithm.2-line 14
                # print(((mpz(zz)%q)*(mpz(inv_z)%q))%q)
                # print(mpz(zz))
                # print(mpz(inv_z))
                # y = gmpy2.mul(mpz(int.from_bytes(str.encode(xind), byteorder='big', signed=False)),inv_z)
                y = ((mpz(int.from_bytes(xind, byteorder='big', signed=False)) % q) * (mpz(inv_z) % q)) % q # Algorithm.2-line 14
                y = int(y)  # Algorithm.2-line 14
                # print('y',y)
                # y = Web3.toBytes(hexstr=hex(int(y))) # y的int结果可能超越32位表示范围
                # print(y)

                # stag 16字节+~F 16字节+cnt 15字节+补位 1字节
                string_addr = stag+requester_f[i]+cnt.to_bytes(length=15,byteorder='big',signed=False)+int(0).to_bytes(length=1,byteorder='big',signed=False)   # Algorithm.2-line 15
                addr = Web3.keccak(string_addr) # Algorithm.2-line 15
                # print('addr',string_addr)
                # addr = Web3.toBytes(hexstr=addr)
                # 占位方式同string_addr
                string_val = stag+requester_f[i]+cnt.to_bytes(length=15,byteorder='big',signed=False)+int(1).to_bytes(length=1,byteorder='big',signed=False)    # Algorithm.2-line 16
                val = Web3.keccak(string_val)   # Algorithm.2-line 16
                # val = Web3.toBytes(hexstr=val)

                tid_bytes = tid.ljust(len(val), '\x00') # Algorithm.2-line 16 将tid补位到异或运算需要的长度，高位补\x00
                tid_bytes = tid_bytes.encode()  # Algorithm.2-line 16

                val = bytes([x ^ y for x,y in zip(val, tid_bytes)]) # Algorithm.2-line 16

                ETID[addr]=[val,y]  # Algorithm.2-line 17

                ss = int.from_bytes(stag, byteorder='big', signed=False)    # Algorithm.2-line 18
                # print(ss)
                xx = int.from_bytes(xind, byteorder='big', signed=False)    # Algorithm.2-line 18
                # stag_xind = gmpy2.mul(mpz(ss),mpz(xx))
                stag_xind = ((mpz(ss) % q) * (mpz(xx) % q)) % q # Algorithm.2-line 18
                # print(stag_xind)

                # g1 = mpz(int.from_bytes(str(g).encode(), byteorder='big', signed=False))
                xtag = gmpy2.powmod(g1, mpz(stag_xind), p)  # Algorithm.2-line 18
                xtag = Web3.toBytes(hexstr=hex(int(xtag)))  # Algorithm.2-line 18
                # xtag = hex(int(xtag))
                # print(xtag)
                XSET.append(xtag)   # Algorithm.2-line 19

            WCnt.append(keyWord)    # Algorithm.2-line 20
            WCnt.append(cnt)    # Algorithm.2-line 20

        x = Element.random(pairing, Zr) # Algorithm.2-line 21

        ek_2_x = Element(pairing, GT, value=ek_2 ** x)  # Algorithm.2-line 22
        WCnt.append(requester_f[i]) # Algorithm.2-line 22
        # M = encode(WCnt) 真正计算M所需要的步骤
        # 这里因为无法进行ABE解密，暂时先没有真的进行加密，M随机取值
        M = 123
        M = Element(pairing, GT, value=M)   # Algorithm.2-line 22
        C_1 = Element(pairing, GT, value=M * ek_2_x)    # Algorithm.2-line 22
        C_2 = Element(pairing, G2, value=g ** x)    # Algorithm.2-line 22
        C_3 = Element(pairing, G2, value=ek_1 ** x) # Algorithm.2-line 22

        # C_1 = str.encode(str(C_1))
        # C_2 = str.encode(str(C_2))
        # C_3 = str.encode(str(C_3))


        ACL.append([access_policy, C_1, C_2, C_3])  # Algorithm.2-line 23

        temMap[str(C_1)] = WCnt # 因无法使用ABE解密，所使用的临时辅助数据

    # 将内容传给区块链
    return ACL, temMap, ETID, XSET

########### Token生成阶段 ##########
# [输入] 1:系统公共参数pk
#       2:授权属性集合和加密信息ACL
#       3:工作者密钥SK
#       4:解密临时变量temMap
# [输出] 1:search Token ST
#       2:cnt_max (所有可以搜索的请求者中最小频率keyword对应的最大文件数）
#       3:len(Q) （请求keyWord数量）
################################
def tokenGen(SK, ACL, PK, temMap):
    g = PK['g']
    # Q = ["keyword1", "keyword2"]
    # Q = ["keyword0", "keyword2","keyword5","keyword7","keyword8"]   # 请求KeyWord数量 查询请求
    # 获取ACL
    pairing = PK['pairing']
    cnt_max = 0 # Algorithm.3-line 2
    gamma_ran = SK['gamma_ran']
    sk = SK['sk']
    hash_val_gamma = Element.from_hash(pairing, G2, str(gamma_ran)) # Algorithm.3-line 6 提前计算，避免在循环中重复运算

    FF = []
    xtoken =[]
    # xtoken_tem = []

    for i in range(len(ACL)):   # Algorithm.3-line 3
        ask = Element.one(pairing, G2)  # Algorithm.3-line 4
        # ----------------# Algorithm.3-line 5 ---------------
        # 由于每个属性只有一个值，只需要看工作者是否存在对应属性就可以了，不存在就是解不开
        access_policy = ACL[i][0]
        ok = True
        for att_name in access_policy:
            if att_name in sk :
                ask = Element(pairing, G2, value= ask * sk[att_name])
            else:
                ok = False
                break

        if not ok:
            continue
        # ----------------# Algorithm.3-line 5 ---------------

        # -------------------解密过程，暂时有问题，先不起作用--------------------

        ask_c2 = pairing.apply(ask, ACL[i][2])
        gamma_c3 = pairing.apply(hash_val_gamma, ACL[i][3])
        ask_c2_gamma_c3 = Element(pairing, GT, value = ask_c2*gamma_c3)

        M = Element(pairing, GT, value = ACL[i][1]*(ask_c2_gamma_c3 ** (-1)))

        # -------------------解密过程，暂时有问题，先不起作用--------------------

        M = temMap[str(ACL[i][1])]  # Algorithm.3-line 6 暂时先从临时数据结构中获得解密后的结果

        F = M[-1]   # Algorithm.3-line 8 获取Wcnt
        for j in range(int((len(M)-1)/2)):  # Algorithm.3-line 7
            if M[2*j] == Q[0]:  # Algorithm.3-line 7
                FF.append(F)    # Algorithm.3-line 9
                if M[2*j+1] > cnt_max:  # Algorithm.3-line 10
                    cnt_max = M[2*j+1]  # Algorithm.3-line 11
                break

    stag = hmac.new(master_K_X, Q[0].encode(), digestmod='md5').digest()    # Algorithm.3-line 12
    # stag = Web3.toBytes(hexstr='0x'+stag)

    for i in range(cnt_max):    # Algorithm.3-line 13
        xtoken.append([])
        # xtoken_tem.append([])
        cat = Q[0] + str(i+1)   # Algorithm.3-line 16
        z = hmac.new(master_K_Z, cat.encode(), digestmod='md5').digest()    # Algorithm.3-line 16
        z = mpz(int.from_bytes(z, byteorder='big', signed=False))   # Algorithm.3-line 16

        for j in range(len(Q)): # Algorithm.3-line 14
            # --------------第一个位置用不到，补\x00占位 -------------
            if j==0 :
               # xtoken_tem[i].append(bytes(0))
               xtoken[i].append(bytes(0)) # 占位符，无意义
               continue
            # --------------第一个位置用不到，补\x00占位 -------------
            wj_tem = hmac.new(master_K_X, Q[j].encode(), digestmod='md5').digest()  # Algorithm.3-line 15
            ww = int.from_bytes(wj_tem,byteorder='big', signed=False)   # Algorithm.3-line 15
            # w_z = ((mpz(z)%q)*(mpz(ww)%q))%q
            # xtoken_tem[i].append(w_z)

            # print(ww)
            # g1 = mpz(int.from_bytes(str(g).encode(), byteorder='big', signed=False))
            # ww_zz = gmpy2.mul(ww,z)
            ww_zz = ((mpz(ww)%q)*(mpz(z)%q))%q  # Algorithm.3-line 17

            # xtrap = gmpy2.powmod(g1, ww, p)
            # xtrap_z = gmpy2.powmod(xtrap, z, p)
            xtrap_z = gmpy2.powmod(g1,ww_zz,p)  # Algorithm.3-line 17
            xtrap_z = Web3.toBytes(hexstr=hex(int(xtrap_z)))    # Algorithm.3-line 17
            # print('xtrap_z',xtrap_z.__len__()) 某些情况下长度不足384 需要补位
            if xtrap_z.__len__() != 384 :
                xtrap_z = int(0).to_bytes(length=1,byteorder='big',signed=False)+ xtrap_z
                print('care there',i,j)
            # xtrap_z = xtrap_z.zfill(384)
            # xtrap_z = hex(int(xtrap_z))
            xtoken[i].append(xtrap_z)   # Algorithm.3-line 17

    ST = [FF, stag, xtoken] # Algorithm.3-line 18
    return ST,cnt_max,len(Q)
    # 将上述内容部署在区块链上

# def TaskMatch(FF, cnt_max, stag, ETID, n, xtoken, XSET):
#     Res =[]
#     for F in FF:
#         for i in range(cnt_max):
#             cat = stag + str(F) + Web3.toHex(i+1)[2:] +'0'
#             addr = Web3.keccak(hexstr=cat).hex()
#             addr = Web3.toBytes(hexstr=addr)
#
#             if addr in ETID:
#                 val,y = ETID[addr]
#
#                 exist = True
#                 for j in range(n):
#                     if j==0:
#                         continue
#                     # print(y)
#                     # xtoken_t = int.from_bytes(xtoken[i][j],byteorder='big', signed=False)
#                     # y_t= int.from_bytes(y,byteorder='big', signed=False)
#                     # xtoken_y = gmpy2.powmod(mpz(xtoken_t), mpz(y_t), p)
#                     # xtoken_y = Web3.toBytes(hexstr=hex(int(xtoken_y)))
#                     tem_test = ((mpz(xtoken_tem[i][j])%q)*(mpz(y)%q))%q
#                     # print(tem_test)
#                     xtoken_y = gmpy2.powmod(xtoken[i][j], mpz(y), p)
#                     # print(xtoken_y)
#                     if xtoken_y not in XSET:
#                         # print('not')
#                         exist = False
#                         break
#
#                 if exist:
#                     cat = stag + str(F) + Web3.toHex(i+1)[2:] +'1'
#                     hash_cat = Web3.keccak(hexstr=cat).hex()
#                     cat_bytes = Web3.toBytes(hexstr=hash_cat)
#
#                     tid = bytes([x ^ y for x, y in zip(val, cat_bytes)])
#                     tid = tid.lstrip(b'\x00').decode()
#
#                     Res.append(tid)
#     return Res

if __name__ == '__main__':
    # from_account = w3.toChecksumAddress("0x3c62Aa7913bc303ee4B9c07Df87B556B6770E3fC")
    # abi_build_index = json.loads(abi_build_index)
    # store_var_contract = w3.eth.contract(address=w3.toChecksumAddress('0x903b76aF4e3a88D27148905D1a8141D84657ac65'), abi=abi_build_index)

    #p_hex = hex(int(p))
    #tx_setP_hash = store_var_contract.functions.setP(p_hex).transact(
    #    {"from": from_account, "gas": 3000000, "gasPrice": 0})
    #tx_receipt = w3.eth.waitForTransactionReceipt(tx_setP_hash)
    #print('---------setP', tx_receipt.status, tx_receipt.gasUsed)
    Q = ['a','d','c']   # 构建问询

    print("--------------从文件构建数据集--------")
    constructData('/Users/yuzhemeng/PycharmProjects/PFTMcrowd/dataset_test') # 从文件读取数据，替换路径
    print("--------------构建数据集完成--------")

    print("--------------Initialization--------")
    time_start = time.time()  # 记录开始时间
    pk,ptf,sk_list = initial()
    time_end = time.time()  # 记录结束时间
    print("--------------Initialization Finsh!--------")
    print("消耗时间",str(time_end - time_start)+'s')
    # print(pk['g'])
    # print(int.from_bytes(str(pk['g']).encode(),byteorder='big', signed=False))
    # print(pk['pairing'])
    # print(pk['alpha_ran'])
    # print(pk['beta_ran'])
    # print(ptf)

    print("--------------Build Index--------")
    time_start = time.time()  # 记录开始时间
    ACL,temMap,ETID,XSET = buildIndex(pk,ptf)


    access_policy_list = []
    c1_list = []
    c2_list = []
    c3_list = []
    addr_list = []
    ETID_val_list = []
    ETID_y_list = []

    for i in range(len(ACL)):
        access_policy_list.append(str(ACL[i][0]).encode())
        c1_list.append(str(ACL[i][1]).encode())
        c2_list.append(str(ACL[i][2]).encode())
        c3_list.append(str(ACL[i][3]).encode())

    for key in ETID:
        addr_list.append(key)
        ETID_val_list.append(ETID[key][0])
        ETID_y_list.append(ETID[key][1])
        # print(key.__len__(),ETID[key][1])

    tx_set_access_policy_hash = store_var_contract.functions.set_access_policy(access_policy_list, len(access_policy_list)).transact({"from": from_account, "gas": 6000000, "gasPrice": 0})
    # tx_receipt = w3.eth.waitForTransactionReceipt(tx_set_access_policy_hash)
    # print('---------set access_policy', tx_receipt.status, tx_receipt.gasUsed)

    tx_set_c1 = store_var_contract.functions.set_c1(c1_list, len(c1_list)).transact({"from": from_account, "gas": 6000000, "gasPrice": 0})
    # tx_receipt = w3.eth.waitForTransactionReceipt(tx_set_c1)
    # print('---------set c1', tx_receipt.status, tx_receipt.gasUsed)

    tx_set_c2 = store_var_contract.functions.set_c2(c2_list, len(c2_list)).transact({"from": from_account, "gas": 6000000, "gasPrice": 0})
    # tx_receipt = w3.eth.waitForTransactionReceipt(tx_set_c2)
    # print('---------set c2', tx_receipt.status, tx_receipt.gasUsed)

    tx_set_c3 = store_var_contract.functions.set_c3(c3_list, len(c3_list)).transact({"from": from_account, "gas": 6000000, "gasPrice": 0})
    # tx_receipt = w3.eth.waitForTransactionReceipt(tx_set_c3)
    # print('---------set c3', tx_receipt.status, tx_receipt.gasUsed)

    tx_set_ETID_val = store_var_contract.functions.set_ETID_val(addr_list ,ETID_val_list, len(ETID_val_list)).transact({"from": from_account, "gas": 600000000, "gasPrice": 0})
    # tx_receipt = w3.eth.waitForTransactionReceipt(tx_set_ETID_val)
    # print('---------set ETID val', tx_receipt.status, tx_receipt.gasUsed)

    tx_set_ETID_y = store_var_contract.functions.set_ETID_y(addr_list ,ETID_y_list, len(ETID_y_list)).transact({"from": from_account, "gas": 600000000, "gasPrice": 0})
    # tx_receipt = w3.eth.waitForTransactionReceipt(tx_set_ETID_y)
    # print('---------set ETID y', tx_receipt.status, tx_receipt.gasUsed)

    # print(XSET)

    tx_XSET_add = store_var_contract.functions.XSET_add(XSET ,len(XSET)).transact({"from": from_account, "gas": 600000000, "gasPrice": 0})
    # tx_receipt = w3.eth.waitForTransactionReceipt(tx_XSET_add, timeout=10000)
    # print('---------set XSET', tx_receipt.status, tx_receipt.gasUsed)
    time_end = time.time()  # 记录结束时间
    print("--------------Build Index Finsh！--------")
    print("消耗时间", str(time_end - time_start) + 's')



    print('--------------Token Generation-----------------')
    time_start = time.time()  # 记录开始时间
    ST,cnt_max,n_max = tokenGen(sk_list[0],ACL,pk,temMap)

    xtoken = ST[2]
    FF = ST[0]
    stag = ST[1]
    # print(len(ST[0]))
    # print('cnt_max',cnt_max)
    # print('FF',FF)
    tx_set_FF_hash = store_var_contract.functions.set_FF(FF, len(FF)).transact(
        {"from": from_account, "gas": 600000000, "gasPrice": 0})
    # tx_receipt = w3.eth.waitForTransactionReceipt(tx_set_FF_hash)
    # print('---------set_FF', tx_receipt.status, tx_receipt.gasUsed)

    tx_set_stag_hash = store_var_contract.functions.set_stag(stag).transact(
        {"from": from_account, "gas": 600000000, "gasPrice": 0})
    # tx_receipt = w3.eth.waitForTransactionReceipt(tx_set_stag_hash)
    # print('---------set_stag', tx_receipt.status, tx_receipt.gasUsed)

    # n_max = 2
    for i in range(cnt_max):
        xtoken_tem =xtoken[i]
        # print(xtoken_tem)
        tx_set_ST_w_hash = store_var_contract.functions.set_ST_w(i+1, xtoken_tem, n_max).transact(
            {"from": from_account, "gas": 600000000, "gasPrice": 0})
        # tx_receipt = w3.eth.waitForTransactionReceipt(tx_set_ST_w_hash)
        # print('---------set_ST_w', tx_receipt.status, tx_receipt.gasUsed)
    time_end = time.time()  # 记录结束时间
    print('--------------Token Generation Finsh!-----------------')
    print("消耗时间", str(time_end - time_start) + 's')


    print('---------Search Result-------------')
    time_start = time.time()  # 记录开始时间
    # print(len(FF),cnt_max)
    # print('cnt_max',cnt_max,len(FF))
    tx_TaskMatching_hash = store_var_contract.functions.TaskMatching(cnt_max, len(FF), n_max).transact(
        {"from": from_account, "gas": 600000000, "gasPrice": 0})
    # tx_receipt = w3.eth.waitForTransactionReceipt(tx_TaskMatching_hash)
    # print('---------onchain_search', tx_receipt.status, tx_receipt.gasUsed)
    time_end = time.time()  # 记录结束时间
    print('---------Search Result Finsh-------------')
    print("消耗时间", str(time_end - time_start) + 's')

    testR = store_var_contract.functions.get_returnR_u().call()
    # print('testR', type(testR), len(testR), testR)
    for ss in testR:
        print('res',ss.decode().strip('\x00'))

    code = store_var_contract.functions.get_code().call()
    print('code', code)

    # testaddr = store_var_contract.functions.get_test_addr().call()

    # print('test_addr', testaddr)

    # Res = TaskMatch(ST[0], cnt_max, ST[1], ETID, 2, ST[2], XSET, xtoken_tem)
    # print(Res)


