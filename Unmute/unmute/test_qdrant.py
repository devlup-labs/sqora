import qdrant_client
import sys
client = qdrant_client.QdrantClient(url="http://localhost:6333")
try:
    results = client.query_points(collection_name="pyqs", query=[0.1]*384, limit=1)
    print(results)
except Exception as e:
    print(e)
