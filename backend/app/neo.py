from py2neo import Graph, Node, Relationship
import time

class NeoHandler:
    def __init__(self, uri, user, password):
        self.g = Graph(uri, auth=(user, password))
        try:
            # create uniqueness constraint for Domain (idempotent in recent Neo4j)
            self.g.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Domain) REQUIRE d.name IS UNIQUE")
        except Exception:
            pass

    def insert_email_event(self, email_event: dict):
        # Email node
        e = Node("Email", id=email_event['id'], subject=email_event.get('subject',''), ts=time.time(), risk=email_event.get('risk', 0.0))
        self.g.merge(e, "Email", "id")

        # Sender node
        s = Node("Actor", address=email_event.get('from'), role="sender")
        self.g.merge(s, "Actor", "address")
        self.g.merge(Relationship(s, "SENT", e))

        # Recipients
        for r_addr in email_event.get('to', []):
            r = Node("Actor", address=r_addr, role="recipient")
            self.g.merge(r, "Actor", "address")
            self.g.merge(Relationship(e, "TO", r))

        # URLs & Domains
        for url, domain in email_event.get('url_domain_map', {}).items():
            d = Node("Domain", name=domain)
            self.g.merge(d, "Domain", "name")
            u = Node("URL", url=url)
            self.g.merge(u, "URL", "url")
            self.g.merge(Relationship(e, "CONTAINS_URL", u))
            self.g.merge(Relationship(u, "HOSTED_ON", d))

    def update_domain_info(self, domain: str, data: dict):
        # set properties on Domain node
        self.g.run(
            """
            MERGE (d:Domain {name:$name})
            SET d += $props
            """,
            name=domain, props=data
        )

    def get_top_nodes(self, limit=200):
        q = f"""
        MATCH (n)-[r]->(m)
        RETURN n,r,m LIMIT $limit
        """
        res = self.g.run(q, limit=limit).data()
        nodes = {}
        edges = []
        for row in res:
            n = row['n']
            m = row['m']
            r = row['r']
            for obj in (n, m):
                uid = f"{obj.__class__.__name__}_{obj.identity}"
                if uid not in nodes:
                    props = dict(obj)
                    label = props.get('name') or props.get('address') or props.get('subject') or props.get('url') or str(uid)
                    nodes[uid] = {"id": uid, "label": label, "props": props}
            src = f"{n.__class__.__name__}_{n.identity}"
            tgt = f"{m.__class__.__name__}_{m.identity}"
            edges.append({"source": src, "target": tgt, "label": type(r).__name__})
        return {"nodes": list(nodes.values()), "edges": edges}
