import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import networkx as nx
from pathlib import Path
import logging
from typing import Dict, List, Set, Tuple
import json
from supply_chain_network import SupplyChainNetwork

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 Dash 应用
app = dash.Dash(__name__)
app.title = "供应链网络可视化"

# 加载网络
network = SupplyChainNetwork()
network.build_or_load_network(force_rebuild=False)

# 预计算节点位置
pos = nx.spring_layout(network.graph, k=1, iterations=50)

# 应用布局
app.layout = html.Div([
    html.Div([
        html.H1("供应链网络可视化", style={'textAlign': 'center'}),
        html.Div([
            dcc.Input(
                id='search-input',
                type='text',
                placeholder='搜索公司名称...',
                style={'width': '300px', 'margin': '10px'}
            ),
            html.Button('搜索', id='search-button', n_clicks=0),
            html.Button('重置视图', id='reset-button', n_clicks=0),
        ], style={'textAlign': 'center', 'margin': '10px'}),
        html.Div([
            dcc.Dropdown(
                id='view-type-dropdown',
                options=[
                    {'label': '显示全部', 'value': 'all'},
                    {'label': '仅显示供应商关系', 'value': 'supplier'},
                    {'label': '仅显示客户关系', 'value': 'customer'}
                ],
                value='all',
                style={'width': '200px', 'margin': '10px'}
            ),
        ], style={'textAlign': 'center'}),
    ]),
    
    html.Div([
        dcc.Graph(
            id='network-graph',
            style={'height': '80vh'},
            config={'displayModeBar': True}
        ),
    ]),
    
    html.Div([
        html.Div(id='node-info', style={'margin': '20px'})
    ]),
    
    dcc.Store(id='selected-node'),
    dcc.Store(id='graph-data')
])

def create_network_figure(selected_node: str = None, view_type: str = 'all'):
    """创建网络图形"""
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
        customdata=[],
        hovertemplate=(
            "<b>%{text}</b><br>" +
            "共享供应商度: %{marker.color}<br>" +
            "节点类型: %{customdata[0]}<br>" +
            "行业: %{customdata[1]}<br>" +
            "地区: %{customdata[2]}<br>" +
            "<extra></extra>"
        )
    )
    
    # 添加节点
    for node in network.graph.nodes():
        x, y = pos[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple([network.graph.nodes[node]['canonical_name']])
        
        # 设置节点大小和颜色
        if network.graph.nodes[node].get('is_shared_supplier', False):
            size = 20 + network.graph.nodes[node].get('shared_degree', 0) * 5
            color = network.graph.nodes[node].get('shared_degree', 0)
        else:
            size = 10
            color = 0
        
        # 添加节点详细信息
        node_type = '上市公司' if network.graph.nodes[node].get('is_listed', 0) == 1 else '供应商/客户'
        industry = network.graph.nodes[node].get('industry', '未知')
        area = network.graph.nodes[node].get('area', '未知')
        
        node_trace['marker']['size'] += tuple([size])
        node_trace['marker']['color'] += tuple([color])
        node_trace['customdata'] += tuple([[node_type, industry, area]])
    
    # 准备边轨迹
    edge_traces = []
    for edge_type, color in [('supplier', '#ff7f0e'), ('customer', '#1f77b4')]:
        if view_type != 'all' and view_type != edge_type:
            continue
            
        edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=0.5, color=color),
            hoverinfo='text',
            mode='lines',
            name=edge_type,
            customdata=[],
            hovertemplate=(
                "<b>%{customdata[0]}</b> → <b>%{customdata[1]}</b><br>" +
                "关系类型: %{customdata[2]}<br>" +
                "金额: %{customdata[3]:,.2f}<br>" +
                "占比: %{customdata[4]:.2%}<br>" +
                "公告日期: %{customdata[5]}<br>" +
                "<extra></extra>"
            )
        )
        
        for edge in network.graph.edges():
            if network.graph.edges[edge]['relationship_type'] == edge_type:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_trace['x'] += tuple([x0, x1, None])
                edge_trace['y'] += tuple([y0, y1, None])
                
                # 添加边详细信息
                source_name = network.graph.nodes[edge[0]]['canonical_name']
                target_name = network.graph.nodes[edge[1]]['canonical_name']
                amount = network.graph.edges[edge].get('procurement_amount', 0) or network.graph.edges[edge].get('revenue', 0)
                share = network.graph.edges[edge].get('procurement_share', 0) or network.graph.edges[edge].get('revenue_share', 0)
                date = network.graph.edges[edge].get('announcement_date', '未知')
                
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
    
    return fig

@app.callback(
    [Output('network-graph', 'figure'),
     Output('node-info', 'children')],
    [Input('search-button', 'n_clicks'),
     Input('reset-button', 'n_clicks'),
     Input('view-type-dropdown', 'value')],
    [State('search-input', 'value'),
     State('selected-node', 'data')]
)
def update_graph(search_clicks, reset_clicks, view_type, search_value, selected_node):
    """更新图形"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return create_network_figure(), None
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'search-button' and search_value:
        # 搜索节点
        for node in network.graph.nodes():
            if search_value.lower() in network.graph.nodes[node]['canonical_name'].lower():
                selected_node = node
                break
    
    elif trigger_id == 'reset-button':
        selected_node = None
    
    return create_network_figure(selected_node, view_type), create_node_info(selected_node)

def create_node_info(node_id: str = None):
    """创建节点信息显示"""
    if not node_id:
        return None
    
    node_data = network.graph.nodes[node_id]
    
    return html.Div([
        html.H3(node_data['canonical_name']),
        html.Table([
            html.Tr([html.Td('节点类型'), html.Td('上市公司' if node_data.get('is_listed', 0) == 1 else '供应商/客户')]),
            html.Tr([html.Td('行业'), html.Td(node_data.get('industry', '未知'))]),
            html.Tr([html.Td('地区'), html.Td(node_data.get('area', '未知'))]),
            html.Tr([html.Td('注册资本'), html.Td(f"{node_data.get('registered_capital', 0):,.2f}")]),
            html.Tr([html.Td('是否共享供应商'), html.Td('是' if node_data.get('is_shared_supplier', False) else '否')]),
            html.Tr([html.Td('共享供应商度'), html.Td(node_data.get('shared_degree', 0))]),
        ], style={'width': '100%', 'border': '1px solid black'})
    ])

if __name__ == '__main__':
    app.run_server(debug=True, port=8050) 