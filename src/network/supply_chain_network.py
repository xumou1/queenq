import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import logging
from thefuzz import fuzz
import re
from typing import Dict, List, Set, Tuple, Optional
import plotly.graph_objects as go
from datetime import datetime
import json
import pickle

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompanyEntityResolver:
    """公司实体解析器，用于识别和统一公司实体"""
    
    def __init__(self, fuzzy_threshold: float = 80):
        self.fuzzy_threshold = fuzzy_threshold
        self.company_suffixes = [
            '有限公司', '股份公司', '集团公司', '集团', '公司',
            'Ltd.', 'Co.', 'Inc.', 'Corp.', 'Corporation'
        ]
        self.name_to_id: Dict[str, str] = {}
        self.id_to_attributes: Dict[str, Dict] = {}
        self.next_id = 1
    
    def normalize_company_name(self, name: str) -> str:
        """标准化公司名称"""
        if pd.isna(name):
            return ""
        
        # 转换为小写并去除空格
        name = str(name).lower().strip()
        
        # 移除公司后缀
        for suffix in self.company_suffixes:
            name = name.replace(suffix.lower(), '')
        
        # 移除多余空格
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def get_unique_id(self, name: str) -> str:
        """获取或创建公司唯一ID"""
        normalized_name = self.normalize_company_name(name)
        if not normalized_name:
            return None
        
        # 检查是否已存在
        if normalized_name in self.name_to_id:
            return self.name_to_id[normalized_name]
        
        # 创建新ID
        new_id = f"node_id_{self.next_id:03d}"
        self.next_id += 1
        self.name_to_id[normalized_name] = new_id
        return new_id
    
    def add_company_attributes(self, node_id: str, attributes: Dict):
        """添加公司属性"""
        if node_id not in self.id_to_attributes:
            self.id_to_attributes[node_id] = {}
        self.id_to_attributes[node_id].update(attributes)
    
    def find_similar_company(self, name: str) -> Tuple[str, float]:
        """使用模糊匹配查找相似公司"""
        normalized_name = self.normalize_company_name(name)
        if not normalized_name:
            return None, 0
        
        best_match = None
        best_score = 0
        
        for existing_name in self.name_to_id.keys():
            score = fuzz.token_set_ratio(normalized_name, existing_name)
            if score > best_score and score >= self.fuzzy_threshold:
                best_score = score
                best_match = existing_name
        
        return best_match, best_score

class SupplyChainNetwork:
    """供应链网络构建和分析类"""
    
    def __init__(self, graph_path: str = 'data/processed/supply_chain_graph.gpickle'):
        self.resolver = CompanyEntityResolver()
        self.graph = nx.DiGraph()
        self.df_nodes = None
        self.graph_path = graph_path
    
    def save_network(self):
        """保存网络到文件"""
        try:
            Path(self.graph_path).parent.mkdir(parents=True, exist_ok=True)
            nx.write_gpickle(self.graph, self.graph_path)
            logger.info(f"网络已保存到: {self.graph_path}")
        except Exception as e:
            logger.error(f"保存网络时出错: {str(e)}")
            raise
    
    def load_network(self) -> bool:
        """从文件加载网络
        
        Returns:
            bool: 是否成功加载网络
        """
        try:
            if Path(self.graph_path).exists():
                self.graph = nx.read_gpickle(self.graph_path)
                logger.info(f"从 {self.graph_path} 加载网络成功")
                return True
            return False
        except Exception as e:
            logger.error(f"加载网络时出错: {str(e)}")
            return False
    
    def build_or_load_network(self, force_rebuild: bool = False):
        """构建或加载网络
        
        Args:
            force_rebuild (bool): 是否强制重新构建网络
        """
        if not force_rebuild and self.load_network():
            return
        
        logger.info("开始构建网络...")
        self.load_data()
        self.resolve_entities()
        self.build_network()
        self.identify_shared_suppliers()
        self.save_network()
        logger.info("网络构建完成")
    
    def load_data(self):
        """加载数据文件"""
        try:
            self.df_company_info = pd.read_csv('data/raw/supply_chain_company_info.csv')
            self.df_suppliers = pd.read_csv('data/raw/listed_company_suppliers.csv')
            self.df_customers = pd.read_csv('data/raw/listed_company_customers.csv')
            
            # 显示基本信息
            for name, df in [
                ('公司基本信息', self.df_company_info),
                ('供应商信息', self.df_suppliers),
                ('客户信息', self.df_customers)
            ]:
                logger.info(f"\n{name} 数据概览:")
                logger.info(f"行数: {len(df)}")
                logger.info(f"列: {', '.join(df.columns)}")
                logger.info("\n前5行数据:")
                logger.info(df.head())
                
        except Exception as e:
            logger.error(f"加载数据时出错: {str(e)}")
            raise
    
    def resolve_entities(self):
        """解析公司实体"""
        # 1. 首先处理公司基本信息
        for _, row in self.df_company_info.iterrows():
            node_id = self.resolver.get_unique_id(row['Comname'])
            if node_id:
                self.resolver.add_company_attributes(node_id, {
                    'canonical_name': row['Comname'],
                    'company_id': row['Conumb'],
                    'company_class': row['Coclasf'],
                    'is_listed': row['Lstrorn'],
                    'stock_code': row['LstScode'],
                    'industry': row['Industry'],
                    'area': row['Area'],
                    'registered_capital': row['Rgscpt']
                })
        
        # 2. 处理供应商关系
        for _, row in self.df_suppliers.iterrows():
            # 处理上市公司
            listed_company_id = self.resolver.get_unique_id(row['Coname'])
            if listed_company_id:
                self.resolver.add_company_attributes(listed_company_id, {
                    'canonical_name': row['Coname'],
                    'stock_code': row['Scode'],
                    'is_listed': 1
                })
            
            # 处理供应商
            supplier_id = self.resolver.get_unique_id(row['Suplnm'])
            if supplier_id:
                self.resolver.add_company_attributes(supplier_id, {
                    'canonical_name': row['Suplnm'],
                    'company_id': row['Conumb'],
                    'is_listed': row['Lstrorn']
                })
        
        # 3. 处理客户关系
        for _, row in self.df_customers.iterrows():
            # 处理上市公司
            listed_company_id = self.resolver.get_unique_id(row['Coname'])
            if listed_company_id:
                self.resolver.add_company_attributes(listed_company_id, {
                    'canonical_name': row['Coname'],
                    'stock_code': row['Scode'],
                    'is_listed': 1
                })
            
            # 处理客户
            customer_id = self.resolver.get_unique_id(row['Custnm'])
            if customer_id:
                self.resolver.add_company_attributes(customer_id, {
                    'canonical_name': row['Custnm'],
                    'company_id': row['Conumb'],
                    'is_listed': row['Lstrorn']
                })
        
        # 4. 创建节点DataFrame
        self.df_nodes = pd.DataFrame.from_dict(
            self.resolver.id_to_attributes,
            orient='index'
        ).reset_index()
        self.df_nodes.rename(columns={'index': 'unique_node_id'}, inplace=True)
        
        logger.info(f"\n解析后的唯一公司数量: {len(self.df_nodes)}")
    
    def build_network(self):
        """构建网络"""
        # 1. 添加节点
        for _, row in self.df_nodes.iterrows():
            self.graph.add_node(
                row['unique_node_id'],
                **row.to_dict()
            )
        
        # 2. 添加供应商关系边
        for _, row in self.df_suppliers.iterrows():
            supplier_id = self.resolver.get_unique_id(row['Suplnm'])
            listed_company_id = self.resolver.get_unique_id(row['Coname'])
            
            if supplier_id and listed_company_id:
                self.graph.add_edge(
                    supplier_id,
                    listed_company_id,
                    relationship_type='supplier',
                    procurement_amount=row['Suplpa'],
                    procurement_share=row['Suplpart'],
                    announcement_date=row['Anncdate']
                )
        
        # 3. 添加客户关系边
        for _, row in self.df_customers.iterrows():
            listed_company_id = self.resolver.get_unique_id(row['Coname'])
            customer_id = self.resolver.get_unique_id(row['Custnm'])
            
            if listed_company_id and customer_id:
                self.graph.add_edge(
                    listed_company_id,
                    customer_id,
                    relationship_type='customer',
                    revenue=row['Custinc'],
                    revenue_share=row['Custincrt'],
                    announcement_date=row['Anncdate']
                )
        
        logger.info(f"\n网络统计:")
        logger.info(f"节点数: {self.graph.number_of_nodes()}")
        logger.info(f"边数: {self.graph.number_of_edges()}")
    
    def identify_shared_suppliers(self):
        """识别共享供应商"""
        # 计算每个供应商的客户数量
        supplier_customer_counts = {}
        for node in self.graph.nodes():
            if self.graph.out_degree(node) > 0:  # 有出边的节点可能是供应商
                customer_count = len(set(
                    target for _, target in self.graph.out_edges(node)
                    if self.graph.edges[_, target]['relationship_type'] == 'supplier'
                ))
                if customer_count > 1:  # 如果供应商有多个客户
                    supplier_customer_counts[node] = customer_count
        
        # 更新节点属性
        for node in self.graph.nodes():
            is_shared = node in supplier_customer_counts
            self.graph.nodes[node]['is_shared_supplier'] = is_shared
            if is_shared:
                self.graph.nodes[node]['shared_degree'] = supplier_customer_counts[node]
        
        logger.info(f"\n共享供应商数量: {len(supplier_customer_counts)}")
    
    def visualize_network(self, output_path: str = 'data/processed/network_visualization.html'):
        """使用Plotly可视化网络，添加交互功能和性能优化"""
        # 准备节点位置
        pos = nx.spring_layout(self.graph, k=1, iterations=50)
        
        # 准备节点轨迹
        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers+text',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                size=[],
                color=[],
                colorbar=dict(
                    thickness=15,
                    title='共享供应商度',
                    xanchor='left',
                    titleside='right'
                ),
                line=dict(width=2, color='#666')
            ),
            customdata=[],  # 用于存储节点详细信息
            hovertemplate=(
                "<b>%{text}</b><br>" +
                "共享供应商度: %{marker.color}<br>" +
                "节点类型: %{customdata[0]}<br>" +
                "行业: %{customdata[1]}<br>" +
                "地区: %{customdata[2]}<br>" +
                "<extra></extra>"  # 移除次要信息
            )
        )
        
        # 添加节点
        for node in self.graph.nodes():
            x, y = pos[node]
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_trace['text'] += tuple([self.graph.nodes[node]['canonical_name']])
            
            # 设置节点大小和颜色
            if self.graph.nodes[node].get('is_shared_supplier', False):
                size = 20 + self.graph.nodes[node].get('shared_degree', 0) * 5
                color = self.graph.nodes[node].get('shared_degree', 0)
            else:
                size = 10
                color = 0
            
            # 添加节点详细信息
            node_type = '上市公司' if self.graph.nodes[node].get('is_listed', 0) == 1 else '供应商/客户'
            industry = self.graph.nodes[node].get('industry', '未知')
            area = self.graph.nodes[node].get('area', '未知')
            
            node_trace['marker']['size'] += tuple([size])
            node_trace['marker']['color'] += tuple([color])
            node_trace['customdata'] += tuple([[node_type, industry, area]])
        
        # 准备边轨迹
        edge_traces = []
        for edge_type, color in [('supplier', '#ff7f0e'), ('customer', '#1f77b4')]:
            edge_trace = go.Scatter(
                x=[],
                y=[],
                line=dict(width=0.5, color=color),
                hoverinfo='text',
                mode='lines',
                name=edge_type,
                customdata=[],  # 用于存储边详细信息
                hovertemplate=(
                    "<b>%{customdata[0]}</b> → <b>%{customdata[1]}</b><br>" +
                    "关系类型: %{customdata[2]}<br>" +
                    "金额: %{customdata[3]:,.2f}<br>" +
                    "占比: %{customdata[4]:.2%}<br>" +
                    "公告日期: %{customdata[5]}<br>" +
                    "<extra></extra>"
                )
            )
            
            for edge in self.graph.edges():
                if self.graph.edges[edge]['relationship_type'] == edge_type:
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]
                    edge_trace['x'] += tuple([x0, x1, None])
                    edge_trace['y'] += tuple([y0, y1, None])
                    
                    # 添加边详细信息
                    source_name = self.graph.nodes[edge[0]]['canonical_name']
                    target_name = self.graph.nodes[edge[1]]['canonical_name']
                    amount = self.graph.edges[edge].get('procurement_amount', 0) or self.graph.edges[edge].get('revenue', 0)
                    share = self.graph.edges[edge].get('procurement_share', 0) or self.graph.edges[edge].get('revenue_share', 0)
                    date = self.graph.edges[edge].get('announcement_date', '未知')
                    
                    edge_trace['customdata'] += tuple([[source_name, target_name, edge_type, amount, share, date]])
            
            edge_traces.append(edge_trace)
        
        # 创建图形
        fig = go.Figure(
            data=edge_traces + [node_trace],
            layout=go.Layout(
                title=dict(
                    text='供应链网络可视化',
                    x=0.5,
                    y=0.95,
                    xanchor='center',
                    yanchor='top'
                ),
                showlegend=True,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='white',
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ),
                annotations=[
                    dict(
                        text="提示：<br>1. 节点大小表示共享供应商度<br>2. 节点颜色深浅表示共享供应商度<br>3. 橙色边表示供应商关系<br>4. 蓝色边表示客户关系",
                        showarrow=False,
                        xref="paper",
                        yref="paper",
                        x=0.01,
                        y=0.01,
                        align="left",
                        bgcolor="rgba(255, 255, 255, 0.8)",
                        bordercolor="black",
                        borderwidth=1
                    )
                ]
            )
        )
        
        # 添加交互功能
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    x=0.7,
                    y=1.1,
                    showactive=True,
                    buttons=list([
                        dict(
                            args=[{"visible": [True, True, True]}],
                            label="显示全部",
                            method="update"
                        ),
                        dict(
                            args=[{"visible": [True, False, True]}],
                            label="仅显示供应商关系",
                            method="update"
                        ),
                        dict(
                            args=[{"visible": [False, True, True]}],
                            label="仅显示客户关系",
                            method="update"
                        )
                    ])
                )
            ]
        )
        
        # 保存为HTML文件
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(output_path, include_plotlyjs='cdn')
        logger.info(f"\n网络可视化已保存到: {output_path}")
    
    def export_to_gexf(self, output_path: str = 'data/processed/supply_chain_network.gexf'):
        """导出网络到GEXF格式"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        nx.write_gexf(self.graph, output_path)
        logger.info(f"\n网络已导出到: {output_path}")

def main():
    """主函数"""
    try:
        # 创建网络分析器
        network = SupplyChainNetwork()
        
        # 构建或加载网络
        network.build_or_load_network(force_rebuild=False)
        
        # 可视化网络
        network.visualize_network()
        
    except Exception as e:
        logger.error(f"处理过程中出错: {str(e)}")
        raise

if __name__ == "__main__":
    main() 