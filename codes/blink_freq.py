#!encoding=utf8
# from parse import Parse


from utils.crc16 import modify_str as modify
from utils.bytes import ord_to_hex
# "得到输入的json.解析得到{"pm0":500,"pm1":1000}"
# "和错误代码(返回的)"
# "错误代码只能是0,或-110"



# class Code(object):
#     # 开几个温湿度模块
#     def __init__(self,module_id,freq):
#         self.module_id=module_id
#         self.freq=freq

#     @property    
#     def code(self):
#         if self.amount==0:
#             result="%s0600080000"%ord_to_hex(self.address)

#             return "%s0600080000"%ord_to_hex(self.address)
#         else:
#             result="%s06000801%s"%(ord_to_hex(self.address),ord_to_hex(self.amount))

#         return modify_str(result.decode("hex"))

#     def __repr__(self):
#         return "<SetTempHum>[address %s][%s Sensor]"%(self.address,self.amount)




def parse(raw_status, dic):
    # "输入raw_status,dic,输出[运行代码，缓存状态dict:{"pm01":3000,"pm02":500}   和错误状态。输出缓存状态以便存盘重现。"
    def valid(u_id,period):
        if not raw_status.get(u_id):
            return 0
        if type(period)!=int:
            return 0
        return 1



    to_cache = {}
    codes = []


    middle_results, error_data = to_middle_state(dic)

    if error_data.get("err_code"):
        # 如果err_code不为零，即有错误。
        print("数据错误：err_code", error_data)
        return (None, to_cache, error_data)

    for (u_id, period) in middle_results.items():
        if not valid(u_id,period):
            if not error_data.get("data"):
                error_data["data"] = []
            error_data["data"].append("<u_id:%s><period:%s> not valid"%(u_id,period))
            continue

        code=Code(u_id,period,raw_status)
        to_cache[u_id] = period

        # result = to_code(raw_status, u_id, period)

        # 如果没有data key,增加一个。

        codes.append(code)
    # 这里将两段的错误码拼了起来。达到了不损失细节的目的。
    # if not error_data:
    print("codes,to_cache,error_data====", codes, to_cache, error_data)
    return (codes, to_cache, error_data)


def to_middle_state(dic):
    "输入经json解析的dic,输出[(index,freq),...]的中间态，和错误代码。过滤无效的输入。这样设计，是为了容易写代码。每次输出，中间态的结构都变了。只有错误代码没变。这就导致中间件的衔接顺序是固定的。这不是常规意义的中间件。"
    error_data = {"err_code": 0}
    results = {}
    data = dic.get("data")

    if not data:
        error_data = {"err_code": -3}
        return (results, error_data)

    for module in data:
        if not module.get("u_id"):
            continue
        if not module.get("u_blinkfreq"):
            continue

        results[module.get("u_id")] = module.get("u_blinkfreq")

    return (results, error_data)


# def to_code(raw_status, u_id, period):
#     "传入raw_status,id,freq,生成一条命令。freq 范围500-3000的整数。如果超范围应该自动修正。生成code和error."
#     error = {}

#     if not raw_status.get(u_id):

#         print("u_id", u_id)
#         error[u_id] = "unknown u_id"
#         return (None, error)

#     # try:
#     if type(period) == float:
#         period = int(round(period))

#     if type(period) != int:
#         try:
#             period = int(period)
#         except Exception as e:
#             error[u_id] = str(e)

#         return (None, error)

#     time_para = period // 100 - 5

#     # 在前面的api里应该检测传入的数据类型，如果不对就返回相应的错误。
#     if time_para < 0:
#         time_para = 0
#     if time_para > 25:
#         time_para = 25

#     module_index = raw_status.get(u_id).get("address")

#     code = CODE(module_index, time_para)
#     # print("codeafterCRC", code.command)
#     # print("code.beforeCRC", code.all_but_crc)
#     return (code, None)


class Code:


    def __init__(self, u_id, period,raw_status):
        self.u_id=u_id
        self.period=period
        self.raw_status=raw_status

    # @property
    # def all_but_crc(self):
    #     return self.index + self.static + self.para

    @property
    def code(self):
        # print(self.all_but_crc)
        module_index = self.raw_status.get(self.u_id).get("address")
        self.index = ord_to_hex(module_index)
        time_para = self.period // 100 - 5
        para = ("0%s" % hex(time_para)[2:])[-2:]
        all_but_crc=self.index + "06002C00" + para
        return modify(all_but_crc.decode("hex"))


    def __repr__(self):
        return "<LightFrequency>module_id:<%s>period:<%s>"%(self.u_id,self.period)


# class CODE:
#     index_dic = {1: "01", 2: "02"}
#     index = ""
#     static = "06002C00"
#     para = ""
#     crc = ""

#     def __init__(self, index, para):
#         self.index = self.index_dic.get(index)
#         self.para = ("0%s" % hex(para)[2:])[-2:]

#     @property
#     def all_but_crc(self):
#         return self.index + self.static + self.para

#     @property
#     def code(self):
#         # print(self.all_but_crc)
#         return modify((self.all_but_crc).decode("hex"))

#     def __repr__(self):
#         return "<address %s><freq>"