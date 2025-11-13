from typing import List, Dict
from config import Config

UserArango = None

from arango import ArangoClient


class ArangoManager:
    """Manage ArangoDB operations for GTM results"""

    def __init__(self):
        # if UserArango is not None:
        #     self.client = UserArango(
        #         host=Config.ARANGO_HOST,
        #         username=Config.ARANGO_USERNAME,
        #         password=Config.ARANGO_PASSWORD,
        #         dbname=Config.ARANGO_DB,
        #     )
        #     # Try to get database from user's class
        #     self.db = getattr(self.client, 'db', None)
        #     if self.db is None:
        #         raise RuntimeError("User Arango class did not expose a 'db' attribute")
        # else:
        #     # Fallback to direct python-arango client

        root = ArangoClient(hosts=Config.ARANGO_HOST)
        self.db = root.db(
            Config.ARANGO_DB,
            username=Config.ARANGO_USERNAME,
            password=Config.ARANGO_PASSWORD,
        )

        self.collection_name = Config.ARANGO_COLLECTION
        self._ensure_collection()

    def _ensure_collection(self):
        if not self.db.has_collection(self.collection_name):
            self.db.create_collection(self.collection_name)
        self.col = self.db.collection(self.collection_name)

    def add_results(self, results: List[Dict]):
        """Insert results into ArangoDB collection"""
        if not results:
            return
        docs = []
        for result in results:
            post = result.get('post_data', {})
            sentiment = result.get('sentiment', {})
            classification = result.get('classification', {})
            engagement = result.get('engagement', {})
            doc = {
                'post_id': post.get('post_id'),
                'post_link': post.get('link'),
                'post_title': post.get('title'),
                'post_summary': result.get('summary', ''),
                'author': post.get('author'),
                'subreddit': post.get('subreddit'),
                'timestamp': post.get('timestamp'),
                'relevance_score': classification.get('relevance_score', 0.0),
                'is_relevant': classification.get('is_relevant', False),
                'intent': classification.get('intent', ''),
                'intent_score': classification.get('intent_score', 0.0),
                'sentiment': sentiment.get('sentiment', ''),
                'sentiment_score': sentiment.get('sentiment_level', 0.0),
                'ai_reasoning': classification.get('reasoning', ''),
                'engagement_comment': engagement.get('comment_draft', ''),
                'engagement_dm': engagement.get('dm_draft', ''),
                'engagement_strategy': engagement.get('strategy', ''),
                'priority': engagement.get('priority', ''),
            }
            # Use post_id as _key for dedupe safety
            if doc['post_id']:
                doc['_key'] = doc['post_id']
            docs.append(doc)

        try:
            self.col.import_bulk(docs, on_duplicate='update')
            print(f"Inserted/updated {len(docs)} docs into Arango collection '{self.collection_name}'")
        except Exception as e:
            print(f"Error inserting into Arango: {str(e)}")

    def get_existing_post_ids(self, limit: int = 5000) -> set:
        """Return set of existing post_ids from the collection"""
        try:
            cursor = self.db.aql.execute(
                f"""
                FOR d IN {self.collection_name}
                  LIMIT @limit
                  RETURN d.post_id
                """,
                bind_vars={'limit': limit}
            )
            return set([pid for pid in cursor if pid])
        except Exception as e:
            print(f"Error reading existing post ids from Arango: {str(e)}")
            return set()

    def get_existing_posts(self, limit: int = 5000) -> list:
        """Return set of existing post_ids from the collection"""
        try:
            cursor = self.db.aql.execute(
                f"""
                FOR d IN {self.collection_name}
                  LIMIT @limit
                  RETURN d
                """,
                bind_vars={'limit': limit}
            )
            return list(cursor)
        except Exception as e:
            print(f"Error reading existing post ids from Arango: {str(e)}")
            return set()



    def add_feedback(self, post_id: str, success: bool, notes: str = ""):
        """Store engagement feedback outcome"""
        feedback_col = f"{self.collection_name}_feedback"
        if not self.db.has_collection(feedback_col):
            self.db.create_collection(feedback_col)
        col = self.db.collection(feedback_col)
        try:
            col.insert({'post_id': post_id, 'success': success, 'notes': notes, 'ts': None})
        except Exception as e:
            print(f"Error writing feedback: {str(e)}")

    # def weekly_trends(self, weeks: int = 4):
    #     """Return weekly counts and average scores by intent and sentiment"""
    #     query = f"""
    #     LET weeks = @weeks
    #     FOR d IN {self.collection_name}
    #       COLLECT week = DATE_ISO_WEEK(DATE_TIMESTAMP(d.timestamp)) INTO g
    #       LET cnt = LENGTH(g)
    #       LET avgRel = AVERAGE(g[*].d.relevance_score)
    #       LET intents = MERGE(
    #         FOR x IN g RETURN {[x.d.intent]: 1}
    #       )
    #       LET sentiments = MERGE(
    #         FOR x IN g RETURN {[x.d.sentiment]: 1}
    #       )
    #       RETURN { week, count: cnt, avgRelevance: avgRel, intents, sentiments }
    #     """
    #     try:
    #         return list(self.db.aql.execute(query, bind_vars={'weeks': weeks}))
    #     except Exception as e:
    #         print(f"Error computing trends: {str(e)}")
    #         return []
    def insert_weekly_trends(self,doc):
        self.collection_name_week="gmt_weekly_analysis"
        self.coll = self.db.collection(self.collection_name_week)
        try:
            self.coll.insert(doc)
            cursor = self.db.aql.execute(
                f"""
            FOR doc IN {self.collection_name_week}
                SORT doc.timestamp DESC
                LIMIT 1
                RETURN doc
            """,
                bind_vars={}
            )

            print(f"Inserted/updated {len(doc)} docs into Arango collection '{self.collection_name}'")
            return list(cursor)
        except Exception as e:
            print(f"Error inserting into Arango: {str(e)}")
            return e