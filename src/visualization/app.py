import dash
from dash import dcc, html, dash_table, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import duckdb
import pandas as pd
from pathlib import Path
import json
import atexit

# 初始化 Dash 应用
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
server = app.server

# 数据库路径
DB_PATH = Path("data/processed/supply_chain_network.duckdb")

def get_conn():
    return duckdb.connect(str(DB_PATH), read_only=True)

# 创建初始 Cytoscape 组件
initial_elements = []
initial_cyto = cyto.Cytoscape(
    id="network-graph",
    layout={"name": "cose"},
    style={"width": "100%", "height": "600px"},
    elements=initial_elements,
    stylesheet=[
        {
            "selector": "node",
            "style": {
                "label": "data(label)",
                "background-color": "#BEE",
                "text-valign": "center",
                "text-halign": "center",
                "font-size": "12px",
                "text-wrap": "wrap",
                "text-max-width": "80px"
            }
        },
        {
            "selector": "edge",
            "style": {
                "width": 1,
                "line-color": "#ccc",
                "font-size": "12px"
            }
        },
        {
            "selector": "node:selected",
            "style": {
                "background-color": "#FF0000",
                "border-width": 2,
                "border-color": "#000"
            }
        }
    ],
    responsive=True,
    userZoomingEnabled=True,
    userPanningEnabled=True,
    boxSelectionEnabled=True,
    autoungrabify=False,
    autolock=False,
    autounselectify=False,
    minZoom=0.1,
    maxZoom=2
)

# 修改布局，添加筛选和切换按钮
app.layout = dbc.Container([
    html.H1("供应链网络可视化", className="text-center my-4"),
    
    # 筛选区域
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("数据筛选"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("共享供应商筛选："),
                            dbc.RadioItems(
                                id="supplier-filter",
                                options=[
                                    {"label": "全部", "value": "all"},
                                    {"label": "仅共享供应商", "value": "shared"},
                                    {"label": "仅非共享供应商", "value": "non-shared"}
                                ],
                                value="all",
                                inline=True
                            )
                        ], width=12)
                    ])
                ])
            ], className="mb-4")
        ])
    ]),
    
    # 视图切换和回退按钮
    dbc.Row([
        dbc.Col([
            dbc.RadioItems(
                id="view-selector",
                options=[
                    {"label": "表格视图", "value": "table"},
                    {"label": "图形视图", "value": "graph"}
                ],
                value="table",
                inline=True,
                className="mb-4"
            )
        ], width=8),
        dbc.Col([
            dbc.Button(
                "返回列表",
                id="back-button",
                color="secondary",
                className="mb-4",
                style={"display": "none"}
            )
        ], width=4)
    ]),
    
    # 主视图区域
    html.Div([
        # 表格视图
        dcc.Loading(
            id="loading-table",
            type="circle",
            children=html.Div(id="table-view", style={"display": "block"})
        ),
        # 图形视图
        html.Div(id="graph-view", style={"display": "none"}, children=[initial_cyto])
    ], id="main-view"),
    
    # 公司详情和关系区域
    dbc.Row([
        # 左侧：公司详情
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("公司详情"),
                dbc.CardBody(
                    dcc.Loading(
                        id="loading-details",
                        type="circle",
                        children=html.Div(id="company-details")
                    )
                )
            ], className="mb-4")
        ], width=6),
        
        # 右侧：公司关系
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.Div([
                        html.Span("公司关系", className="me-3"),
                        dbc.ButtonGroup([
                            dbc.Button("全部", id="all-relations-btn", color="primary", className="me-2"),
                            dbc.Button("入向", id="incoming-relations-btn", color="secondary", className="me-2"),
                            dbc.Button("出向", id="outgoing-relations-btn", color="secondary")
                        ], className="float-end")
                    ], className="d-flex justify-content-between align-items-center")
                ]),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-relationships",
                        type="circle",
                        children=[
                            # 关系图
                            cyto.Cytoscape(
                                id="company-relationships-graph",
                                layout={"name": "cose"},
                                style={"width": "100%", "height": "400px"},
                                elements=[],
                                stylesheet=[
                                    {
                                        "selector": "node",
                                        "style": {
                                            "label": "data(label)",
                                            "background-color": "#BEE",
                                            "text-valign": "center",
                                            "text-halign": "center",
                                            "width": "data(size)",
                                            "height": "data(size)",
                                            "font-size": "12px",
                                            "text-wrap": "wrap",
                                            "text-max-width": "80px"
                                        }
                                    },
                                    {
                                        "selector": "edge",
                                        "style": {
                                            "width": 1,
                                            "line-color": "#ccc",
                                            "label": "data(label)",
                                            "font-size": "12px"
                                        }
                                    },
                                    {
                                        "selector": "node:selected",
                                        "style": {
                                            "background-color": "#FF0000",
                                            "border-width": 2,
                                            "border-color": "#000"
                                        }
                                    }
                                ],
                                responsive=True,
                                userZoomingEnabled=True,
                                userPanningEnabled=True,
                                boxSelectionEnabled=True,
                                autoungrabify=False,
                                autolock=False,
                                autounselectify=False,
                                minZoom=0.1,
                                maxZoom=2
                            ),
                            # 关系数据表
                            html.Div(id="company-relationships-table", className="mt-4")
                        ]
                    )
                ])
            ])
        ], width=6)
    ]),
    
    # 存储组件
    dcc.Store(id="selected-node-store"),
    dcc.Store(id="graph-elements-store"),
    dcc.Store(id="relation-direction-store", data="all")
], fluid=True)

# 添加关系方向切换回调
@app.callback(
    [Output("all-relations-btn", "color"),
     Output("incoming-relations-btn", "color"),
     Output("outgoing-relations-btn", "color"),
     Output("relation-direction-store", "data")],
    [Input("all-relations-btn", "n_clicks"),
     Input("incoming-relations-btn", "n_clicks"),
     Input("outgoing-relations-btn", "n_clicks")],
    prevent_initial_call=True
)
def update_relation_direction(all_clicks, incoming_clicks, outgoing_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "primary", "secondary", "secondary", "all"
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "all-relations-btn":
        return "primary", "secondary", "secondary", "all"
    elif button_id == "incoming-relations-btn":
        return "secondary", "primary", "secondary", "incoming"
    else:
        return "secondary", "secondary", "primary", "outgoing"

# 修改视图切换回调，修复共享供应商筛选
@app.callback(
    [Output("table-view", "style"),
     Output("graph-view", "style"),
     Output("table-view", "children"),
     Output("network-graph", "elements")],
    [Input("view-selector", "value"),
     Input("selected-node-store", "data"),
     Input("supplier-filter", "value")],
    [State("network-graph", "elements")]
)
def update_view(view_type, selected_node, supplier_filter, current_elements):
    print(f"视图切换回调触发，view_type: {view_type}, selected_node: {selected_node}, supplier_filter: {supplier_filter}")
    
    # 构建共享供应商筛选条件
    supplier_condition = ""
    if supplier_filter == "shared":
        supplier_condition = """
        AND (
            (s.is_shared_supplier = true AND e.source_node_id = s.unique_node_id) OR
            (t.is_shared_supplier = true AND e.target_node_id = t.unique_node_id)
        )
        """
    elif supplier_filter == "non-shared":
        supplier_condition = """
        AND (
            (s.is_shared_supplier = false OR s.is_shared_supplier IS NULL) AND
            (t.is_shared_supplier = false OR t.is_shared_supplier IS NULL)
        )
        """
    
    # 获取表格数据
    if selected_node:
        query = f"""
        WITH company_relationships AS (
            -- 出向关系
            SELECT 
                s.canonical_name AS source_name,
                t.canonical_name AS target_name,
                e.source_node_id,
                e.target_node_id,
                e.relationship_type,
                e.procurement_amount,
                e.revenue,
                s.is_shared_supplier as source_is_shared,
                t.is_shared_supplier as target_is_shared
            FROM edges e
            JOIN nodes s ON e.source_node_id = s.unique_node_id
            JOIN nodes t ON e.target_node_id = t.unique_node_id
            WHERE e.source_node_id = '{selected_node}'
            UNION ALL
            -- 入向关系
            SELECT 
                s.canonical_name AS source_name,
                t.canonical_name AS target_name,
                e.source_node_id,
                e.target_node_id,
                e.relationship_type,
                e.procurement_amount,
                e.revenue,
                s.is_shared_supplier as source_is_shared,
                t.is_shared_supplier as target_is_shared
            FROM edges e
            JOIN nodes s ON e.source_node_id = s.unique_node_id
            JOIN nodes t ON e.target_node_id = t.unique_node_id
            WHERE e.target_node_id = '{selected_node}'
        )
        SELECT *
        FROM company_relationships
        WHERE 1=1 {supplier_condition}
        ORDER BY source_name, target_name
        """
    else:
        query = f"""
        SELECT 
            s.canonical_name AS source_name,
            t.canonical_name AS target_name,
            e.source_node_id,
            e.target_node_id,
            e.relationship_type,
            e.procurement_amount,
            e.revenue,
            s.is_shared_supplier as source_is_shared,
            t.is_shared_supplier as target_is_shared
        FROM edges e
        JOIN nodes s ON e.source_node_id = s.unique_node_id
        JOIN nodes t ON e.target_node_id = t.unique_node_id
        WHERE 1=1 {supplier_condition}
        ORDER BY source_name, target_name
        """
    
    try:
        with get_conn() as conn:
            df = conn.execute(query).df()
            print("表格数据查询结果：")
            print(f"数据框形状: {df.shape}")
            print("数据框列名:", df.columns.tolist())
            print("数据框前5行:", df.head())
    except Exception as e:
        print(f"表格数据查询错误: {e}")
        df = pd.DataFrame()
    
    # 格式化数值
    for col in ['procurement_amount', 'revenue']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) and x != 0 else "0")
    
    # 添加共享供应商标记列
    if 'source_is_shared' in df.columns and 'target_is_shared' in df.columns:
        df['is_shared'] = df.apply(
            lambda row: '是' if row['source_is_shared'] or row['target_is_shared'] else '否',
            axis=1
        )
    
    table = dash_table.DataTable(
        id="relationships-table",
        columns=[
            {"name": "源公司", "id": "source_name"},
            {"name": "目标公司", "id": "target_name"},
            {"name": "关系类型", "id": "relationship_type"},
            {"name": "采购金额", "id": "procurement_amount"},
            {"name": "收入", "id": "revenue"},
            {"name": "是否共享供应商", "id": "is_shared"}
        ],
        data=df.to_dict("records"),
        page_size=20,
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "10px",
            "whiteSpace": "normal",
            "height": "auto"
        },
        style_header={
            "backgroundColor": "rgb(230, 230, 230)",
            "fontWeight": "bold"
        }
    )
    
    # 获取图形数据
    if view_type == "graph":
        if current_elements and len(current_elements) > 0:
            print("使用当前图形元素")
            elements = current_elements
        else:
            print("重新查询图形数据")
            graph_query = f"""
            WITH initial_nodes AS (
                SELECT DISTINCT n.unique_node_id, n.canonical_name
                FROM nodes n
                JOIN edges e ON n.unique_node_id IN (e.source_node_id, e.target_node_id)
                JOIN nodes s ON e.source_node_id = s.unique_node_id
                JOIN nodes t ON e.target_node_id = t.unique_node_id
                WHERE 1=1 {supplier_condition}
            ),
            node_edges AS (
                SELECT DISTINCT
                    n.unique_node_id,
                    n.canonical_name,
                    e.source_node_id,
                    e.target_node_id,
                    e.procurement_amount,
                    e.revenue
                FROM initial_nodes n
                JOIN edges e ON n.unique_node_id IN (e.source_node_id, e.target_node_id)
                JOIN nodes s ON e.source_node_id = s.unique_node_id
                JOIN nodes t ON e.target_node_id = t.unique_node_id
                WHERE 1=1 {supplier_condition}
            )
            SELECT 
                ne.unique_node_id,
                ne.canonical_name,
                ne.source_node_id,
                ne.target_node_id,
                t.canonical_name as target_name,
                ne.procurement_amount,
                ne.revenue
            FROM node_edges ne
            JOIN nodes t ON ne.target_node_id = t.unique_node_id
            """
            try:
                with get_conn() as conn:
                    graph_df = conn.execute(graph_query).df()
                    print("图形数据查询结果：")
                    print(f"数据框形状: {graph_df.shape}")
                    print("数据框列名:", graph_df.columns.tolist())
                    print("数据框前5行:", graph_df.head())
                    
                    # 构建 Cytoscape 元素
                    elements = []
                    nodes = set()
                    
                    # 计算节点大小范围
                    max_amount = max(
                        graph_df['procurement_amount'].max() if 'procurement_amount' in graph_df.columns else 0,
                        graph_df['revenue'].max() if 'revenue' in graph_df.columns else 0
                    )
                    min_size = 20
                    max_size = 100
                    
                    # 先添加所有节点
                    for _, row in graph_df.iterrows():
                        if pd.notna(row["unique_node_id"]) and row["unique_node_id"] not in nodes:
                            # 计算节点大小
                            amount = max(
                                row['procurement_amount'] if pd.notna(row['procurement_amount']) else 0,
                                row['revenue'] if pd.notna(row['revenue']) else 0
                            )
                            size = min_size + (max_size - min_size) * (amount / max_amount) if max_amount > 0 else min_size
                            
                            elements.append({
                                "data": {
                                    "id": row["unique_node_id"],
                                    "label": row["canonical_name"],
                                    "size": size
                                }
                            })
                            nodes.add(row["unique_node_id"])
                        
                        if pd.notna(row["target_node_id"]) and row["target_node_id"] not in nodes:
                            # 计算目标节点大小
                            amount = max(
                                row['procurement_amount'] if pd.notna(row['procurement_amount']) else 0,
                                row['revenue'] if pd.notna(row['revenue']) else 0
                            )
                            size = min_size + (max_size - min_size) * (amount / max_amount) if max_amount > 0 else min_size
                            
                            elements.append({
                                "data": {
                                    "id": row["target_node_id"],
                                    "label": row["target_name"],
                                    "size": size
                                }
                            })
                            nodes.add(row["target_node_id"])
                    
                    # 再添加边
                    for _, row in graph_df.iterrows():
                        if (pd.notna(row["source_node_id"]) and 
                            pd.notna(row["target_node_id"]) and 
                            row["source_node_id"] in nodes and 
                            row["target_node_id"] in nodes):
                            elements.append({
                                "data": {
                                    "source": row["source_node_id"],
                                    "target": row["target_node_id"]
                                }
                            })
                    
                    print(f"构建的图形元素数量: {len(elements)}")
                    print(f"节点数量: {len(nodes)}")
            except Exception as e:
                print(f"图形数据查询错误: {e}")
                elements = []
    else:
        elements = []
    
    # 根据视图类型返回不同的显示样式
    if view_type == "table":
        return {"display": "block"}, {"display": "none"}, table, elements
    else:
        return {"display": "none"}, {"display": "block"}, table, elements

# 修改数据库连接检查函数
def check_db_connection():
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"数据库连接检查失败: {e}")
        return False

# 公司详情回调
@app.callback(
    Output("company-details", "children"),
    Input("selected-node-store", "data")
)
def update_company_details(selected_node):
    if not selected_node:
        return "请选择一个公司查看详情"
    if not check_db_connection():
        return "数据库连接异常，请刷新页面重试"
    print(f"查询公司详情，node_id: {selected_node}")
    try:
        with get_conn() as conn:
            # 查询 nodes 表
            query = f"""
            SELECT 
                unique_node_id,
                canonical_name,
                company_id,
                company_class,
                is_listed,
                stock_code,
                industry,
                area,
                registered_capital,
                is_shared_supplier,
                shared_degree
            FROM nodes
            WHERE unique_node_id = '{selected_node}'
            """
            df = conn.execute(query).df()
            print("公司详情查询结果：", df)
            column_names = {
                'canonical_name': '公司名称',
                'company_id': '公司编号',
                'company_class': '公司分类',
                'is_listed': '是否上市',
                'stock_code': '股票代码',
                'industry': '所属行业',
                'area': '所属地区',
                'registered_capital': '注册资本',
                'is_shared_supplier': '是否共享供应商',
                'shared_degree': '共享度'
            }
            details = []
            if df.empty:
                print(f"nodes表未找到该公司({selected_node})，尝试从edges表查找...")
                name_query = f"""
                SELECT DISTINCT 
                    CASE 
                        WHEN source_node_id = '{selected_node}' THEN source_name
                        WHEN target_node_id = '{selected_node}' THEN target_name
                    END as company_name
                FROM (
                    SELECT 
                        s.canonical_name as source_name,
                        t.canonical_name as target_name,
                        e.source_node_id,
                        e.target_node_id
                    FROM edges e
                    JOIN nodes s ON e.source_node_id = s.unique_node_id
                    JOIN nodes t ON e.target_node_id = t.unique_node_id
                    WHERE e.source_node_id = '{selected_node}' OR e.target_node_id = '{selected_node}'
                )
                WHERE company_name IS NOT NULL
                LIMIT 1
                """
                name_df = conn.execute(name_query).df()
                company_name = name_df.iloc[0]['company_name'] if not name_df.empty else "未知公司"
                print(f"edges表查到公司名称: {company_name if company_name else '无'}")
                details.append({"属性": "公司名称", "值": company_name})
                for col, display_name in column_names.items():
                    if col != 'canonical_name':
                        details.append({"属性": display_name, "值": "无"})
            else:
                node_name = df.iloc[0]['canonical_name']
                name_query = f"""
                SELECT DISTINCT 
                    CASE 
                        WHEN source_node_id = '{selected_node}' THEN source_name
                        WHEN target_node_id = '{selected_node}' THEN target_name
                    END as company_name
                FROM (
                    SELECT 
                        s.canonical_name as source_name,
                        t.canonical_name as target_name,
                        e.source_node_id,
                        e.target_node_id
                    FROM edges e
                    JOIN nodes s ON e.source_node_id = s.unique_node_id
                    JOIN nodes t ON e.target_node_id = t.unique_node_id
                    WHERE e.source_node_id = '{selected_node}' OR e.target_node_id = '{selected_node}'
                )
                WHERE company_name IS NOT NULL
                LIMIT 1
                """
                name_df = conn.execute(name_query).df()
                edge_name = name_df.iloc[0]['company_name'] if not name_df.empty else None
                if edge_name and edge_name != node_name:
                    print(f"警告：nodes表与edges表公司名称不一致！nodes: {node_name}, edges: {edge_name}")
                for col in df.columns:
                    if col != "unique_node_id":
                        value = df.iloc[0][col]
                        if pd.isna(value):
                            value = "无"
                        elif isinstance(value, bool):
                            value = "是" if value else "否"
                        elif isinstance(value, (int, float)):
                            value = f"{value:,.2f}" if value != 0 else "0"
                        details.append({
                            "属性": column_names.get(col, col),
                            "值": str(value)
                        })
            return dash_table.DataTable(
                columns=[{"name": "属性", "id": "属性"}, {"name": "值", "id": "值"}],
                data=details,
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left", "padding": "10px", "whiteSpace": "normal", "height": "auto"}
            )
    except Exception as e:
        print(f"查询公司详情时发生错误: {e}")
        return f"查询出错: {str(e)}"

# 添加回退按钮回调
@app.callback(
    Output("back-button", "style"),
    Input("selected-node-store", "data")
)
def toggle_back_button(selected_node):
    if selected_node:
        return {"display": "block"}
    return {"display": "none"}

# 回退按钮点击回调
@app.callback(
    Output("selected-node-store", "data", allow_duplicate=True),
    Input("back-button", "n_clicks"),
    prevent_initial_call=True
)
def clear_selected_node(n_clicks):
    if n_clicks:
        return None
    return None

# 修改公司关系回调，添加入向/出向筛选
@app.callback(
    [Output("company-relationships-table", "children"),
     Output("company-relationships-graph", "elements")],
    [Input("selected-node-store", "data"),
     Input("relation-direction-store", "data")]
)
def update_company_relationships(selected_node, relation_direction):
    if not selected_node:
        return "请选择一个公司查看关系", []
    if not check_db_connection():
        return "数据库连接异常，请刷新页面重试", []
    print(f"查询公司关系，node_id: {selected_node}, direction: {relation_direction}")
    try:
        with get_conn() as conn:
            # 构建方向筛选条件
            direction_condition = ""
            if relation_direction == "incoming":
                direction_condition = "AND direction = '入向'"
            elif relation_direction == "outgoing":
                direction_condition = "AND direction = '出向'"
            
            query = f"""
            WITH company_relationships AS (
                -- 出向关系
                SELECT 
                    '出向' AS direction,
                    t.canonical_name AS connected_company,
                    e.relationship_type,
                    e.procurement_amount,
                    e.revenue,
                    t.unique_node_id as connected_node_id
                FROM edges e
                JOIN nodes t ON e.target_node_id = t.unique_node_id
                WHERE e.source_node_id = '{selected_node}'
                UNION ALL
                -- 入向关系
                SELECT 
                    '入向' AS direction,
                    s.canonical_name AS connected_company,
                    e.relationship_type,
                    e.procurement_amount,
                    e.revenue,
                    s.unique_node_id as connected_node_id
                FROM edges e
                JOIN nodes s ON e.source_node_id = s.unique_node_id
                WHERE e.target_node_id = '{selected_node}'
            )
            SELECT *
            FROM company_relationships
            WHERE 1=1 {direction_condition}
            ORDER BY direction, connected_company
            """
            df = conn.execute(query).df()
            print("公司关系查询结果：", df)
            
            if df.empty:
                print(f"未找到公司关系，direction: {relation_direction}")
                return "未找到公司关系", []
            
            # 构建关系图元素
            elements = []
            nodes = set()
            
            # 计算节点大小范围
            max_amount = max(
                df['procurement_amount'].max() if 'procurement_amount' in df.columns else 0,
                df['revenue'].max() if 'revenue' in df.columns else 0
            )
            min_size = 20
            max_size = 100
            
            # 添加中心节点
            center_node_query = f"SELECT canonical_name FROM nodes WHERE unique_node_id = '{selected_node}'"
            center_name = conn.execute(center_node_query).fetchone()
            center_name = center_name[0] if center_name else selected_node
            elements.append({
                "data": {
                    "id": selected_node,
                    "label": center_name,
                    "size": max_size  # 中心节点使用最大尺寸
                }
            })
            nodes.add(selected_node)
            
            # 添加关联节点和边
            for _, row in df.iterrows():
                if row['connected_node_id'] not in nodes:
                    # 计算节点大小
                    amount = max(
                        row['procurement_amount'] if pd.notna(row['procurement_amount']) else 0,
                        row['revenue'] if pd.notna(row['revenue']) else 0
                    )
                    size = min_size + (max_size - min_size) * (amount / max_amount) if max_amount > 0 else min_size
                    
                    elements.append({
                        "data": {
                            "id": row['connected_node_id'],
                            "label": row['connected_company'],
                            "size": size
                        }
                    })
                    nodes.add(row['connected_node_id'])
                
                # 添加边
                elements.append({
                    "data": {
                        "source": selected_node if row['direction'] == '出向' else row['connected_node_id'],
                        "target": row['connected_node_id'] if row['direction'] == '出向' else selected_node,
                        "label": row['relationship_type']
                    }
                })
            
            # 格式化数值
            for col in ['procurement_amount', 'revenue']:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) and x != 0 else "0")
            
            # 创建关系数据表
            table = dash_table.DataTable(
                columns=[
                    {"name": "方向", "id": "direction"},
                    {"name": "关联公司", "id": "connected_company"},
                    {"name": "关系类型", "id": "relationship_type"},
                    {"name": "采购金额", "id": "procurement_amount"},
                    {"name": "收入", "id": "revenue"}
                ],
                data=df.to_dict("records"),
                page_size=10,
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "left",
                    "padding": "10px",
                    "whiteSpace": "normal",
                    "height": "auto"
                }
            )
            
            return table, elements
    except Exception as e:
        print(f"查询公司关系时发生错误: {e}")
        return f"查询出错: {str(e)}", []

# 表格点击回调
@app.callback(
    Output("selected-node-store", "data"),
    Input("relationships-table", "active_cell"),
    Input("relationships-table", "data")
)
def update_selected_node_from_table(active_cell, data):
    if not active_cell:
        return None
    
    row = data[active_cell["row"]]
    if active_cell["column_id"] == "source_name":
        return row["source_node_id"]
    elif active_cell["column_id"] == "target_name":
        return row["target_node_id"]
    return None

# 图形点击回调
@app.callback(
    Output("selected-node-store", "data", allow_duplicate=True),
    Input("network-graph", "tapNodeData"),
    prevent_initial_call=True
)
def update_selected_node_from_graph(node_data):
    if not node_data:
        return None
    print(f"节点点击事件触发，节点数据: {node_data}")
    return node_data["id"]

if __name__ == "__main__":
    app.run(debug=True) 