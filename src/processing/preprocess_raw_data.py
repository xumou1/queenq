import pandas as pd
import numpy as np
import logging
from pathlib import Path
import re
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_directories():
    """确保必要的目录存在"""
    Path("data/raw").mkdir(parents=True, exist_ok=True)

def clean_registered_capital(value):
    """清理注册资本字段，将中文单位转换为数值"""
    if pd.isna(value):
        return np.nan
    
    # 将值转换为字符串
    value = str(value)
    
    # 移除逗号和空格
    value = value.replace(',', '').replace(' ', '')
    
    # 提取数字部分
    match = re.search(r'([\d.]+)', value)
    if not match:
        return np.nan
    
    number = float(match.group(1))
    
    # 根据单位进行转换
    if '万' in value:
        number *= 10000
    
    return number

def clean_percentage(value):
    """清理百分比字段，将百分比转换为小数"""
    if pd.isna(value):
        return np.nan
    
    # 将值转换为字符串
    value = str(value)
    
    # 移除百分号和空格
    value = value.replace('%', '').replace(' ', '')
    
    try:
        return float(value) / 100
    except ValueError:
        return np.nan

def clean_currency(value):
    """清理货币字段，移除货币符号和逗号"""
    if pd.isna(value):
        return np.nan
    
    # 将值转换为字符串
    value = str(value)
    
    # 移除货币符号、逗号和空格
    value = value.replace('元', '').replace(',', '').replace(' ', '')
    
    try:
        return float(value)
    except ValueError:
        return np.nan

def process_company_info():
    """处理供应链公司基本信息"""
    try:
        # 读取Excel文件
        df = pd.read_excel('data/raw/供应链公司基本信息.xlsx')
        
        # 定义列映射
        column_mapping = {
            '公司名称': 'Comname',
            '公司编号': 'Conumb',
            '公司分类': 'Coclasf',
            '是否上市': 'Lstrorn',
            '公司股票代码': 'LstScode',
            '注册资本': 'Rgscpt',
            '经营状态': 'Magmtst',
            '公司类型': 'Cotype',
            '核准日期': 'Aprdt',
            '所属地区': 'Area',
            '曾用名': 'Usednm',
            '成立日期': 'Etbmtdt',
            '所属行业': 'Industry',
            '企业地址': 'Regaddr',
            '经营范围': 'Busiscope'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 数据清理和转换
        df['Lstrorn'] = df['Lstrorn'].map({'是': 1, '否': 0})
        df['Rgscpt'] = df['Rgscpt'].apply(clean_registered_capital)
        
        # 转换日期字段
        for date_col in ['Aprdt', 'Etbmtdt']:
            try:
                # 移除可能的表头值
                df[date_col] = df[date_col].replace({
                    '核准日期': pd.NaT,
                    '成立日期': pd.NaT
                })
                # 转换日期格式
                df[date_col] = pd.to_datetime(df[date_col], format='%Y-%m-%d', errors='coerce')
            except Exception as e:
                logger.warning(f"无法转换日期列 {date_col}: {str(e)}")
        
        # 保存为CSV
        df.to_csv('data/raw/supply_chain_company_info.csv', index=False, encoding='utf-8')
        logger.info("成功处理供应链公司基本信息")
        
    except Exception as e:
        logger.error(f"处理供应链公司基本信息时出错: {str(e)}")

def process_suppliers():
    """处理上市公司供应商信息"""
    try:
        # 读取Excel文件
        df = pd.read_excel('data/raw/上市公司供应商名称及采购额.xlsx')
        
        # 定义列映射
        column_mapping = {
            '股票代码': 'Scode',
            '公司简称': 'Coname',
            '公告日期': 'Anncdate',
            '序号': 'Num',
            '供应商名称': 'Suplnm',
            '公司编号': 'Conumb',
            '是否上市公司': 'Lstrorn',
            '公司股票代码': 'LstScode',
            '参控关系': 'Ctlprtrlat',
            '采购金额(元)': 'Suplpa',
            '采购占比(%)': 'Suplpart'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 数据清理和转换
        df['Num'] = pd.to_numeric(df['Num'], errors='coerce')
        df['Lstrorn'] = df['Lstrorn'].map({'是': 1, '否': 0})
        df['Suplpa'] = df['Suplpa'].apply(clean_currency)
        df['Suplpart'] = df['Suplpart'].apply(clean_percentage)
        
        # 转换日期字段
        try:
            # 移除可能的表头值
            df['Anncdate'] = df['Anncdate'].replace({
                '公告日期': pd.NaT
            })
            # 转换日期格式
            df['Anncdate'] = pd.to_datetime(df['Anncdate'], format='%Y-%m-%d', errors='coerce')
        except Exception as e:
            logger.warning(f"无法转换日期列 Anncdate: {str(e)}")
        
        # 保存为CSV
        df.to_csv('data/raw/listed_company_suppliers.csv', index=False, encoding='utf-8')
        logger.info("成功处理上市公司供应商信息")
        
    except Exception as e:
        logger.error(f"处理上市公司供应商信息时出错: {str(e)}")

def process_customers():
    """处理上市公司客户信息"""
    try:
        # 读取Excel文件
        df = pd.read_excel('data/raw/上市公司客户名称及收入.xlsx')
        
        # 定义列映射
        column_mapping = {
            '股票代码': 'Scode',
            '公司简称': 'Coname',
            '公告日期': 'Anncdate',
            '序号': 'Num',
            '客户名称': 'Custnm',
            '公司编号': 'Conumb',
            '是否上市公司': 'Lstrorn',
            '公司股票代码': 'LstScode',
            '参控关系': 'Ctlprtrlat',
            '客户收入': 'Custinc',
            '客户收入占比（%）': 'Custincrt'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 数据清理和转换
        df['Num'] = pd.to_numeric(df['Num'], errors='coerce')
        df['Lstrorn'] = df['Lstrorn'].map({'是': 1, '否': 0})
        df['Custinc'] = df['Custinc'].apply(clean_currency)
        df['Custincrt'] = df['Custincrt'].apply(clean_percentage)
        
        # 转换日期字段
        try:
            # 移除可能的表头值
            df['Anncdate'] = df['Anncdate'].replace({
                '公告日期': pd.NaT
            })
            # 转换日期格式
            df['Anncdate'] = pd.to_datetime(df['Anncdate'], format='%Y-%m-%d', errors='coerce')
        except Exception as e:
            logger.warning(f"无法转换日期列 Anncdate: {str(e)}")
        
        # 保存为CSV
        df.to_csv('data/raw/listed_company_customers.csv', index=False, encoding='utf-8')
        logger.info("成功处理上市公司客户信息")
        
    except Exception as e:
        logger.error(f"处理上市公司客户信息时出错: {str(e)}")

def main():
    """主函数"""
    setup_directories()
    process_company_info()
    process_suppliers()
    process_customers()

if __name__ == "__main__":
    main() 