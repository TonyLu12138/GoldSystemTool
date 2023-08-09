import cmath
import logging
from tqdm import tqdm
import configparser

# 配置日志记录
logging.basicConfig(filename='output.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# 使用configparser读取配置文件
config = configparser.ConfigParser()
config.read('input.ini')

# 读取配置
r_ = int(config['r_']['r_'])
i_ = int(config['i_']['i_'])
detailed_logging = config.getboolean('debug', 'detailed_logging')
show_progress_bar = detailed_logging

# 计算平方根
def root(num):
    with tqdm(total=100, desc="计算平方根进度", disable=not show_progress_bar) as pbar:
        square_root = cmath.sqrt(num)
        pbar.update(100)
    return square_root

def main():
    if detailed_logging:
        logging.debug("文件：%s", __file__)
        logging.debug("开始执行函数：%s", main.__name__)

    number = complex(r_, i_)
    root_result = root(number)

    if detailed_logging:
        print("复数的平方根：", root_result, " and ", -root_result)
        logging.debug("复数的平方根：%s and %s", root_result, -root_result)
        if root_result.real == 0:
            print("实部的平方根：", root_result.real)
            logging.debug("实部的平方根：%s", root_result.real)
        else:
            print("实部的平方根：", root_result.real, " and ", -root_result.real)
            logging.debug("实部的平方根：%s and %s", root_result.real, -root_result.real)
        if root_result.imag == 0:
            print("虚部的平方根：", root_result.imag)
            logging.debug("虚部的平方根：%s", root_result.imag)
        else:
            print("虚部的平方根：", root_result.imag, " and ", -root_result.imag)
            logging.debug("虚部的平方根：%s and %s", root_result.imag, -root_result.imag)
    else:
        logging.debug("开始执行操作 A")
        logging.debug("开始执行操作 B")

    try:
        operation_B()

    except Exception as e:
        if detailed_logging:
            # 输出异常信息
            logging.exception("程序发生异常：%s", str(e))
        else:
            logging.error("程序发生异常：%s", str(e))

def operation_B():
    if detailed_logging:
        if show_progress_bar:
            for _ in tqdm(range(100), desc="操作 B 进度"):
                pass
    # 模拟操作 B
    return 10 / 0

if __name__ == '__main__':
    main()
