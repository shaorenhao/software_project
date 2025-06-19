from py2neo import Graph, Node, Relationship
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv()

class KnowledgeGraph:
    def __init__(self):
        try:
            self.graph = Graph(
                os.getenv("NEO4J_URI"),
                auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
            )
            self._initialize_schema()
            print("✅ 成功连接到Neo4j Aura知识图谱")
        except Exception as e:
            print(f"❌ 知识图谱连接失败: {str(e)}")
            raise

    def _initialize_schema(self):
        """初始化图数据库约束和索引"""
        self.graph.run("""
        CREATE CONSTRAINT unique_concept_name IF NOT EXISTS 
        FOR (c:Concept) REQUIRE c.name IS UNIQUE
        """)
        
        self.graph.run("""
        CREATE INDEX concept_type_index IF NOT EXISTS 
        FOR (c:Concept) ON (c.type)
        """)

    def add_concept(self, name: str, concept_type: str, properties: Dict = None) -> Node:
        """添加或更新概念节点"""
        properties = properties or {}
        properties.update({"type": concept_type})
        
        node = Node("Concept", name=name, **properties)
        self.graph.merge(node, "Concept", "name")
        return node

    def add_relation(self, source_name: str, relation_type: str, 
                    target_name: str, properties: Dict = None) -> Relationship:
        """添加概念间关系"""
        properties = properties or {}
        
        query = """
        MATCH (source:Concept {name: $source_name}), (target:Concept {name: $target_name})
        MERGE (source)-[r:%s]->(target)
        SET r += $properties
        RETURN r
        """ % relation_type
        
        self.graph.run(query, 
                      source_name=source_name,
                      target_name=target_name,
                      properties=properties)
        
        return True

    def find_concept(self, name: str) -> Optional[Node]:
        """查找概念节点"""
        return self.graph.nodes.match("Concept", name=name).first()

    def query_related_concepts(self, concept_name: str, 
                             relation_type: str = None, 
                             depth: int = 1) -> List[Dict]:
        """查询相关概念"""
        relation_clause = f":{relation_type}" if relation_type else ""
        query = f"""
        MATCH path=(start:Concept {{name: $name}})-[r{relation_clause}*1..{depth}]->(related:Concept)
        UNWIND relationships(path) AS rel
        RETURN related, collect(rel) AS relations
        """
        
        result = self.graph.run(query, name=concept_name).data()
        
        return [
            {
                "concept": dict(record["related"]),
                "relations": [dict(rel) for rel in record["relations"]]
            }
            for record in result
        ]

    def semantic_search(self, query: str, top_k: int = 3) -> List[Node]:
        """语义搜索概念"""
        query = query.lower()
        result = self.graph.run("""
        MATCH (c:Concept)
        WHERE toLower(c.name) CONTAINS $query OR 
              toLower(c.definition) CONTAINS $query
        RETURN c LIMIT $limit
        """, query=query, limit=top_k)
        
        return [dict(record["c"]) for record in result]

    def visualize_subgraph(self, concept_name: str, depth: int = 2):
        """生成子图的Graphviz DOT格式"""
        query = f"""
        MATCH path=(start:Concept {{name: $name}})-[r*1..{depth}]->(related:Concept)
        RETURN path
        """
        result = self.graph.run(query, name=concept_name)
        
        dot_lines = ['digraph G {', 'rankdir=LR;', 'node [shape=box, style="rounded,filled", fillcolor="#f8f9fa"];']
        nodes = set()
        edges = set()
        
        for record in result:
            path = record["path"]
            for rel in path.relationships:
                start = rel.start_node["name"]
                end = rel.end_node["name"]
                rel_type = type(rel).__name__
                
                # 添加节点
                nodes.add(f'"{start}" [label="{start}\\n({rel.start_node.get("type","")})"]')
                nodes.add(f'"{end}" [label="{end}\\n({rel.end_node.get("type","")})"]')
                
                # 添加边
                edges.add(f'"{start}" -> "{end}" [label="{rel_type}", fontsize=10]')
        
        dot_lines.extend(nodes)
        dot_lines.extend(edges)
        dot_lines.append('}')
        
        return '\n'.join(dot_lines)